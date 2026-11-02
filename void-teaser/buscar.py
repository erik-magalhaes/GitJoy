"""Busca imagens livres no Openverse (licenças comerciais) e baixa candidatos: buscar.py chave "consulta" [n]"""
import sys, json, os, urllib.request, urllib.parse, ssl
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
chave, q = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
    {"q": q, "page_size": n, "license_type": "commercial", "aspect_ratio": "", "size": os.environ.get("TAM", "large")})
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
import time
for t in range(4):
    try:
        res = json.load(urllib.request.urlopen(req, context=ctx, timeout=60))["results"]; break
    except Exception as e:
        print("busca falhou", e); time.sleep(5 * 2 ** t)
os.makedirs("cand", exist_ok=True)
meta = json.load(open("cand/meta.json")) if os.path.exists("cand/meta.json") else {}
for i, r in enumerate(res):
    nome = f"{chave}_{i:02d}.jpg"
    if os.path.exists("cand/" + nome):
        continue
    import time
    for tent in range(4):
      try:
        u = r["url"]
        if "upload.wikimedia.org/wikipedia/commons/" in u and "/thumb/" not in u:
            p = u.split("/wikipedia/commons/")[1]
            u = "https://upload.wikimedia.org/wikipedia/commons/thumb/" + p + "/1280px-" + p.split("/")[-1]
        rq = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        dados = urllib.request.urlopen(rq, context=ctx, timeout=30).read()
        open("cand/" + nome, "wb").write(dados)
        meta[nome] = {k: r.get(k) for k in ("title", "creator", "license", "license_version", "foreign_landing_url", "url", "width", "height")}
        break
      except Exception as e:
        print("falhou", nome, e); time.sleep(3 * 2 ** tent)
json.dump(meta, open("cand/meta.json", "w"), indent=1, ensure_ascii=False)
print(chave, len(res))
