"""Prepare delivery formats and illustrated video loops from generated source art.

No image API is called here. New artwork is generated with the built-in image
tool; this script converts formats, renders video frames, and packages metadata.
Requires Pillow, NumPy, SciPy, ffmpeg, and ffprobe.
"""
from pathlib import Path
import argparse, csv, hashlib, json, math, os, subprocess, zipfile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageChops, ImageFont
import numpy as np
from scipy.ndimage import map_coordinates

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / 'media-vault').exists() else HERE.parent
VAULT = ROOT / 'media-vault'
BASE = 'https://zyclops.xyz/media-vault/'
FPS, SIZE, FRAMES = 30, 720, 180
FFMPEG = 'ffmpeg'
FFPROBE = 'ffprobe'
FONT = os.environ.get('ZYCLOPS_STICKER_FONT', '/System/Library/Fonts/Supplemental/Impact.ttf')
THEMES = json.loads((VAULT / 'meta/prompts-v2.json').read_text())
BY_ID = {t['id']: t for t in THEMES}

def run(args):
    result=subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if result.returncode: raise RuntimeError(result.stderr.decode()[-2000:])

def probe(path):
    return json.loads(subprocess.check_output([FFPROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))

def encode_options(path):
    return ['-c:v','libx264','-preset','medium','-crf','19','-profile:v','high','-pix_fmt','yuv420p','-r','30','-an','-movflags','+faststart',str(path)]

def prepare_images(sources):
    for t in THEMES:
        if t['id'] not in sources: continue
        target = VAULT / 'images' / f"zyclops-{t['id']}-v1.jpg"
        if not target.exists():
            with Image.open(sources[t['id']]) as im:
                assert im.width == im.height, f"Expected square artwork: {t['id']}"
                im.convert('RGB').resize((1200,1200),Image.Resampling.LANCZOS).save(target,quality=94,subsampling=0,optimize=True)
        thumb = VAULT / 'thumbs' / target.name
        if not thumb.exists():
            with Image.open(target) as im:
                im.resize((480,480),Image.Resampling.LANCZOS).save(thumb,quality=85,optimize=True)

def image_path(theme):
    versioned = VAULT / 'images' / f'zyclops-{theme}-v1.jpg'
    return versioned if versioned.exists() else VAULT / 'images' / f'{theme}.jpg'

def poster_video(theme, path):
    image = image_path(theme)
    effect = "scale=2160:2160,zoompan=z='1.005+0.015*(1-cos(2*PI*on/180))/2':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=180:s=720x720:fps=30,scale=in_range=pc:out_range=tv,format=yuv420p,setparams=range=limited"
    run([FFMPEG,'-v','error','-y','-i',str(image),'-vf',effect,'-frames:v',str(FRAMES),*encode_options(path)])

Y,X = np.mgrid[0:SIZE,0:SIZE].astype(np.float32)
S = SIZE / 1254
def mask(cx,cy,rx,ry):
    return np.exp(-((X-cx*S)/(rx*S))**4-((Y-cy*S)/(ry*S))**4)

def warped(source, dx, dy):
    return Image.fromarray(np.stack([map_coordinates(source[:,:,c],[Y+dy,X+dx],order=1,mode='nearest',prefilter=False) for c in range(3)],axis=2).astype(np.uint8))

def draw_sparks(frame, phase, regions):
    layer = Image.new('RGBA',(SIZE,SIZE))
    draw = ImageDraw.Draw(layer)
    for i,(cx,cy) in enumerate(regions):
        p = (phase + i*.137) % 1
        alpha = int(155 * math.sin(math.pi*p)**2)
        px = (cx+6*math.sin(p*math.pi*2+i))*S
        py = (cy-74*p)*S
        radius = 1.1 if i%2 else 1.6
        draw.ellipse((px-radius,py-radius,px+radius,py+radius),fill=(246,203,85,alpha))
    return Image.alpha_composite(frame.convert('RGBA'),layer).convert('RGB')

def cine_frame(name, source, phase):
    angle = phase*math.pi*2
    dx,dy = np.zeros_like(X),np.zeros_like(Y)
    if name == 'gm-steam':
        steam = mask(625,764,47,101)
        dx += steam*5.5*S*np.sin(Y/(24*S)+angle*2)
        dy += steam*2*S*math.sin(angle*2)
    elif name == 'pump-action':
        arms = mask(496,646,222,90)
        stroke = (1-math.cos(angle*3))/2
        dy -= arms*20*S*stroke
        dx += arms*1.5*S*math.sin(angle*3)
        puff = mask(715,813,83,109)
        dx += puff*3.8*S*math.sin(angle*3)
        dy += puff*2.7*S*math.cos(angle*3)
    elif name == 'fine-fire':
        for i,(cx,cy,rx,ry) in enumerate([(103,636,93,253),(1144,666,86,225),(960,479,156,172)]):
            flame=mask(cx,cy,rx,ry)
            dx += flame*4.5*S*np.sin(Y/(28*S)+angle*3+i)
            dy += flame*8*S*math.sin(angle*2+i)
    elif name == 'lurking-blink':
        curtain=mask(895,637,164,356)
        dx += curtain*3.5*S*math.sin(angle)
    frame=warped(source,dx,dy)
    if name == 'lurking-blink':
        # The eye rim stays intact; a clipped charcoal lid crosses the aperture.
        blink=0
        for center in (.28,.77):
            distance=abs(phase-center)
            if distance < .034: blink=max(blink,(1+math.cos(math.pi*distance/.034))/2)
        if blink:
            aperture=Image.new('L',(SIZE,SIZE)); ad=ImageDraw.Draw(aperture)
            ad.ellipse(tuple(v*S for v in (478,449,679,585)),fill=255)
            lid=Image.new('RGBA',(SIZE,SIZE)); ld=ImageDraw.Draw(lid)
            upper=(449+73*blink)*S
            lower=(585-62*blink)*S
            ld.rectangle((475*S,445*S,682*S,upper),fill=(37,36,30,255))
            ld.rectangle((475*S,lower,682*S,589*S),fill=(37,36,30,255))
            if blink > .85:
                ld.arc(tuple(v*S for v in (482,498,677,541)),0,180,fill=(173,132,52,int(255*(blink-.85)/.15)),width=2)
            lid.putalpha(ImageChops.multiply(lid.getchannel('A'),aperture))
            frame=Image.alpha_composite(frame.convert('RGBA'),lid).convert('RGB')
    if name == 'fine-fire':
        frame=draw_sparks(frame,phase,[(69,655),(139,792),(194,459),(1053,538),(1123,821),(1159,552),(982,696)])
    return frame

def cine_video(name, theme, path):
    source=np.asarray(Image.open(image_path(theme)).convert('RGB').resize((SIZE,SIZE),Image.Resampling.LANCZOS))
    process=subprocess.Popen([FFMPEG,'-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{SIZE}x{SIZE}','-framerate',str(FPS),'-i','pipe:0',*encode_options(path)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for index in range(FRAMES): process.stdin.write(cine_frame(name,source,index/FRAMES).tobytes())
        process.stdin.close()
        error=process.stderr.read().decode()
        if process.wait(): raise RuntimeError(error)
    except BaseException:
        process.kill(); process.wait(); raise

def character_video(source_name, source_root, path):
    source=source_root/'assets/animated'/f'{source_name}-preview.webm'
    decoder=subprocess.Popen([FFMPEG,'-v','error','-stream_loop','1','-i',str(source),'-vf','scale=620:620,fps=30','-t','6','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    encoder=subprocess.Popen([FFMPEG,'-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','720x720','-framerate','30','-i','pipe:0',*encode_options(path)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    font=ImageFont.truetype(FONT,21)
    try:
        for i in range(FRAMES):
            chunk=decoder.stdout.read(620*620*3)
            if len(chunk)!=620*620*3: raise RuntimeError('Incomplete sticker decode')
            canvas=Image.new('RGB',(720,720),(17,19,16))
            canvas.paste(Image.frombytes('RGB',(620,620),chunk),(50,18))
            ImageDraw.Draw(canvas).text((360,670),'ZYCLOPS · $ZYCL',font=font,fill=(237,196,73),anchor='mt')
            encoder.stdin.write(canvas.tobytes())
        encoder.stdin.close()
        error=encoder.stderr.read().decode()
        if encoder.wait(): raise RuntimeError(error)
        if decoder.wait(): raise RuntimeError(decoder.stderr.read().decode())
    except BaseException:
        decoder.kill();encoder.kill();decoder.wait();encoder.wait();raise

VIDEOS = [
    ('gm-steam','gm','cinemagraph','GM · first brew'),
    ('pump-action','pump','cinemagraph','PUMP · manual labour'),
    ('lurking-blink','lurking','cinemagraph','LURKING · blink and you miss him'),
    ('fine-fire','this-is-fine','cinemagraph','This is fine · still warm'),
    ('night-watch-motion','night-watch','motion_poster','Night watch · moving poster'),
    ('sentinel-motion','golden-sentinel','motion_poster','Golden sentinel · moving poster'),
    ('moonwalk-motion','moonwalk','motion_poster','Moonwalk · moving poster'),
    ('rain-motion','rainy-alley','motion_poster','After the rain · moving poster'),
    ('gm-wave','gm','character_loop','GM · wave'),
    ('pump-fists','pump','character_loop','PUMP · fists up'),
    ('fine-coffee','this-is-fine','character_loop','This is fine · coffee break'),
]

def render_video(spec, source_root):
    ident,theme,kind,title=spec
    path=VAULT/'video'/f'zyclops-{ident}-v1.mp4'
    if path.exists() and path.stat().st_size < 1000: path.unlink()
    if not path.exists():
        if kind=='motion_poster': poster_video(theme,path)
        elif kind=='cinemagraph': cine_video(ident,theme,path)
        else: character_video({'gm-wave':'gm','pump-fists':'pump','fine-coffee':'fine'}[ident],source_root,path)
    poster=VAULT/'thumbs'/f'zyclops-{ident}-v1.jpg'
    if not poster.exists(): run([FFMPEG,'-v','error','-y','-ss','0.5','-i',str(path),'-frames:v','1','-vf','scale=480:480','-q:v','2',str(poster)])
    if kind != 'motion_poster':
        gif=VAULT/'gif'/f'zyclops-{ident}-v1.gif'
        if not gif.exists():
            effect='fps=12,scale=480:480:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4'
            run([FFMPEG,'-v','error','-y','-i',str(path),'-filter_complex',effect,'-loop','0',str(gif)])
    print('Rendered',ident,flush=True)

def common(t, path, ident, media_type, thumb):
    file=VAULT/path
    return {'id':f'zyclops-{ident}-v1','creative_id':f'zyclops-{t["id"]}-v1','title':t['title'],'theme':t['id'],'collection':t.get('kind','meme'),'media_type':media_type,'path':path,'url':BASE+path,'mime_type':'image/jpeg' if media_type=='image' else 'video/mp4','width':1200 if media_type=='image' else 720,'height':1200 if media_type=='image' else 720,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'thumbnail_path':thumb,'thumbnail_url':BASE+thumb,'captions':[t['caption'],t['caption']+'\n\n$ZYCL'],'alt_text':t['alt'],'tags':t['tags'],'suggested_context':'Holder artwork to share with your own caption.' if t.get('kind')=='artwork' else 'Evergreen fictional reaction meme; not a report of market conditions.','suggested_cooldown_hours':72}

STILL_ADDITIONS = {'based','touch-grass','wen-moon','wagmi','ngmi','ser','night-watch','the-blind-spot','golden-sentinel','moonwalk','rainy-alley','the-forge','campfire','redacted-world'}
VIDEO_ADDITIONS = [v for v in VIDEOS if v[0] != 'hodl-motion']

def gif_alternate(ident):
    relative=f'gif/zyclops-{ident}-v1.gif'; file=VAULT/relative
    if not file.exists(): return []
    with Image.open(file) as im:
        assert im.n_frames<=350 and im.size==(480,480),relative
    assert file.stat().st_size<=5_000_000,relative
    return [{'format':'gif','mime_type':'image/gif','path':relative,'url':BASE+relative,'width':480,'height':480,'fps':12,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}]

def package():
    legacy=json.loads((VAULT/'meta/legacy-manifest-v1.json').read_text())
    old_assets=legacy['assets']
    for a in old_assets:
        assert hashlib.sha256((VAULT/a['path']).read_bytes()).hexdigest()==a['sha256'], a['id']
        a.update(collection='meme',release=1,topic=a['creative_id'])
        if a['media_type']=='video':
            poster=f"thumbs/{a['id']}-poster-v2.jpg"
            if not (VAULT/poster).exists(): run([FFMPEG,'-v','error','-y','-ss','0.5','-i',str(VAULT/a['path']),'-frames:v','1','-vf','scale=480:480','-q:v','2',str(VAULT/poster)])
            a.update(thumbnail_path=poster,thumbnail_url=BASE+poster,poster_path=poster,poster_url=BASE+poster,has_audio=False,fps=30)
    legacy_loop_alt={
        'gm-loop':'An animated black-and-gold ZYCLOPS sticker waves hello above the letters GM.',
        'pump-loop':'An animated ZYCLOPS sticker raises his fists with a glowing golden eye and sparkles.',
        'this-is-fine-loop':'An animated ZYCLOPS sticker calmly drinks coffee while cartoon flames flicker.'}
    for a in old_assets:
        if a['id'] in legacy_loop_alt:a['alt_text']=legacy_loop_alt[a['id']]
    additions=[]
    for t in THEMES:
        if t['id'] not in STILL_ADDITIONS:continue
        path=f"images/zyclops-{t['id']}-v1.jpg"; thumb=f"thumbs/zyclops-{t['id']}-v1.jpg"
        a=common(t,path,t['id'],'image',thumb)
        a.update(creative_id=t['id'],topic=t['id'],theme=t.get('kind','meme'),release=2)
        if t.get('kind')!='artwork':a['title']+=' · alternate artwork'
        assert a['bytes']<=5_000_000,path
        additions.append(a)
    for ident,theme,kind,title in VIDEO_ADDITIONS:
        path=f'video/zyclops-{ident}-v1.mp4'; thumb=f'thumbs/zyclops-{ident}-v1.jpg'
        a=common(BY_ID[theme],path,ident,'video',thumb)
        a.update(title=title,creative_id=theme,topic=theme,theme=BY_ID[theme].get('kind','meme'),release=2,duration_seconds=6,fps=30,animation_type=kind,poster_path=thumb,poster_url=BASE+thumb,has_audio=False)
        if kind=='cinemagraph':a['alt_text']='Illustrated loop: '+a['alt_text']
        elif kind=='motion_poster':a['alt_text']='Gentle looping camera movement across '+a['alt_text']
        else:a['alt_text']={
            'gm-wave':'A black-and-gold ZYCLOPS sticker waves hello above GM, with a ZYCLOPS footer.',
            'pump-fists':'ZYCLOPS raises his fists as his golden eye and sparkles pulse, with a ZYCLOPS footer.',
            'fine-coffee':'ZYCLOPS calmly drinks coffee while flames flicker and steam rises, with a ZYCLOPS footer.'}[ident]
        alternates=gif_alternate(ident)
        if alternates:a['alternates']=alternates
        additions.append(a)
    assets=additions+old_assets
    assert len({a['id'] for a in assets})==len(assets)
    for a in assets:
        if a['media_type']=='video':
            info=probe(VAULT/a['path']); stream=next(s for s in info['streams'] if s['codec_type']=='video')
            assert stream['codec_name']=='h264' and stream['pix_fmt'] in ('yuv420p','yuvj420p'),a['id']
            if a['release']==2:assert stream['pix_fmt']=='yuv420p',a['id']
            assert (stream['width'],stream['height'])==(720,720),a['id']
            assert stream['r_frame_rate']=='30/1',a['id']
            duration=float(info['format']['duration'])
            assert 2.9<=duration<=6.05,a['id']
            if a['release']==2:assert abs(duration-6)<.05,a['id']
            a.update(duration_seconds=round(duration,3),pixel_format=stream['pix_fmt'])
        else:
            with Image.open(VAULT/a['path']) as im:assert im.size==(1200,1200),a['id']
        assert (VAULT/a['thumbnail_path']).exists(),a['id']
    manifest={**legacy,'library_version':'2026-09-06.2','brand':'ZYCLOPS','ticker':'$ZYCL','base_url':BASE,'access':'Unlisted, publicly accessible by URL; not authenticated.','counts':{'images':sum(a['media_type']=='image' for a in assets),'videos':sum(a['media_type']=='video' for a in assets),'gif_alternates':sum(len(a.get('alternates',[])) for a in assets)},'assets':assets}
    (VAULT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    fields=['id','creative_id','title','collection','release','media_type','url','mime_type','width','height','bytes','duration_seconds','animation_type','caption','alt_text','tags']
    with (VAULT/'catalog.csv').open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader()
        for a in assets:
            row={k:a.get(k,'') for k in fields};row.update(caption=a['captions'][0],tags='|'.join(a['tags']));writer.writerow(row)
    include={'index.html','vault.css','vault.js','manifest.json','catalog.csv','BOT-README.md'}
    include.update(str(p.relative_to(VAULT)) for p in (VAULT/'meta').glob('*') if p.is_file())
    for a in assets:
        include.update([a['path'],a['thumbnail_path']])
        if a.get('poster_path'):include.add(a['poster_path'])
        include.update(v['path'] for v in a.get('alternates',[]))
    bundle=VAULT/'zyclops-media-pack-v2.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for relative in sorted(include):archive.write(VAULT/relative,'media-vault/'+relative)
    print(json.dumps({'assets':len(assets),'added':len(additions),'counts':manifest['counts'],'zip_bytes':bundle.stat().st_size},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-map',type=Path)
    parser.add_argument('--source-root',type=Path,default=ROOT)
    parser.add_argument('--images-only',action='store_true')
    parser.add_argument('--package-only',action='store_true')
    parser.add_argument('--videos-only',action='store_true')
    parser.add_argument('--video',action='append',help='Render only a specified video id; repeatable.')
    args=parser.parse_args()
    for folder in ('images','thumbs','video','gif','meta'): (VAULT/folder).mkdir(exist_ok=True)
    if args.source_map: prepare_images(json.loads(args.source_map.read_text()))
    if args.package_only:
        package()
    elif not args.images_only:
        specs=[v for v in VIDEOS if not args.video or v[0] in args.video]
        with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(lambda v:render_video(v,args.source_root),specs))
        if not args.videos_only and not args.video: package()
