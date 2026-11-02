"""Lista vídeos do Mixkit por busca (ids + miniaturas) e baixa: mixkit.py busca termo [termo...] | mixkit.py baixa id [id...]"""
import os, re, sys, json, subprocess, time
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mix")
UA = "Mozilla/5.0"
def get(url, out=None):
    cmd = ["curl", "-s", "-L", "-A", UA, "--max-time", "120", url]
    if out:
        cmd += ["-o", out, "-w", "%{http_code}"]
    r = subprocess.run(cmd, capture_output=True, text=not out or True)
    return r.stdout
if sys.argv[1] == "busca":
    idx = json.load(open(f"{D}/idx.json")) if os.path.exists(f"{D}/idx.json") else {}
    for q in sys.argv[2:]:
        h = get(f"https://mixkit.co/free-stock-video/{q}/")
        ids = []
        for m in re.finditer(r'https://assets.mixkit.co/videos/(\d+)/\1-thumb-360-0\.jpg', h):
            if m.group(1) not in ids:
                ids.append(m.group(1))
        # títulos (alt das imagens)
        for i in ids:
            t = re.search(rf'alt="([^"]+)"[^>]*{i}-thumb|{i}-thumb[^>]*alt="([^"]+)"', h)
            idx[i] = {"q": q, "titulo": (t.group(1) or t.group(2)) if t else ""}
            p = f"{D}/t_{i}.jpg"
            if not os.path.exists(p):
                get(f"https://assets.mixkit.co/videos/{i}/{i}-thumb-360-0.jpg", p)
        print(q, len(ids))
        json.dump(idx, open(f"{D}/idx.json", "w"), indent=1)
elif sys.argv[1] == "baixa":
    for i in sys.argv[2:]:
        for r in ("1080", "720"):
            p = f"{D}/v_{i}.mp4"
            code = get(f"https://assets.mixkit.co/videos/{i}/{i}-{r}.mp4", p)
            if code == "200" and os.path.getsize(p) > 100000:
                print(i, r, os.path.getsize(p) // 1000000, "MB")
                break
