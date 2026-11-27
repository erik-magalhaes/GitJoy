#!/usr/bin/env python3
"""Baixa a FOTO PRINCIPAL de cada jogo do site antigo (Acervo de Jogos), exatamente o arquivo que o site mostra na
vitrine (cartão do jogo na lista do acervo, 1024 px), para subir na Rejoy (13/nov/2026). Sem as fotos da galeria.
O arquivo é salvo como veio do site (webp/jpg/png); como a Rejoy pode não aceitar webp, sai também uma cópia em JPG
(qualidade 95, visualmente idêntica).
    /usr/bin/python3 baixar.py → out/fotos_site_acervo.zip (cópias em JPG + lista.csv) e
    out/fotos_site_acervo_ORIGINAIS_webp.zip (os arquivos exatamente como estão no site)
"""
import csv, html, os, re, subprocess, zipfile
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

BASE = "https://suavez.acervodejogos.com.br"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
ORIG, FOTOS = os.path.join(OUT, "originais"), os.path.join(OUT, "fotos")


def get(url):
    return subprocess.run(["curl", "-sL", "--retry", "3", "-A", "Mozilla/5.0", url], capture_output=True).stdout


def cartoes():
    vistos, res = set(), []
    for p in range(1, 20):
        h = get(f"{BASE}/boardgames?page={p}").decode()
        novos = 0
        for blk in re.split(r'<a href="/boardgames/', h)[1:]:
            m = re.match(r'([a-z0-9\-]+)" class="lojacard-block">.*?<img src="([^"]+)" alt="([^"]*)"', blk, re.S)
            if m and m.group(1) not in vistos:
                vistos.add(m.group(1)); novos += 1
                res.append((m.group(1), m.group(2), html.unescape(m.group(3)).strip()))
        if not novos:
            break
    return res


def um(c):
    slug, url, nome = c
    dado = get(url)
    ext = "png" if dado[:4] == b"\x89PNG" else "webp" if dado[8:12] == b"WEBP" else "jpg"
    base = re.sub(r'[\\/:*?"<>|]', "", nome)
    open(os.path.join(ORIG, f"{base}.{ext}"), "wb").write(dado)
    if ext == "webp":
        im = Image.open(os.path.join(ORIG, f"{base}.{ext}"))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA"); fundo = Image.new("RGB", im.size, (255, 255, 255)); fundo.paste(im, mask=im.getchannel("A")); im = fundo
        im.convert("RGB").save(os.path.join(FOTOS, f"{base}.jpg"), quality=95, subsampling=0)
        final = f"{base}.jpg"
    else:
        open(os.path.join(FOTOS, f"{base}.{ext}"), "wb").write(dado)
        final = f"{base}.{ext}"
    w, h = Image.open(os.path.join(FOTOS, final)).size
    return nome, final, f"{w}x{h}", f"{BASE}/boardgames/{slug}"


if __name__ == "__main__":
    os.makedirs(ORIG, exist_ok=True); os.makedirs(FOTOS, exist_ok=True)
    cs = cartoes()
    with ThreadPoolExecutor(8) as ex:
        res = sorted(ex.map(um, cs), key=lambda r: r[0].lower())
    with open(os.path.join(OUT, "lista.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["jogo", "arquivo", "tamanho", "página no site antigo"])
        w.writerows(res)
    with zipfile.ZipFile(os.path.join(OUT, "fotos_site_acervo.zip"), "w") as z:
        for a in sorted(os.listdir(FOTOS)):
            z.write(os.path.join(FOTOS, a), "fotos/" + a)
        z.write(os.path.join(OUT, "lista.csv"), "lista.csv")
    with zipfile.ZipFile(os.path.join(OUT, "fotos_site_acervo_ORIGINAIS_webp.zip"), "w") as z:
        for a in sorted(os.listdir(ORIG)):
            z.write(os.path.join(ORIG, a), "originais/" + a)
    print(len(cs), "jogos;", len(os.listdir(FOTOS)), "fotos")
