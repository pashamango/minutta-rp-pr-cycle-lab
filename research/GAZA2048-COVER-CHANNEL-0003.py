#!/usr/bin/env python3
"""Synthetic cover-channel experiment; no printer/camera/Amazon claims."""
import argparse, hashlib, io, json, math, random, time, importlib.metadata
from pathlib import Path
import cv2, numpy as np, qrcode
from PIL import Image, ImageDraw

SEED = 920003
TRIALS = 100
LOCATOR_BITS = 48
GRID = 8

def locator(i):
    body = hashlib.sha256(f"GAZA2048-COVER:{i}".encode()).digest()[:6]
    return f"v1:{i:04x}:" + body.hex()

def qr_image(text, scale=5):
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=scale, border=4)
    q.add_data(text); q.make(fit=True)
    return np.asarray(q.make_image(fill_color="black", back_color="white").convert("RGB")), q.version

def cover(seed, size=720):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[:size, :size]
    a = (18*np.sin(x/31)+14*np.cos(y/47)+10*np.sin((x+y)/71))
    base = np.zeros((size,size,3), np.float32)
    base[:,:,0] = 105 + a + 12*np.sin(y/113)
    base[:,:,1] = 55 + .65*a + 18*np.cos(x/97)
    base[:,:,2] = 75 + .85*a + 15*np.sin((x-2*y)/131)
    base += rng.normal(0, 2.2, base.shape)
    im = Image.fromarray(np.uint8(np.clip(base,0,255)), "RGB")
    d=ImageDraw.Draw(im); d.rectangle((24,24,size-24,size-24), outline=(232,205,145), width=4)
    d.text((54,56), "THE HIDDEN GARDEN", fill=(240,220,170))
    d.text((56,93), "a synthetic cover study", fill=(205,175,145))
    return np.asarray(im)

def put_qr(c, q, integrated=False):
    out=c.copy(); h,w=c.shape[:2]; side=q.shape[0]*2; q=cv2.resize(q,(side,side),interpolation=cv2.INTER_NEAREST)
    x=w-side-55; y=h-side-55
    if integrated:
        # Preserve every module and quiet zone, but use a framed, palette-matched placement.
        q=np.where(q<128, np.array([30,18,38],np.uint8), np.array([239,220,172],np.uint8))
        out[y:y+side,x:x+side]=q
        cv2.rectangle(out,(x-10,y-10),(x+side+10,y+side+10),(181,143,92),3)
    else: out[y:y+side,x:x+side]=q
    return out

def chroma_embed(c, i, strength=7):
    out=c.astype(np.float32); h,w=c.shape[:2]
    digest=hashlib.sha256(f"GAZA2048-COVER:{i}".encode()).digest()[:6]
    bits=np.unpackbits(np.frombuffer(digest,np.uint8))
    # Low-amplitude blue-vs-red spread-spectrum blocks; no luminance modulation.
    for k,b in enumerate(bits):
        gy, gx=divmod(k, GRID); y0=gy*h//8; y1=(gy+1)*h//8; x0=gx*w//8; x1=(gx+1)*w//8
        pat=np.random.default_rng(7000+i*100+k).choice([-1.,1.], size=(y1-y0,x1-x0))
        sign=1 if b else -1
        out[y0:y1,x0:x1,2] += strength*sign*pat
        out[y0:y1,x0:x1,0] -= strength*sign*pat
    return np.uint8(np.clip(out,0,255))

def chroma_decode(im, i):
    h,w=im.shape[:2]; a=im.astype(float)
    signal=a[:,:,2]-a[:,:,0]; digest=hashlib.sha256(f"GAZA2048-COVER:{i}".encode()).digest()[:6]
    bits=np.unpackbits(np.frombuffer(digest,np.uint8)); scores=[]
    # The custom decoder knows the construction and trial index only for the synthetic oracle.
    for k in range(48):
        gy,gx=divmod(k,GRID); y0=gy*h//8; y1=(gy+1)*h//8; x0=gx*w//8; x1=(gx+1)*w//8
        pat=np.random.default_rng(7000+i*100+k).choice([-1.,1.], size=(y1-y0,x1-x0))
        scores.append(float(np.mean(signal[y0:y1,x0:x1]*pat)))
    got=np.array(scores)>0
    return bool(np.mean(got==bits) >= .98 and np.mean(np.abs(scores)) >= 0.9)

def damage(im, severity, rng, nr):
    h,w=im.shape[:2]; a=im.copy()
    scale=rng.uniform(.68,.92) if severity else 1
    if severity>=1:
        a=cv2.resize(a,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA); a=cv2.resize(a,(w,h),interpolation=cv2.INTER_LINEAR)
    if severity>=2:
        q=rng.randint(48,82); _,enc=cv2.imencode('.jpg',a,[cv2.IMWRITE_JPEG_QUALITY,q]); a=cv2.imdecode(enc,cv2.IMREAD_COLOR)
        ang=rng.uniform(-6,6); M=cv2.getRotationMatrix2D((w/2,h/2),ang,1); a=cv2.warpAffine(a,M,(w,h),borderValue=(110,60,75))
        a=np.uint8(np.clip(a.astype(float)+nr.normal(0,rng.uniform(2,10),a.shape),0,255))
    if severity>=3:
        d=rng.uniform(.01,.07)*min(h,w); src=np.float32([[0,0],[w,0],[w,h],[0,h]]); dst=src+nr.uniform(-d,d,(4,2)).astype('float32')
        a=cv2.warpPerspective(a,cv2.getPerspectiveTransform(src,dst),(w,h),borderValue=(110,60,75))
        side=rng.randint(int(.03*w),int(.13*w)); a[:side,:]=a[:, :side]=a[-side:,:]=a[:,-side:]=a[side,side]
    return a

def main(out, demo_dir):
    Path(demo_dir).mkdir(parents=True,exist_ok=True); rng=random.Random(SEED); nr=np.random.default_rng(SEED); det=cv2.QRCodeDetector(); rows=[]
    constructions=('standard','artwork','chroma','hybrid'); t0=time.perf_counter()
    for i in range(TRIALS):
        c=cover(500+i); q,ver=qr_image(locator(i)); imgs={'standard':put_qr(c,q),'artwork':put_qr(c,q,True),'chroma':chroma_embed(c,i),'hybrid':chroma_embed(put_qr(c,q,True),i)}
        if i==0:
            for name,img in imgs.items(): Image.fromarray(img).save(Path(demo_dir)/(name+'.png'))
        for name,img in imgs.items():
            for sev in range(4):
                d=damage(img,sev,rng,nr); gray=cv2.cvtColor(d,cv2.COLOR_RGB2GRAY); t=time.perf_counter()
                got=det.detectAndDecode(gray)[0]; qr_ok=got==locator(i); ch_ok=name in ('chroma','hybrid') and chroma_decode(d,i)
                ok=qr_ok if name in ('standard','artwork') else (ch_ok if name=='chroma' else (qr_ok or ch_ok))
                wrong=bool(got and got!=locator(i)); rows.append({'construction':name,'severity':sev,'trial':i,'ok':ok,'qr_exact':qr_ok,'chroma_exact':ch_ok,'wrong_qr':wrong,'decode_ms':(time.perf_counter()-t)*1000,'gray_ok':False})
                if sev==3 and i<TRIALS//4:
                    gd=cv2.cvtColor(d,cv2.COLOR_RGB2GRAY); gg=det.detectAndDecode(gd)[0]; rows[-1]['gray_ok']=gg==locator(i)
    summary=[]
    for name in constructions:
      for sev in range(4):
        z=[r for r in rows if r['construction']==name and r['severity']==sev]; summary.append({'construction':name,'severity':sev,'trials':len(z),'exact_recovery_rate':sum(r['ok'] for r in z)/len(z),'qr_recovery_rate':sum(r['qr_exact'] for r in z)/len(z),'chroma_recovery_rate':sum(r['chroma_exact'] for r in z)/len(z),'undetected_error_rate':sum(r['wrong_qr'] for r in z)/len(z),'median_decode_ms':round(float(np.median([r['decode_ms'] for r in z])),3)})
    clean={n:next(x for x in summary if x['construction']==n and x['severity']==0) for n in constructions}
    delta=imgs['chroma'].astype(float)-c.astype(float); hdelta=imgs['hybrid'].astype(float)-imgs['artwork'].astype(float)
    result={'seed':SEED,'trials_per_cell':TRIALS,'locator_bits':LOCATOR_BITS,'locator_format':'v1 + 16-bit trial + 48-bit SHA-256 truncation in a 19-character QR byte payload','library_versions':{'qrcode':importlib.metadata.version('qrcode'),'opencv':cv2.__version__,'numpy':np.__version__,'pillow':importlib.metadata.version('Pillow')},'qr_version':ver,'qr_modules':q.shape[0]//5,'ordinary_qr_compatible':{'standard':True,'artwork':True,'chroma':False,'hybrid':True},'visual_proxy':{'chroma_strength_rgb_delta':7,'chroma_changed_pixel_fraction':float(np.mean(np.any(delta!=0,axis=2))),'chroma_mean_abs_rgb_delta':round(float(np.mean(np.abs(delta))),3),'chroma_p95_abs_rgb_delta':round(float(np.percentile(np.abs(delta),95)),3),'hybrid_changed_pixel_fraction':float(np.mean(np.any(hdelta!=0,axis=2))),'hybrid_mean_abs_rgb_delta':round(float(np.mean(np.abs(hdelta))),3)},'clean_control':clean,'summary':summary,'gray_severity3_sample_rows':sum(r['gray_ok'] for r in rows if r['severity']==3 and r['trial']<25),'gray_sample_n':25,'elapsed_s':round(time.perf_counter()-t0,2)}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--out',default='research/GAZA2048-COVER-CHANNEL-0003-results.json'); p.add_argument('--demo-dir',default='research/GAZA2048-COVER-CHANNEL-0003-demo'); a=p.parse_args(); main(a.out,a.demo_dir)
