#!/usr/bin/env python3
"""COMO CHEGAR no Beca’s de TREM ou ÔNIBUS (7/nov/2026, pedido dele): "como se fosse o Google Maps, só que tipo um
sketch, colorido, bonitinho". Mapa DESENHADO a partir das ruas reais do OpenStreetMap (`mapa/area.osm`, © OSM
contributors, ODbL): Estação Mauá (CPTM Linha 10-Turquesa) e Terminal Municipal de Mauá → Igreja Matriz → Rua Sorocaba, 35.
Rota a pé = menor caminho no grafo das ruas (`mapa/rota.py`): estação ≈ 200 m, terminal ≈ 340 m.
Ícones: OpenMoji (CC BY-SA 4.0) em `mapa/openmoji/`.

    /usr/bin/python3 mapa_becas.py            # post 1080x1350 + story 1080x1920 → out/mapa/
    /usr/bin/python3 mapa_becas.py --reels    # vídeo: o mapa se desenha, a rota anda até o pin (+ --stories)
"""
import math
import os
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "mapa"))
import rota as R  # noqa: E402

ROOT = os.path.dirname(AQUI)
OUT = os.path.join(AQUI, "out", "mapa")
FONTES = os.path.join(ROOT, "assinatura-reels", "assets", "fonts")
MAO = os.path.join(ROOT, "taco-reels", "assets", "fonts")
OM = os.path.join(AQUI, "mapa", "openmoji")

MAR = (63, 36, 18)
TINTA = (78, 56, 44)
PAPEL = (248, 241, 226)
QUARTEIRAO = (241, 232, 214)
AZUL = (66, 133, 244)
VERMELHO = (234, 67, 53)
TURQ = (0, 163, 168)
LAR = (244, 136, 37)
PET = (28, 124, 150)
AMA = (255, 199, 31)
VERDE = (52, 168, 83)
LILAS = (150, 110, 200)
BR = (255, 255, 255)

SS = 2  # desenha em 2x e reduz (traço liso)


def lilita(s):
    return ImageFont.truetype(os.path.join(FONTES, "LilitaOne.ttf"), int(s))


def fig(s, peso=800):
    f = ImageFont.truetype(os.path.join(FONTES, "Figtree.ttf"), int(s))
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def mao(s):
    return ImageFont.truetype(os.path.join(MAO, "PatrickHand-Regular.ttf"), int(s))


# ------------------------------------------------------------------ projeção
ROT = 20  # 7/nov: mapa girado (horário) para a rota ficar na diagonal da tela e caber com mais zoom; tem bússola


class Proj:
    """centro = (lat, lon, ox, oy): o ponto geográfico cai em (w/2 + ox, h/2 + oy) (px em 1x)."""
    def __init__(self, w, h, centro, mpp):
        self.w, self.h, self.mpp = w, h, mpp
        self.c = centro[:2]
        self.ox, self.oy = (centro[2], centro[3]) if len(centro) > 3 else (0.0, 0.0)
        self.kx = 111320 * math.cos(math.radians(centro[0]))
        self.co, self.si = math.cos(math.radians(ROT)), math.sin(math.radians(ROT))

    def __call__(self, p):
        x = (p[1] - self.c[1]) * self.kx / self.mpp
        y = -(p[0] - self.c[0]) * 111320 / self.mpp
        x, y = x * self.co - y * self.si, x * self.si + y * self.co
        return ((x + self.ox) * SS + self.w * SS / 2, (y + self.oy) * SS + self.h * SS / 2)


def denso(pts, passo):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / passo))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out


def treme(pts, amp, seed):
    """Desloca cada ponto na perpendicular com um ruído suave (traço de mão)."""
    rng = np.random.default_rng(seed)
    f1, f2, p1, p2 = rng.uniform(0.006, 0.012), rng.uniform(0.02, 0.04), *rng.uniform(0, 6.3, 2)
    out, s = [], 0.0
    for i, (x, y) in enumerate(pts):
        if i:
            s += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        o = amp * (0.65 * math.sin(s * f1 / SS + p1) + 0.35 * math.sin(s * f2 / SS + p2))
        out.append((x - dy / n * o, y + dx / n * o))
    return out


def linha(d, pts, cor, w, seed, amp=1.6):
    if len(pts) < 2:
        return
    d.line(treme(denso(pts, 14 * SS), amp * SS, seed), fill=cor, width=int(w * SS), joint="curve")


def poligono(d, pts, cor, contorno, seed, w=3):
    p = treme(denso(pts + [pts[0]], 14 * SS), 1.4 * SS, seed)
    d.polygon(p, fill=cor)
    d.line(p, fill=contorno, width=int(w * SS), joint="curve")


def hachura(img, caixa, cor, alfa, seed, passo=16, ang=-35, mask=None):
    """Lápis de cor: riscos diagonais finos e irregulares."""
    x0, y0, x1, y1 = caixa
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed)
    t = math.radians(ang)
    dx, dy = math.cos(t), math.sin(t)
    L = math.hypot(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    k = -L
    while k < L:
        ox, oy = cx - dy * k, cy + dx * k
        j = rng.uniform(-3, 3) * SS
        a = int(alfa * rng.uniform(0.5, 1.0))
        d.line((ox - dx * L + j, oy - dy * L, ox + dx * L + j, oy + dy * L + rng.uniform(-6, 6) * SS),
               fill=cor + (a,), width=int(rng.uniform(1.5, 3.2) * SS))
        k += passo * SS * rng.uniform(0.6, 1.4)
    if mask is not None:
        lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(mask))))
    img.alpha_composite(lay)


# ------------------------------------------------------------------ ícones
@lru_cache(None)
def icone(cod, s):
    return Image.open(os.path.join(OM, cod + ".png")).convert("RGBA").resize((int(s), int(s)), Image.LANCZOS)


def selo(cod, s, cor):
    """Ícone OpenMoji num círculo branco com aro colorido e contorno de tinta (como o pin do Maps)."""
    pad = 10
    im = Image.new("RGBA", (s + 2 * pad, s + 2 * pad + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((pad + 3, pad + 9, pad + s + 3, pad + s + 9), fill=MAR + (90,))
    d.ellipse((pad, pad, pad + s, pad + s), fill=BR, outline=cor, width=max(4, s // 12))
    d.ellipse((pad - 2, pad - 2, pad + s + 2, pad + s + 2), outline=TINTA, width=3)
    ic = icone(cod, int(s * 0.78))
    im.alpha_composite(ic, (pad + (s - ic.width) // 2, pad + (s - ic.height) // 2))
    return im


def pilula(txt, f, cor, fg=BR, padx=22, h=None, sub=None, fsub=None):
    tw = int(f.getlength(txt))
    sw = int(fsub.getlength(sub)) if sub else 0
    h = h or int(f.size * 1.35) + (int(fsub.size * 1.15) if sub else 0)
    w = max(tw, sw) + 2 * padx
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w + 6, h + 6), h // 2 if not sub else 22, fill=MAR)
    d.rounded_rectangle((0, 0, w, h), h // 2 if not sub else 22, fill=cor, outline=MAR, width=4)
    if sub:
        d.text((w / 2, h * 0.36), txt, font=f, fill=fg, anchor="mm")
        d.text((w / 2, h * 0.74), sub, font=fsub, fill=fg, anchor="mm")
    else:
        d.text((w / 2, h / 2), txt, font=f, fill=fg, anchor="mm")
    return im


def cola(img, sp, x, y, ang=0.0):
    if ang:
        sp = sp.rotate(ang, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))


def pin(s):
    """Pin vermelho do Maps (gota) com a xícara dentro."""
    w, h = int(s * 1.0), int(s * 1.42)
    im = Image.new("RGBA", (w + 20, h + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = w / 2
    cx, cy = 10 + r, 8 + r
    gota = [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(math.radians(140), math.radians(400), 60)]
    gota += [(cx, 8 + h)]
    d.ellipse((cx - r * 0.55, 8 + h - 6, cx + r * 0.55, 8 + h + 12), fill=MAR + (80,))
    d.polygon([(x + 5, y + 6) for x, y in gota], fill=MAR + (120,))
    d.polygon(gota, fill=VERMELHO)
    d.line(gota + [gota[0]], fill=MAR, width=5, joint="curve")
    d.ellipse((cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62), fill=BR, outline=MAR, width=3)
    ic = icone("2615", int(r * 1.05))
    im.alpha_composite(ic, (int(cx - ic.width / 2), int(cy - ic.height / 2)))
    return im, (cx, 8 + h)  # ponta


# ------------------------------------------------------------------ o mapa
VIA = {  # tipo: (largura, cor do miolo)
    "trunk": (30, (255, 214, 120)), "trunk_link": (16, (255, 214, 120)),
    "primary": (27, (255, 224, 140)), "primary_link": (14, (255, 224, 140)),
    "secondary": (23, (255, 236, 170)), "secondary_link": (12, (255, 236, 170)),
    "tertiary": (20, BR), "tertiary_link": (11, BR),
    "residential": (17, BR), "unclassified": (15, BR), "living_street": (15, (250, 230, 226)),
    "pedestrian": (14, (250, 228, 222)), "service": (8, (252, 249, 242)), "busway": (10, (252, 236, 214)),
}
RUAS = [  # (nome no OSM, como escrever, posição ao longo da rua 0..1)
    ("Rua Sorocaba", "R. Sorocaba", 0.55),
    ("Rua Santa Cecília", "R. Santa Cecília", 0.5),
    ("Rua da Matriz", "R. da Matriz", 0.5),
    ("Avenida Queiroz Pedroso", "Av. Queiroz Pedroso", 0.5),
    ("Avenida Governador Mário Covas Júnior", "Av. Gov. Mário Covas Jr.", 0.4),
    ("Rua Jundiaí", "R. Jundiaí", 0.5),
    ("Rua Vereador Vicente Orlando", "R. Ver. Vicente Orlando", 0.5),
    ("Avenida Barão de Mauá", "Av. Barão de Mauá", 0.5),
]


def pts_way(P, ns):
    return [P(R.ND[n]) for n in ns if n in R.ND]


def centroide(ns):
    ps = [R.ND[n] for n in ns if n in R.ND]
    return (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))


def way_por(chave, valor):
    for _, t, ns in R.WAYS:
        if t.get(chave) == valor:
            return ns


ROTA_TERM, D_TERM = R.caminho(R.TERMINAL, R.BECAS)
ROTA_EST, D_EST = R.caminho(R.ESTACAO, R.BECAS)
ESTACAO_C = centroide(way_por("building", "train_station"))
TERMINAL_C = centroide(way_por("name", "Terminal Municipal de Mauá"))
MATRIZ_C = centroide(way_por("name", "Paróquia Imaculada Conceição"))


@lru_cache(None)
def base(w, h, centro, mpp):
    """Papel + quarteirões + praças + estação/terminal/igreja + trilhos + ruas (sem rota, sem ícones). Em 2x."""
    P = Proj(w, h, centro, mpp)
    W2, H2 = w * SS, h * SS
    img = Image.new("RGBA", (W2, H2), QUARTEIRAO + (255,))
    rng = np.random.default_rng(3)
    g = rng.normal(0, 5, (H2 // 4, W2 // 4))
    grao = Image.fromarray(np.clip(128 + g, 0, 255).astype(np.uint8)).resize((W2, H2), Image.BILINEAR)
    img = Image.composite(img, Image.new("RGBA", (W2, H2), (232, 222, 200, 255)), grao.point(lambda v: 255 if v > 120 else 225))
    hachura(img, (0, 0, W2, H2), (226, 200, 160), 60, 1, passo=22)
    d = ImageDraw.Draw(img)
    # praças, mata
    for _, t, ns in R.WAYS:
        if t.get("leisure") == "park" or t.get("natural") == "wood" or t.get("leisure") == "pitch":
            p = pts_way(P, ns)
            if len(p) > 3:
                poligono(d, p, (196, 228, 168, 255), (90, 140, 70, 255), hash(ns[0]) % 999, 2.5)
    # prédios que importam
    for chave, valor, cor, cont in (("building", "train_station", (196, 236, 236), TURQ),
                                    ("name", "Terminal Municipal de Mauá", (255, 222, 186), LAR),
                                    ("name", "Paróquia Imaculada Conceição", (230, 216, 246), LILAS),
                                    ("name", "Shopping Mauá Plaza", (236, 228, 240), (170, 150, 180))):
        ns = way_por(chave, valor)
        if ns:
            poligono(d, pts_way(P, ns), cor + (255,), cont + (255,), 7, 3)
    # trilhos (Linha 10-Turquesa): faixa turquesa + dormentes
    for _, t, ns in R.WAYS:
        if t.get("railway") == "rail":
            p = pts_way(P, ns)
            linha(d, p, TINTA, 11, 5, 0.8)
            linha(d, p, TURQ, 7, 5, 0.8)
    for _, t, ns in R.WAYS:
        if t.get("name") == "Linha 10 - Turquesa":
            p = denso(pts_way(P, ns), 22 * SS)
            for a, b in zip(p, p[1:]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                n = math.hypot(dx, dy) or 1
                d.line((a[0] - dy / n * 9 * SS, a[1] + dx / n * 9 * SS, a[0] + dy / n * 9 * SS, a[1] - dx / n * 9 * SS),
                       fill=TINTA, width=2 * SS)
    # ruas: primeiro todos os contornos, depois os miolos (os cruzamentos emendam)
    vias = [(VIA[t["highway"]], pts_way(P, ns), hash(ns[0]) % 9999) for _, t, ns in R.WAYS if t.get("highway") in VIA]
    vias.sort(key=lambda v: v[0][0])
    for (lw, _), p, sd in vias:
        linha(d, p, TINTA, lw + 7, sd)
    for (lw, cor), p, sd in vias:
        linha(d, p, cor, lw, sd + 1)
    # nomes das ruas, à mão, ao longo da rua
    for nome, txt, fr in RUAS:
        ws = [ns for _, t, ns in R.WAYS if t.get("name") == nome and t.get("highway") in VIA]
        if not ws:
            continue
        ns = max(ws, key=len)
        p = [P(R.ND[n]) for n in ns if n in R.ND]
        p = [q for q in p if 60 * SS < q[0] < W2 - 60 * SS and 60 * SS < q[1] < H2 - 60 * SS]
        if len(p) < 2:
            continue
        i = min(len(p) - 2, int(fr * (len(p) - 1)))
        (x0, y0), (x1, y1) = p[i], p[i + 1]
        ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        f = mao(30 * SS)
        tw = int(f.getlength(txt)) + 20 * SS
        lab = Image.new("RGBA", (tw, 46 * SS), (0, 0, 0, 0))
        ImageDraw.Draw(lab).text((tw / 2, 23 * SS), txt, font=f, fill=TINTA, anchor="mm",
                                 stroke_width=3 * SS, stroke_fill=PAPEL)
        cola(img, lab, (x0 + x1) / 2, (y0 + y1) / 2, ang)
    return img


def rota_pts(P, rota):
    return denso([P(p) for p in rota], 4)


def comprimento(p):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:]))


def bolinhas(d, p, cor, ate=1.0, passo=24):
    """Rota a pé do Maps: bolinhas, aqui um pouco tortas (desenhadas à mão)."""
    L = comprimento(p) * ate
    s, alvo, k = 0.0, 0.0, 0
    for a, b in zip(p, p[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        while alvo <= s + seg and alvo <= L:
            u = (alvo - s) / seg if seg else 0
            x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
            r = (8.5 + 1.2 * math.sin(k * 2.3)) * SS
            d.ellipse((x - r - 3 * SS, y - r - 3 * SS, x + r + 3 * SS, y + r + 3 * SS), fill=TINTA)
            d.ellipse((x - r, y - r, x + r, y + r), fill=cor, outline=BR, width=2 * SS)
            alvo += passo * SS
            k += 1
        s += seg


def ponto_em(p, frac):
    L = comprimento(p) * frac
    s = 0.0
    for a, b in zip(p, p[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if s + seg >= L:
            u = (L - s) / seg if seg else 0
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        s += seg
    return p[-1]


def mapa(w, h, centro, mpp, prog=1.0, pins=1.0, tempo=0.0):
    """Mapa pronto em 1x. prog = quanto da rota já foi desenhado; pins = escala de entrada dos ícones."""
    P = Proj(w, h, centro, mpp)
    img = base(w, h, centro, mpp).copy()
    d = ImageDraw.Draw(img)
    pt, pe = rota_pts(P, ROTA_TERM), rota_pts(P, ROTA_EST)
    bolinhas(d, pt, AZUL, prog)
    img = img.resize((w, h), Image.LANCZOS)
    q = lambda p: (P(p)[0] / SS, P(p)[1] / SS)  # noqa: E731
    ks = pins if isinstance(pins, tuple) else (pins,) * 4
    if max(ks) > 0:
        for k, (cod, cor, pos, txt, sub, dx, dy) in zip(ks, (("1F68C", LAR, TERMINAL_C, "TERMINAL DE ÔNIBUS", "Terminal Municipal", -40, -88),
                                                ("1F686", TURQ, ESTACAO_C, "ESTAÇÃO MAUÁ", "Linha 10-Turquesa", -40, 98),
                                                ("26EA", LILAS, MATRIZ_C, "IGREJA MATRIZ", None, -40, 108))):
            if k <= 0:
                continue
            x, y = q(pos)
            sp = selo(cod, int((84 if cod != "26EA" else 66) * k), cor)
            cola(img, sp, x + (-30 if cod == "26EA" else 0), y)
            if k >= 1:
                pl = pilula(txt, lilita(28), cor, sub=sub, fsub=fig(20, 800) if sub else None)
                px = min(w - pl.width / 2 - 12, max(pl.width / 2 + 12, x + dx))  # nunca sai da tela
                cola(img, pl, px, y + dy)
        k = ks[3]
        x, y = q(R.ALQUI)
        if k > 0:
            cola(img, selo("1F48A", int(48 * k), VERDE), x + 22, y + 6)
        if k >= 1:
            ImageDraw.Draw(img).text((x + 50, y + 8), "Alquifarma", font=mao(28), fill=TINTA, anchor="lm",
                                     stroke_width=3, stroke_fill=PAPEL)
    xs = [q(p)[0] for p in ROTA_TERM]
    ys = [q(p)[1] for p in ROTA_TERM]
    bussola(img, 82, min(ys) + 10)
    if 0 < prog < 1:  # quem está andando
        x, y = ponto_em(pt, prog)
        cola(img, selo("1F6B6", 64, AZUL), x / SS, y / SS - 34)
    return img, q


def bussola(img, x, y, r=46):
    """Rosa dos ventos à mão apontando o norte de verdade (o mapa está girado)."""
    d = ImageDraw.Draw(img)
    d.ellipse((x - r, y - r, x + r, y + r), fill=BR, outline=TINTA, width=4)
    a = math.radians(-90 + ROT)  # norte na tela
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    pn = [(x + ux * r * 0.78, y + uy * r * 0.78), (x + px * 11, y + py * 11), (x - px * 11, y - py * 11)]
    ps = [(x - ux * r * 0.7, y - uy * r * 0.7), (x + px * 11, y + py * 11), (x - px * 11, y - py * 11)]
    d.polygon(pn, fill=VERMELHO, outline=TINTA)
    d.polygon(ps, fill=(225, 215, 200), outline=TINTA)
    nx, ny = x + ux * (r + 22), y + uy * (r + 22)
    d.text((nx, ny), "N", font=lilita(34), fill=MAR, anchor="mm", stroke_width=4, stroke_fill=PAPEL)


# ------------------------------------------------------------------ peças paradas
def barra_busca(w):
    h = 96
    im = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=MAR + (150,))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=BR, outline=MAR, width=5)
    cx, cy = 58, h / 2
    d.ellipse((cx - 17, cy - 19, cx + 13, cy + 11), outline=TINTA, width=6)
    d.line((cx + 9, cy + 7, cx + 24, cy + 22), fill=TINTA, width=7)
    d.text((100, h / 2 - 15), "Beca’s Café", font=fig(36, 900), fill=MAR, anchor="lm")
    d.text((100, h / 2 + 20), "Rua Sorocaba, 35 · Mauá", font=fig(26, 700), fill=(120, 100, 90), anchor="lm")
    sv = Image.open(os.path.join(ROOT, "hobby-reels", "assets", "logo_suavez.png")).convert("RGBA")
    sv = sv.resize((int(sv.width * 70 / sv.height), 70), Image.LANCZOS)
    im.alpha_composite(sv, (w - sv.width - 22, (h - 70) // 2))
    return im


def minutos(m):
    return max(1, round(m / 75))


def folha(w, h, n=3, ty=74, y0=128, passo=98):
    """Painel de baixo (como o do Maps): de trem / de ônibus."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, h + 60), 44, fill=BR, outline=MAR, width=6)
    d.rounded_rectangle((w / 2 - 50, 16, w / 2 + 50, 26), 5, fill=(215, 205, 195))
    d.text((48, ty), "COMO CHEGAR", font=lilita(54), fill=MAR, anchor="lm")
    d.text((48 + lilita(54).getlength("COMO CHEGAR "), ty + 2), "de trem ou ônibus", font=mao(46), fill=PET, anchor="lm")
    linhas = [("1F686", TURQ, "De TREM: desce na Estação Mauá", f"Linha 10-Turquesa · uns {minutos(D_EST)} min a pé"),
              ("1F68C", LAR, "De ÔNIBUS: Terminal Municipal", f"do lado da estação · uns {minutos(D_TERM)} min a pé"),
              ("26EA", LILAS, "Passa pela Igreja Matriz", "e vira na Rua Sorocaba: é o nº 35!")]
    y = y0
    for cod, cor, a, b in linhas[:n]:
        im.alpha_composite(selo(cod, 70, cor), (34, y - 4))
        d.text((140, y + 22), a, font=fig(33, 900), fill=MAR, anchor="lm")
        d.text((140, y + 60), b, font=fig(27, 700), fill=(110, 92, 82), anchor="lm")
        y += passo
    return im


def titulo_folha(img, y):
    d = ImageDraw.Draw(img)
    f = lilita(40)
    txt = "TARDE DE JOGOS · SEXTA, 20/11 · 13H ÀS 19H"
    pl = pilula(txt, f, AMA, fg=MAR)
    cola(img, pl, img.width / 2, y, -1.2)


MPP = 0.33  # 7/nov: era 0,46 ("ficou muito longe, não dá pra entender")
MEIO = (-23.66876, -46.46112)  # meio do caminho terminal → Beca’s


def enquadra(w, h, y0, y1, mpp):
    """Centra a rota + estação/terminal/Matriz/Alquifarma na faixa visível y0..y1."""
    P = Proj(w, h, MEIO, mpp)
    pts = [P(p) for p in ROTA_TERM + [TERMINAL_C, ESTACAO_C, MATRIZ_C, R.ALQUI]]
    cx = (min(x for x, _ in pts) + max(x for x, _ in pts)) / 2 / SS
    cy = (min(y for _, y in pts) + max(y for _, y in pts)) / 2 / SS
    return MEIO + (w / 2 - cx, (y0 + y1) / 2 - cy)


CENTRO = enquadra(1080, 990, 170, 980, MPP)  # post: entre a barra de busca e o painel


def pin_becas(tela, q):
    x, y = q(R.BECAS)
    p, ponta = pin(96)
    tela.alpha_composite(p, (int(x - ponta[0]), int(y - ponta[1])))
    cola(tela, pilula("CHEGOU!", lilita(34), VERMELHO), x + 150, y - 118, -3)


def post():
    W, H = 1080, 1350
    Y0 = 990
    img, q = mapa(W, Y0, CENTRO, MPP)
    tela = Image.new("RGBA", (W, H), PAPEL + (255,))
    tela.alpha_composite(img, (0, 0))
    pin_becas(tela, q)
    tela.alpha_composite(barra_busca(W - 80), (40, 40))
    tela.alpha_composite(folha(W, H - Y0, ty=82, y0=118, passo=78), (0, Y0))
    cola(tela, pilula("TARDE DE JOGOS · SEXTA, 20/11 · 13H ÀS 19H", lilita(34), AMA, fg=MAR), W / 2, Y0 + 2, -1.2)
    return tela.convert("RGB")


def story():
    W, H = 1080, 1920
    Y0 = 1060  # topo do painel
    img, q = mapa(W, Y0 + 80, enquadra(W, Y0 + 80, 250, Y0 - 20, MPP), MPP)
    tela = Image.new("RGBA", (W, H), PAPEL + (255,))
    tela.alpha_composite(img, (0, 0))
    pin_becas(tela, q)
    tela.alpha_composite(barra_busca(W - 80), (40, 120))
    fo = folha(W, H - Y0, n=2, ty=96, y0=150)
    d = ImageDraw.Draw(fo)
    # espaço LIVRE no meio da tela para o adesivo de link (y≈1500–1640): o link da rota no Maps
    d.text((W / 2, 1418 - Y0), "ABRE A ROTA NO SEU MAPS AQUI:", font=lilita(44), fill=PET, anchor="mm")
    seta = [(W / 2 - 22, 1450 - Y0), (W / 2 + 22, 1450 - Y0), (W / 2, 1482 - Y0)]
    d.polygon(seta, fill=VERMELHO, outline=MAR)
    d.rounded_rectangle((150, 1496 - Y0, W - 150, 1640 - Y0), 30, outline=(220, 208, 196), width=4)
    tela.alpha_composite(fo, (0, Y0))
    cola(tela, pilula("TARDE DE JOGOS · SEXTA, 20/11 · 13H ÀS 19H", lilita(34), AMA, fg=MAR), W / 2, Y0 + 2, -1.2)
    cola(tela, pilula("MANDA PRA QUEM VAI COM VOCÊ!", lilita(38), LAR), W / 2, 1735, -1.5)
    cola(tela, pilula("Rua Sorocaba, 35 · pertinho da Igreja Matriz", fig(30, 800), PET), W / 2, 1830, 0)
    return tela.convert("RGB")


# ------------------------------------------------------------------ vídeo (Reels e Stories)
VW, VH, FPS = 1080, 1920, 30
Y0V = 1060
DUR = 12.0
FMT = "reels"
T_PINS = (1.1, 1.35, 1.6, 1.8)  # terminal, estação, Matriz, Alquifarma
T_ROTA = (2.1, 6.0)
T_PIN, T_CHEGOU, T_FOLHA = 6.15, 6.6, 7.0


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def out_back(u, k=1.9):
    u = min(1.0, max(0.0, u)) - 1
    return 1 + (k + 1) * u ** 3 + k * u ** 2


def pop(img, sp, x, y, t, t0, ang=0.0, d=0.35):
    if t < t0:
        return
    e = out_back((t - t0) / d)
    if e <= 0.02:
        return
    sp = sp.resize((max(1, int(sp.width * e)), max(1, int(sp.height * e))), Image.LANCZOS)
    cola(img, sp, x, y, ang)


@lru_cache(None)
def mapa_vazio():
    return mapa(VW, VH, CENTRO_V, MPP, prog=0, pins=0)[0]


CENTRO_V = enquadra(VW, VH, 250, Y0V - 20, MPP)  # mapa na tela inteira, a rota no mesmo lugar do story


@lru_cache(None)
def folha_video(fmt):
    fo = folha(VW, VH - Y0V, n=3 if fmt == "reels" else 2, ty=96, y0=150)
    d = ImageDraw.Draw(fo)
    if fmt == "stories":
        d.text((VW / 2, 1418 - Y0V), "ABRE A ROTA NO SEU MAPS AQUI:", font=lilita(44), fill=PET, anchor="mm")
        d.polygon([(VW / 2 - 22, 1450 - Y0V), (VW / 2 + 22, 1450 - Y0V), (VW / 2, 1482 - Y0V)], fill=VERMELHO, outline=MAR)
    return fo


def quadro(t):
    tela = Image.new("RGBA", (VW, VH), PAPEL + (255,))
    # o mapa se desenha (varrida de lápis na diagonal, borda irregular)
    if t < 1.0:
        m = mapa_vazio()
        v = ease(t / 0.95) * (VW + VH * 0.6 + 200) - 100
        yy, xx = np.mgrid[0:m.height, 0:m.width]
        borda = 18 * np.sin(yy / 23.0) + 10 * np.sin(yy / 7.0 + 1)
        a = np.clip((v - (xx + yy * 0.6 + borda)) / 40, 0, 1)
        mm = m.copy()
        mm.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
        tela.alpha_composite(mm)
    else:
        ks = tuple(min(1.0, max(0.0, out_back((t - t0) / 0.35))) if t >= t0 + 0.35 else (0.0 if t < t0 else max(0.05, out_back((t - t0) / 0.35))) for t0 in T_PINS)
        prog = ease((t - T_ROTA[0]) / (T_ROTA[1] - T_ROTA[0]))
        img, q = mapa(VW, VH, CENTRO_V, MPP, prog=prog, pins=ks)
        tela.alpha_composite(img)
        if t >= T_PIN:  # o pin cai e quica
            x, y = q(R.BECAS)
            p, ponta = pin(100)
            u = (t - T_PIN) / 0.45
            yy = y - 320 * (1 - out_back(u, 1.4)) if u < 1 else y
            tela.alpha_composite(p, (int(x - ponta[0]), int(yy - ponta[1])))
            pop(tela, pilula("CHEGOU!", lilita(36), VERMELHO), x + 150, y - 118, t, T_CHEGOU, -3)
    # barra de busca digitando
    if t >= 0.1:
        bb = barra_busca(VW - 80)
        e = ease((t - 0.1) / 0.3)
        tela.alpha_composite(bb, (40, int(120 - 200 * (1 - e))))
    # gancho → faixa da tarde de jogos
    if t < T_FOLHA:  # embaixo do mapa, onde não tem rota
        pop(tela, pilula("VEM DE TREM OU DE ÔNIBUS?", lilita(58), AMA, fg=MAR, padx=34), VW / 2, 1420, t, 0.15, -2)
    # painel de baixo sobe
    if t >= T_FOLHA:
        e = ease((t - T_FOLHA) / 0.45)
        fo = folha_video(FMT)
        tela.alpha_composite(fo, (0, int(Y0V + (VH - Y0V) * (1 - e))))
        pop(tela, pilula("TARDE DE JOGOS · SEXTA, 20/11 · 13H ÀS 19H", lilita(34), AMA, fg=MAR), VW / 2, Y0V + 2, t,
            T_FOLHA + 0.45, -1.2)
        if FMT == "reels":
            pop(tela, pilula("COMENTA: VOCÊ VEM DE TREM OU DE ÔNIBUS?", lilita(36), LAR), VW / 2, 1610, t, T_FOLHA + 0.8, -1.5)
            pop(tela, pilula("Rua Sorocaba, 35 · pertinho da Igreja Matriz", fig(30, 800), PET), VW / 2, 1720, t, T_FOLHA + 1.0)
            pop(tela, pilula("GARANTA SUA MESA: WHATSAPP (11) 97793-3910", lilita(32), VERDE), VW / 2, 1815, t, T_FOLHA + 1.2, 1)
        else:
            pop(tela, pilula("MANDA PRA QUEM VAI COM VOCÊ!", lilita(38), LAR), VW / 2, 1735, t, T_FOLHA + 0.8, -1.5)
            pop(tela, pilula("Rua Sorocaba, 35 · pertinho da Igreja Matriz", fig(30, 800), PET), VW / 2, 1830, t, T_FOLHA + 1.0)
    return tela.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def audio(com, sem):
    import kit as K  # noqa: F401
    import sons as S
    ev = [(0.0, S.arrasta(0.9), 0.35), (0.15, S.cartao(), 0.4)]
    ev += [(t0, S.plim(), 0.3) for t0 in T_PINS[:3]]
    n = int((T_ROTA[1] - T_ROTA[0]) / 0.28)
    ev += [(T_ROTA[0] + 0.28 * k, S.tic(k % 2 == 0), 0.18) for k in range(n)]  # passinhos
    ev += [(T_PIN + 0.35, S.dado(), 0.3), (T_CHEGOU, S.sino(), 0.45), (T_FOLHA, S.sopro(0.4), 0.35),
           (T_FOLHA + 0.8, S.cartao(), 0.35), (T_FOLHA + 1.0, S.cartao(), 0.3), (T_FOLHA + 1.2, S.cartao(), 0.3)]
    S.grava(com, DUR, ev, S.musica_marimba_pop(DUR + 0.5), musica_ganho=0.42, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)


def video():
    global FMT
    import kit as K
    FMT = "stories" if "--stories" in sys.argv else "reels"
    nome = "mapa_" + FMT
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        ims = [quadro(x).resize((VW // 3, VH // 3)) for x in ts]
        f = Image.new("RGB", (VW // 3 * len(ims), VH // 3))
        for i, im in enumerate(ims):
            f.paste(im, (i * VW // 3, 0))
        f.save(os.path.join(OUT, f"frames_{nome}.jpg"))
        print("ok")
        return
    com, sem = os.path.join(OUT, f"{nome}_com.wav"), os.path.join(OUT, f"{nome}_sem.wav")
    audio(com, sem)
    K.OUT = OUT
    K.entrega(nome, DUR, render, com, sem)
    print("ok", nome)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--reels" in sys.argv or "--stories" in sys.argv:
        video()
        return
    post().save(os.path.join(OUT, "mapa_post.png"))
    story().save(os.path.join(OUT, "mapa_story.png"))
    print("ok", round(D_EST), round(D_TERM))


if __name__ == "__main__":
    main()
