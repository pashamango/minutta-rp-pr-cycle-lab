#!/usr/bin/env python3
"""Deterministic QR locator robustness experiment (synthetic only)."""
import argparse, base64, hashlib, io, json, math, random, time, importlib.metadata
from pathlib import Path
import cv2, numpy as np, qrcode
from PIL import Image

SEED=2048002
TRIALS=100
def payload(bits, i):
    raw=hashlib.sha256(f"GAZA2048:{bits}:{i}".encode()).digest()[:math.ceil(bits/8)]
    return f"v1:{bits}:{i}:"+base64.b32encode(raw).decode().rstrip("=")
def render(s, ecc=qrcode.constants.ERROR_CORRECT_M):
    q=qrcode.QRCode(version=None,error_correction=ecc,box_size=8,border=4)
    q.add_data(s); q.make(fit=True)
    return np.array(q.make_image(fill_color="black",back_color="white").convert("L")), q.version
def damage(im, severity, rng, np_rng):
    a=im.copy(); h,w=a.shape
    if severity>=1:
        scale=rng.uniform(.65,.9); a=cv2.resize(a,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
        a=cv2.resize(a,(w,h),interpolation=cv2.INTER_LINEAR)
        a=cv2.GaussianBlur(a,(0,0),rng.uniform(.3,1.0))
    if severity>=2:
        q=rng.randint(45,85); ok,enc=cv2.imencode('.jpg',a,[cv2.IMWRITE_JPEG_QUALITY,q]); a=cv2.imdecode(enc,cv2.IMREAD_GRAYSCALE)
        ang=rng.uniform(-7,7); M=cv2.getRotationMatrix2D((w/2,h/2),ang,1); a=cv2.warpAffine(a,M,(w,h),borderValue=255)
        noise=np_rng.normal(0,rng.uniform(4,14),a.shape); a=np.clip(a.astype(float)+noise,0,255).astype('uint8')
    if severity>=3:
        # perspective and margin loss
        d=rng.uniform(.02,.08)*min(h,w); src=np.float32([[0,0],[w,0],[w,h],[0,h]])
        dst=src+np_rng.uniform(-d,d,(4,2)).astype('float32'); a=cv2.warpPerspective(a,cv2.getPerspectiveTransform(src,dst),(w,h),borderValue=255)
        side=rng.randint(int(.04*w),int(.16*w)); a[:side,:]=255; a[:, :side]=255
        oh,ow=int(h*rng.uniform(.08,.22)),int(w*rng.uniform(.08,.22)); y=rng.randint(h//5, max(h//5+1,4*h//5-oh)); x=rng.randint(w//5,max(w//5+1,4*w//5-ow)); a[y:y+oh,x:x+ow]=255
    return a
def main(out):
    det=cv2.QRCodeDetector(); rows=[]; t0=time.perf_counter(); rng=random.Random(SEED); np_rng=np.random.default_rng(SEED)
    for bits in (40,160):
      clean,ver=render(payload(bits,0));
      clean_ok=det.detectAndDecode(clean)[0]==payload(bits,0)
      for sev in range(4):
       counts={'ok':0,'wrong':0,'fail':0}; lat=[]
       for i in range(TRIALS):
        s=payload(bits,i); img,_=render(s); d=damage(img,sev,rng,np_rng); st=time.perf_counter(); got,_,_=det.detectAndDecode(d); lat.append((time.perf_counter()-st)*1000)
        counts['ok' if got==s else ('wrong' if got else 'fail')]+=1
       rows.append({'bits':bits,'severity':sev,'version':ver,'modules':clean.shape[0]//8,'payload_chars':len(payload(bits,0)),'clean_control':clean_ok,'trials':TRIALS,**counts,'recovery_rate':counts['ok']/TRIALS,'undetected_error_rate':counts['wrong']/TRIALS,'median_decode_ms':round(float(np.median(lat)),3)})
    # collision broker: truncated SHA-256 prefix, deterministic corpus
    coll={}; collision_counts={}
    for n in (1000,10000,100000):
      for b in (32,40,48):
       seen=set(); c=0
       for i in range(n):
        x=hashlib.sha256(f"corpus:{i}".encode()).digest(); k=int.from_bytes(x[:6],'big')>>(48-b)
        if k in seen:c+=1
        seen.add(k)
       collision_counts[f"{n}:{b}"]=c
    result={'seed':SEED,'trials_per_cell':TRIALS,'library_versions':{'qrcode':importlib.metadata.version('qrcode'),'opencv':cv2.__version__,'numpy':np.__version__},'rows':rows,'collision_experiment':collision_counts,'elapsed_s':round(time.perf_counter()-t0,2)}
    Path(out).write_text(json.dumps(result,indent=2)+"\n")
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--out',default='research/GAZA2048-LOCATOR-0002-results.json'); main(p.parse_args().out)
