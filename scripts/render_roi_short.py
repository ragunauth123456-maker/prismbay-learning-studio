"""Create one original PrismBay AI educational Short without third-party footage or audio."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess, wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / ".render"
TMP.mkdir(exist_ok=True)
OUT = ROOT / "assets" / "ai-roi-mini-case.mp4"
FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
BOLD = str(FONT_DIR / "arialbd.ttf")
REGULAR = str(FONT_DIR / "arial.ttf")
W, H, FPS = 1080, 1920, 30
CARDS = [
    ("AI ROI", "3 NUMBERS\nBEFORE YOU BUY", "Start with a measurable workflow, not a demo.", 4),
    ("NUMBER 1", "HOURLY\nLABOR COST", "Include payroll, overhead and supervision.", 4),
    ("NUMBER 2", "HOURS\nACTUALLY SAVED", "Count completed work after human review.", 4),
    ("NUMBER 3", "TOTAL\nAI COST", "Tools + implementation + quality checks.", 4),
    ("ILLUSTRATIVE EXAMPLE", "$200 VALUE\n$220 COST\n-$20 NET", "A negative pilot result calls for a redesign.", 5),
    ("YOUR NEXT STEP", "FREE AI\nROI GUIDE", "First link on @PrismBayAI. Original free lessons.", 5),
]
def frame(i, label, heading, detail):
    img=Image.new("RGB",(W,H),(12,27,46))
    d=ImageDraw.Draw(img)
    for y in range(0,H,18):
        mix=y/H
        d.rectangle((0,y,W,y+17), fill=(int(9+18*mix),int(27+20*mix),int(47+25*mix)))
    d.rounded_rectangle((75,100,1004,116),radius=8,fill=(24,211,177))
    d.text((85,170),"PRISMBAY AI  /  ORIGINAL LESSON",font=ImageFont.truetype(BOLD,37),fill=(146,224,213))
    d.text((85,350),label,font=ImageFont.truetype(BOLD,46),fill=(31,218,183))
    fs=99 if i!=4 else 108
    d.multiline_text((80,490),heading,font=ImageFont.truetype(BOLD,fs),fill=(249,253,255),spacing=32,stroke_width=0)
    d.rounded_rectangle((75,1175,1005,1425),radius=28,fill=(25,59,80))
    df=ImageFont.truetype(REGULAR,45)
    rows=[];current=""
    for word in detail.split():
        candidate=(current+" "+word).strip()
        if current and d.textlength(candidate,font=df)>790:
            rows.append(current);current=word
        else: current=candidate
    if current: rows.append(current)
    d.multiline_text((116,1225),"\n".join(rows),font=df,fill=(236,247,251),spacing=19)
    d.text((85,1580),"FREE GUIDE IN CHANNEL PROFILE" if i==5 else "THREE-NUMBER AI VALUE TEST",font=ImageFont.truetype(BOLD,39),fill=(55,224,194))
    d.text((85,1670),"Own-brand educational content  |  PrismBay",font=ImageFont.truetype(REGULAR,30),fill=(156,177,193))
    for j in range(6):
        x=84+j*155
        d.rounded_rectangle((x,1760,x+116,1770),radius=5,fill=(31,218,183) if j<=i else (62,91,108))
    p=TMP/f"card_{i}.png"
    img.save(p,optimize=True)
    return p
def music(seconds):
    rate=32000
    t=np.arange(int((seconds+1)*rate),dtype=np.float64)/rate
    attack=np.minimum(1,t/.9)
    release=np.clip((seconds-t)/1.2,0,1)
    # Original, royalty-free synthesized ambient chord, no imported recording.
    notes=(110.0,130.81,164.81,220.0)
    tone=sum(np.sin(2*math.pi*f*t+(i*.41))*[.29,.20,.15,.10][i] for i,f in enumerate(notes))
    wobble=.9+.1*np.sin(2*math.pi*.14*t)
    audio=np.int16(np.clip(tone*wobble*attack*release*.11,-1,1)*32767)
    path=TMP/"original_ambient.wav"
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(audio.tobytes())
    return path
def main():
    import shutil
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg: raise RuntimeError("ffmpeg not installed")
    args=[ffmpeg,"-hide_banner","-loglevel","warning","-y"]
    durations=[]
    for i,(label,heading,detail,seconds) in enumerate(CARDS):
        png=frame(i,label,heading,detail)
        durations.append(seconds)
        args += ["-loop","1","-framerate",str(FPS),"-t",str(seconds),"-i",str(png)]
    fade=.35
    full=sum(durations)-fade*(len(durations)-1)
    audio=music(full)
    args+=["-i",str(audio)]
    filters=[f"[{i}:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[v{i}]" for i in range(len(CARDS))]
    prev="v0";elapsed=float(durations[0])
    for i in range(1,len(CARDS)):
        out=f"x{i}"
        filters.append(f"[{prev}][v{i}]xfade=transition=fade:duration={fade}:offset={elapsed-fade:.2f}[{out}]")
        prev=out;elapsed+=durations[i]-fade
    args += ["-filter_complex",";".join(filters),"-map",f"[{prev}]","-map",f"{len(CARDS)}:a","-t",f"{full:.2f}",
             "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
             "-c:a","aac","-b:a","96k","-movflags","+faststart",str(OUT)]
    subprocess.run(args,check=True,timeout=240)
    print("VIDEO_BUILT",OUT,OUT.stat().st_size,"bytes","duration_target",round(full,2),flush=True)
if __name__=="__main__": main()
