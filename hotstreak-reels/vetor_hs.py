#!/usr/bin/env python3
"""Recorta personagens da arte VETORIAL do manual do Hot Streak, redesenhando só os traços escolhidos
(sem o fundo), com transparência e em qualquer resolução."""
import os

import pymupdf
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
MANUAL = os.path.join(ROOT, "assets", "manual.pdf")
P = os.path.join(ROOT, "assets", "pecas")


def replay(page, keep, clip=None, dpi=600):
    """Redesenha numa página nova só os caminhos aprovados por keep(i, d) e renderiza com alfa."""
    out = pymupdf.open()
    np_ = out.new_page(width=page.rect.width, height=page.rect.height)
    for i, d in enumerate(page.get_drawings()):
        if not keep(i, d):
            continue
        sh = np_.new_shape()
        for it in d["items"]:
            k = it[0]
            if k == "l":
                sh.draw_line(it[1], it[2])
            elif k == "c":
                sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif k == "re":
                sh.draw_rect(it[1])
            elif k == "qu":
                sh.draw_quad(it[1])
        sh.finish(fill=d.get("fill"), color=d.get("color"), width=d.get("width") or 0,
                  even_odd=d.get("even_odd", False), closePath=d.get("closePath", False),
                  fill_opacity=d.get("fill_opacity") or 1, stroke_opacity=d.get("stroke_opacity") or 1,
                  lineCap=max(d.get("lineCap") or (0,)) if isinstance(d.get("lineCap"), (tuple, list)) else 0,
                  lineJoin=d.get("lineJoin") or 0)
        sh.commit()
    pix = np_.get_pixmap(dpi=dpi, alpha=True, clip=clip)
    im = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    return im.crop(im.getbbox()) if im.getbbox() else im


def sem_fundo(page):
    W, H = page.rect.width, page.rect.height
    return lambda i, d: not ((d["rect"].width > W * 0.6 and d["rect"].height > H * 0.3) or d["rect"].width > W * 0.9)


if __name__ == "__main__":
    import sys
    doc = pymupdf.open(MANUAL)
    n = int(sys.argv[1])
    im = replay(doc[n], sem_fundo(doc[n]), dpi=150)
    im.save(os.path.join(ROOT, "out_vetor_teste.png"))
    print(im.size)


def dentro(page, box, extra=None):
    """Mantém só os traços cujo retângulo está todo dentro de box (em pontos do PDF)."""
    x0, y0, x1, y1 = box
    W, H = page.rect.width, page.rect.height

    def keep(i, d):
        r = d["rect"]
        if (r.width > W * 0.6 and r.height > H * 0.3) or r.width > W * 0.9:
            return False
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        ok = x0 <= cx <= x1 and y0 <= cy <= y1 and r.width < (x1 - x0) * 1.4
        return ok and (extra is None or extra(i, d))
    return keep


def extrai_tudo():
    os.makedirs(P, exist_ok=True)
    doc = pymupdf.open(MANUAL)
    pg = doc[12]
    # urso e rainha em pé (página do "depois de três corridas"), sem o degrau vermelho do pódio
    nao_vermelho = lambda i, d: not (d.get("fill") and d["fill"][0] > 0.85 and d["fill"][1] < 0.3 and d["fill"][2] < 0.3)
    fora_qr = lambda i, d: d["rect"].x0 < 360
    replay(pg, dentro(pg, (0, 0, 158, 383), nao_vermelho), dpi=500).save(os.path.join(P, "v_gobbler.png"))
    replay(pg, dentro(pg, (158, 0, 370, 383), lambda i, d: nao_vermelho(i, d) and fora_qr(i, d)),
           dpi=500).save(os.path.join(P, "v_mum.png"))
    # torcida da capa inteira (fundo animado do gancho)
    pix = doc[0].get_pixmap(dpi=300)
    Image.frombytes("RGB", (pix.width, pix.height), pix.samples).save(os.path.join(P, "v_torcida.png"))
    print("ok")


def limpa(path, frac=0.01):
    """Tira sobras pequenas soltas (pedaços de outros desenhos) mantendo os componentes grandes."""
    import cv2
    import numpy as np
    im = Image.open(path)
    a = np.asarray(im).copy()
    m = (a[..., 3] > 10).astype(np.uint8)
    m2 = cv2.dilate(m, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m2)
    big = st[1:, 4].max()
    ok = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= big * frac])
    a[~ok, 3] = 0
    im = Image.fromarray(a, "RGBA")
    im.crop(im.getbbox()).save(path)


def extrai_mais():
    doc = pymupdf.open(MANUAL)
    pg = doc[6]
    replay(pg, dentro(pg, (205, 0, 527, 383)), dpi=450).save(os.path.join(P, "v_dangle.png"))
    replay(pg, dentro(pg, (0, 0, 205, 383)), dpi=450).save(os.path.join(P, "v_gobbler2.png"))
    for n in ("v_gobbler", "v_mum", "v_dangle", "v_gobbler2"):
        limpa(os.path.join(P, n + ".png"))
    print("ok")


def extrai_podio():
    """Os quatro mascotes de corpo inteiro (desenho do pódio, página 3), em altíssima resolução."""
    doc = pymupdf.open(MANUAL)
    pg = doc[3]
    for nome, (x0, x1) in {"p_gobbler": (85, 160), "p_mum": (160, 222), "p_dangle": (222, 287),
                           "p_hurley": (287, 352)}.items():
        replay(pg, dentro(pg, (x0, 0, x1, 93)), dpi=2400).save(os.path.join(P, nome + ".png"))
        limpa(os.path.join(P, nome + ".png"), 0.02)
    print("ok")


def torcida_sem_qr(dpi=300, faixa=None):
    """Capa (torcida + placas HOT/STREAK) sem a placa amarela "VIDEO RULES" com o QR da editora.
    faixa=(i0, i1) renderiza só os traços nesse intervalo da ordem de pintura (para camadas)."""
    doc = pymupdf.open(MANUAL)
    pg = doc[0]
    dr = pg.get_drawings()
    sign = next(i for i, d in enumerate(dr) if d.get("fill") and abs(d["fill"][0] - 1.0) < 0.02
                and abs(d["fill"][1] - 0.77) < 0.02 and d["rect"].width > 120)
    sr = dr[sign]["rect"]

    def keep(i, d):
        if faixa and not (faixa[0] <= i < faixa[1]):
            return False
        if i == sign:
            return False
        r = d["rect"]
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        return not (i > sign and sr.x0 <= cx <= sr.x1 and sr.y0 <= cy <= sr.y1 and r.width < sr.width)
    return replay(pg, keep, dpi=dpi), sr, sign, len(dr)
