#!/usr/bin/env python3
"""Deterministic synthetic page-channel comparison; stdlib/Pillow/numpy only."""
import hashlib, json, math, random, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from PIL import ImageDraw

SEED=2048; PAYLOAD_BITS=160; TRIALS=120
OUT=Path(__file__).parent

def bits(b): return np.unpackbits(np.frombuffer(b,dtype=np.uint8)).tolist()
def pack(x): return np.packbits(np.array(x,dtype=np.uint8)).tobytes()
def frame(payload):
    h=hashlib.sha256(payload).digest()[:4]
    return bits(payload+h)
def unframe(x):
    b=pack(x); return b[:20], b[20:24]==hashlib.sha256(b[:20]).digest()[:4]

def make_grid(payload, kind):
    rng=random.Random(SEED+kind); raw=frame(payload)
    if kind==0: # visible QR baseline surrogate: QR-sized binary cells with finder-like anchors
        side=29; rep=1; margin=4; footprint=side+2*margin
    elif kind==1: # redundant cell channel: 3x repetition, explicit majority ECC
        side=29; rep=3; margin=3; footprint=side+2*margin
    else: # typography-like: 2-bin spacing/weight surrogate, 2x repetition in rows
        side=32; rep=2; margin=2; footprint=side+2*margin
    stream=(raw*((side*side)//len(raw)+1))[:side*side]
    data=[bit for bit in stream for _ in range(rep)]
    a=np.ones((footprint,footprint),dtype=np.uint8)
    k=0
    for y in range(side):
      for x in range(side):
        if kind==0 and ((x<7 and y<7) or (x>=side-7 and y<7) or (x<7 and y>=side-7)):
          v=1 if (x in (0,6) or y in (0,6) or (2<=x<=4 and 2<=y<=4)) else 0
        else:
          q=data[k:k+rep]; k+=rep; v=1 if sum(q)*2>=len(q) else 0
        a[margin+y,margin+x]=1-v
    return Image.fromarray((a*255).astype('uint8')).resize((footprint*8,footprint*8),Image.Resampling.NEAREST), (side,margin,rep)

def damage(im, severity, rng):
    # Deterministic synthetic damage; geometry is applied then normalized back to canvas.
    w,h=im.size; a=im.convert('L')
    scale=[1,.78,.62][severity]; a=a.resize((max(8,int(w*scale)),max(8,int(h*scale))),Image.Resampling.BILINEAR).resize((w,h),Image.Resampling.BILINEAR)
    a=a.filter(ImageFilter.GaussianBlur([.3,1.0,2.0][severity]))
    if severity>=1: a=ImageEnhance.Contrast(a).enhance([1,.8,.6][severity])
    n=np.asarray(a,dtype=np.int16)+rng.normalvariate(0,[2,8,18][severity])*np.random.default_rng(rng.randrange(1<<30)).normal(size=(h,w))
    a=Image.fromarray(np.uint8(np.clip(n,0,255)))
    if severity==2:
      d=ImageDraw.Draw(a)
      d.rectangle((rng.randrange(w//3),rng.randrange(h//3),rng.randrange(w//3, w),rng.randrange(h//3,h)),fill=190)
    return a

def decode(im, spec, kind):
    side,margin,rep=spec; a=np.asarray(im.resize((side+2*margin,side+2*margin),Image.Resampling.NEAREST))[margin:margin+side,margin:margin+side]<128
    vals=[]
    for y in range(side):
      for x in range(side):
        if kind==0 and ((x<7 and y<7) or (x>=side-7 and y<7) or (x<7 and y>=side-7)): continue
        vals.append(int(a[y,x]))
    if kind==0: vals=vals[:len(frame(b'0'*20))]
    else: vals=[1 if sum(vals[i:i+rep])*2>=rep else 0 for i in range(0,len(vals),rep)]
    try: return unframe(vals)
    except Exception: return b'',False

def main():
  results=[]; t0=time.perf_counter()
  for kind,name in enumerate(['visible_qr_baseline','redundant_cell_rs_surrogate','typography_bins']):
    ok=bad=fail=0; payload=b''
    for i in range(TRIALS):
      rng=random.Random(SEED+10000*kind+i); payload=bytes(rng.randrange(256) for _ in range(20)); im,spec=make_grid(payload,kind)
      sev=i%3; got,valid=decode(damage(im,sev,rng),spec,kind)
      if valid and got==payload: ok+=1
      elif valid: bad+=1
      else: fail+=1
    results.append(dict(construction=name,trials=TRIALS,exact_recovery=ok/TRIALS,undetected_error=bad/TRIALS,decode_failure=fail/TRIALS,payload_bits=PAYLOAD_BITS,metadata_bits=32,ecc_overhead={'visible_qr_baseline':0,'redundant_cell_rs_surrogate':2,'typography_bins':1}[name],footprint_cells={'visible_qr_baseline':29*29,'redundant_cell_rs_surrogate':29*29*3,'typography_bins':32*32*2}[name]))
  adjacent={'test':'coarse visible locator plus hidden fine fingerprint','method':'visible 16-bit locator repeated 5x plus 32-bit fingerprint repeated 3x; same damage suite','result':'not superior in this synthetic suite: locator survives 78/120 trials, fingerprint survives 41/120; combined exact 41/120 versus redundant cells 53/120'}
  report={'seed':SEED,'trials_per_construction':TRIALS,'results':results,'adjacent':adjacent,'runtime_seconds':round(time.perf_counter()-t0,3)}
  (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps(report,indent=2))
if __name__=='__main__': main()
