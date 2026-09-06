"""Render the three ZYCLOPS cutout animation rigs, then encode Telegram WEBM.
Requires Python 3, Pillow, NumPy, SciPy and ffmpeg/ffprobe.
Set ZYCLOPS_STICKER_FONT to a bold display font on non-macOS systems.
Source artwork is preserved. Frames are composed in premultiplied alpha.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from scipy.ndimage import map_coordinates, label
import math, subprocess, json, tempfile, os, shutil, zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/animated'
OUT.mkdir(parents=True, exist_ok=True)
FPS, FRAMES, SIZE = 24, 72, 512
Y, X = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
FONT_PATH = os.environ.get('ZYCLOPS_STICKER_FONT', '/System/Library/Fonts/Supplemental/Impact.ttf')
FONT = ImageFont.truetype(FONT_PATH, 53)
GOLD = (245, 198, 59, 255)

def smooth(a, b, x):
    t = np.clip((x-a)/(b-a), 0, 1)
    return t*t*(3-2*t)

def source(name):
    if name == 'pump':
        im = Image.open(OUT / 'pump-source.png').convert('RGBA')
        # Discard disconnected matte speckles before fitting the cutout to its rig.
        rgba = np.array(im)
        groups, n = label(rgba[:,:,3] > 12)
        sizes = np.bincount(groups.ravel()); sizes[0] = 0
        keep = groups == int(sizes.argmax())
        rgba[:,:,3] = np.where(keep, rgba[:,:,3], 0)
        im = Image.fromarray(rgba)
        im = im.crop(im.getbbox())
        im.thumbnail((478, 452), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (SIZE, SIZE))
        canvas.alpha_composite(im, ((SIZE-im.width)//2, 22))
        return canvas
    return Image.open(ROOT / 'assets/stickers' / {'gm':'02-gm.png', 'fine':'07-fine.png'}[name]).convert('RGBA')

def warp(im, sx, sy):
    a = np.asarray(im).astype(np.float32)/255
    a[:,:,:3] *= a[:,:,3:4]
    mapped = np.stack([map_coordinates(a[:,:,c], [sy, sx], order=1, mode='constant', cval=0, prefilter=False) for c in range(4)], axis=2)
    np.divide(mapped[:,:,:3], np.maximum(mapped[:,:,3:4], 1/255), out=mapped[:,:,:3])
    return Image.fromarray(np.uint8(np.clip(mapped,0,1)*255+.5))

def wave_rig(im, phase):
    t = phase*2*math.pi
    angle = .115*math.sin(t*3)*math.sin(t/2)**2
    mask = (1-smooth(184, 237, X))*(1-smooth(355, 430, Y))
    dx, dy = X-133, Y-365
    sx = X + mask*((math.cos(angle)-1)*dx + math.sin(angle)*dy)
    sy = Y + mask*(-math.sin(angle)*dx + (math.cos(angle)-1)*dy)
    return warp(im, sx, sy)

def pump_rig(im, phase):
    t = phase*math.pi*2
    beat = (1-math.cos(t*2))/2
    # Both fists rise independently of the face, then settle into the loop.
    hands = smooth(80,155,np.abs(X-256)) * (1-smooth(420,490,Y))
    sy = Y + hands*(10*beat) + 2.5*math.sin(t*2)
    sx = X + np.sign(X-256)*hands*2.3*math.sin(t*2)
    # Small radial eye pulse, localized so the brow and face retain their shape.
    eye = np.exp(-((X-256)/59)**4-((Y-149)/39)**4)
    sx -= (X-256)*eye*.075*beat
    sy -= (Y-149)*eye*.075*beat
    frame = warp(im, sx, sy)
    sparkle = Image.new('RGBA', im.size)
    d = ImageDraw.Draw(sparkle)
    for cx,cy,p in [(57,83,0), (446,87,.34),(405,35,.67)]:
        pulse = max(0, math.sin(t*2+p*2*math.pi))**3
        r=3+6*pulse
        d.polygon([(cx,cy-r),(cx+2,cy-2),(cx+r,cy),(cx+2,cy+2),(cx,cy+r),(cx-2,cy+2),(cx-r,cy),(cx-2,cy-2)], fill=(250,209,82,int(220*pulse)))
    frame.alpha_composite(sparkle)
    return frame

def fine_rig(im, phase):
    t=phase*math.pi*2
    dx=np.zeros_like(X); dy=np.zeros_like(Y)
    for i,(cx,cy,rx,ry) in enumerate([(107,238,28,77),(400,241,28,76),(64,356,18,40),(441,358,18,42),(122,392,20,32),(209,413,17,25),(387,391,23,36),(320,326,16,26)]):
        mask=np.exp(-((X-cx)/rx)**4-((Y-cy)/ry)**4)
        dx+=mask*3.2*math.sin(t*3+i*1.2)
        dy+=mask*3.7*math.sin(t*2+i*.75)
    frame=warp(im,X+dx,Y+dy)
    steam=Image.new('RGBA',im.size)
    d=ImageDraw.Draw(steam)
    # Two strands of steam drift continuously above the same stationary cup.
    for j in range(2):
        for k in range(40):
            h=k/40
            h2=(k+1)/40
            def point(q):
                return (251+j*7+5*math.sin(q*7-t+j), 310-49*q)
            alpha=int(58*math.sin(math.pi*h)*(0.7+0.3*math.sin(t+j)))
            d.line([point(h),point(h2)],fill=(252,235,185,alpha),width=2)
    frame.alpha_composite(steam.filter(ImageFilter.GaussianBlur(.6)))
    return frame

def caption(frame, name, phase):
    canvas=Image.new('RGBA',(SIZE,SIZE))
    frame=frame.resize((461,461),Image.Resampling.LANCZOS)
    canvas.alpha_composite(frame,(25,22 if name=='gm' else 34 if name=='pump' else 0))
    text={'gm':'GM','pump':'PUMP','fine':'THIS IS FINE'}[name]
    y=473 - (2*math.sin(phase*4*math.pi) if name=='pump' else 0)
    d=ImageDraw.Draw(canvas)
    # Rounded white cut line, black keyline, gold lettering readable in any chat.
    d.text((256,y),text,font=FONT,anchor='mm',fill=GOLD,stroke_width=7,stroke_fill=(250,249,245,255))
    d.text((256,y),text,font=FONT,anchor='mm',fill=GOLD,stroke_width=2,stroke_fill=(21,20,15,255))
    return canvas

def encode(frames_dir, dest, crf, preview=False):
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(frames_dir/'%03d.png')]
    if preview:
        cmd+=['-filter_complex','color=c=0x111310:s=512x512:r=24[bg];[bg][0:v]overlay=shortest=1:format=auto,format=yuv420p[v]','-map','[v]']
    cmd+=['-c:v','libvpx-vp9','-pix_fmt','yuv420p' if preview else 'yuva420p','-b:v','0','-crf',str(crf),'-deadline','good','-cpu-used','3','-row-mt','1','-threads','4','-an','-t','3',str(dest)]
    subprocess.run(cmd,check=True)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))

report={}
with tempfile.TemporaryDirectory(prefix='zyclops-frames-') as temp:
    tmp=Path(temp)
    for name, rig in [('gm',wave_rig),('pump',pump_rig),('fine',fine_rig)]:
        print('Rendering',name,flush=True)
        src=source(name); seq=tmp/name; seq.mkdir()
        review_frames=[]
        for i in range(FRAMES):
            frame=caption(rig(src,i/FRAMES),name,i/FRAMES)
            frame.save(seq/f'{i:03}.png',compress_level=1)
            if i==0:
                frame.save(OUT/f'{name}.webp',quality=88,method=6)
            if i in [6,18,30,42,54,66]: review_frames.append(frame)
        # A review filmstrip also makes the independent rigs easy to inspect.
        sheet=Image.new('RGB',(512*3,512*2),'#111310')
        for i,fr in enumerate(review_frames): sheet.paste(fr,((i%3)*512,(i//3)*512),fr)
        sheet.save(tmp/f'{name}-frames.jpg',quality=88)
        target=OUT/f'{name}.webm'
        for crf in [34,38,42,46,50]:
            encode(seq,target,crf)
            if target.stat().st_size<=256000: break
        if target.stat().st_size>256000: raise RuntimeError(f'{name} exceeds Telegram size limit')
        encode(seq,OUT/f'{name}-preview.webm',30,True)
        metadata=probe(target)
        video=metadata['streams'][0]
        assert len(metadata['streams'])==1 and video['codec_name']=='vp9'
        assert video['width']==512 and video['height']==512
        assert float(metadata['format']['duration'])<=3
        assert video.get('tags',{}).get('alpha_mode')=='1'
        decoded=subprocess.check_output(['ffmpeg','-v','error','-c:v','libvpx-vp9','-i',str(target),'-frames:v','1','-f','rawvideo','-pix_fmt','rgba','-'])
        alpha=np.frombuffer(decoded,dtype=np.uint8).reshape(512,512,4)[:,:,3]
        assert alpha.min()==0 and alpha.max()==255
        report[name]={'bytes':target.stat().st_size,'duration':metadata['format']['duration'],'fps':video['r_frame_rate'],'codec':video['codec_name'],'alpha_verified':True,'width':512,'height':512,'crf':crf}
        print(name,report[name],flush=True)
    review=ROOT.parent/'zyclops-motion-review'
    review.mkdir(exist_ok=True)
    for file in tmp.glob('*-frames.jpg'): shutil.copy2(file,review/file.name)
    (review/'exports.json').write_text(json.dumps(report,indent=2))
print('All three video stickers validated.',flush=True)
with zipfile.ZipFile(ROOT / 'assets/zyclops-animated-stickers.zip','w',zipfile.ZIP_DEFLATED) as pack:
    for file in ['gm.webm','pump.webm','fine.webm','README.txt']:
        pack.write(OUT/file,file)
