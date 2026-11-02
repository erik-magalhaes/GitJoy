"""3 quadros de cada clipe baixado + duração -> out/clipes.jpg"""
import glob, os, subprocess
from PIL import Image, ImageDraw, ImageFont
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
vs = sorted(glob.glob("mix/v_*.mp4"))
rows = []
for v in vs:
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout)
    ims = []
    for k in (0.1, 0.5, 0.9):
        p = "/tmp/claude-0/-home-user-GitJoy/3517be86-3457-5c07-bb4d-0fd99650d4f1/scratchpad/fr.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(d * k), "-i", v, "-frames:v", "1", "-vf", "scale=280:-1", p])
        ims.append(Image.open(p).copy())
    rows.append((os.path.basename(v)[2:-4], d, ims))
H = rows[0][2][0].height
im = Image.new("RGB", (280 * 3 * 2, (H + 4) * ((len(rows) + 1) // 2)), "white")
dr = ImageDraw.Draw(im)
for k, (n, d, ims) in enumerate(rows):
    x0 = (k % 2) * 840
    y0 = (k // 2) * (H + 4)
    for j, a in enumerate(ims):
        im.paste(a.resize((280, H)), (x0 + j * 280, y0))
    dr.text((x0 + 4, y0 + 4), f"{n} {d:.1f}s", fill="yellow", font=f, stroke_width=2, stroke_fill="black")
im.save("out/clipes.jpg", quality=80)
