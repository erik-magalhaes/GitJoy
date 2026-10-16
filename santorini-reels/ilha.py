"""Ilha do Santorini desenhada em isométrico (PIL): tabuleiro 5x5 sobre penhasco, torres brancas em 3 andares
(cada andar mais estreito, como as peças do jogo), cúpula azul e construtores (peão: base, corpo e cabeça).

    estado = {(x, y): nível 0..3, ...}, cupulas = {(x, y)}, peoes = {(x, y): cor}
    img = ilha(estado, cupulas, peoes, tile=150, luz="dia")   # RGBA, fundo transparente
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

N = 5
ALT = [0, 64, 56, 50]          # altura de cada andar (px no tile=150)
LARG = [1.0, 0.86, 0.72, 0.58]  # largura do andar (fração da casa)
PALETA = {
    "dia": dict(topo=(250, 250, 246), esq=(222, 224, 226), dir=(196, 200, 206), linha=(150, 160, 170),
                grama=(126, 190, 86), grama2=(108, 172, 72), rocha=(176, 128, 92), rocha2=(140, 98, 70),
                cupula=(30, 84, 196), cupula_luz=(92, 150, 240)),
    "sol": dict(topo=(255, 238, 214), esq=(240, 204, 176), dir=(196, 150, 140), linha=(170, 120, 110),
                grama=(150, 170, 80), grama2=(126, 146, 66), rocha=(190, 112, 80), rocha2=(140, 78, 62),
                cupula=(40, 70, 170), cupula_luz=(250, 170, 120)),
}
PEOES = {"azul": ((36, 78, 170), (88, 136, 226)), "laranja": ((226, 110, 30), (255, 170, 90)),
         "branco": ((210, 210, 214), (255, 255, 255)), "cinza": ((110, 114, 122), (170, 174, 182))}


def _iso(x, y, z, tile, ox, oy):
    """Casa (x, y) com altura z (px) → ponto na tela."""
    return ox + (x - y) * tile / 2, oy + (x + y) * tile / 4 - z


def _prisma(d, cx, cy, z0, z1, frac, tile, ox, oy, c, contorno=True):
    """Bloco com base em (cx, cy) (centro da casa, coords de grade), de z0 a z1."""
    h = frac / 2
    pts = {}
    for k, (dx, dy) in enumerate([(-h, -h), (h, -h), (h, h), (-h, h)]):
        pts[k] = (_iso(cx + dx, cy + dy, z1, tile, ox, oy), _iso(cx + dx, cy + dy, z0, tile, ox, oy))
    top = [pts[k][0] for k in range(4)]
    esq = [pts[3][0], pts[2][0], pts[2][1], pts[3][1]]
    dir_ = [pts[2][0], pts[1][0], pts[1][1], pts[2][1]]
    lw = max(1, int(tile / 75)) if contorno else 0
    d.polygon(esq, fill=c["esq"], outline=c["linha"] if lw else None, width=lw)
    d.polygon(dir_, fill=c["dir"], outline=c["linha"] if lw else None, width=lw)
    d.polygon(top, fill=c["topo"], outline=c["linha"] if lw else None, width=lw)
    return top


def _janelas(d, cx, cy, z0, z1, frac, tile, ox, oy, c):
    """Porta/janela escura em cada face visível (lembra as peças do jogo)."""
    h = frac / 2
    for (a, b) in [((-h, h), (h, h)), ((h, h), (h, -h))]:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        w = frac * 0.16
        zz0, zz1 = z0 + (z1 - z0) * 0.18, z0 + (z1 - z0) * 0.62
        if a[1] == b[1]:
            p = [(cx + mx - w, cy + my), (cx + mx + w, cy + my)]
        else:
            p = [(cx + mx, cy + my + w), (cx + mx, cy + my - w)]
        quad = [_iso(*p[0], zz1, tile, ox, oy), _iso(*p[1], zz1, tile, ox, oy),
                _iso(*p[1], zz0, tile, ox, oy), _iso(*p[0], zz0, tile, ox, oy)]
        d.polygon(quad, fill=(120, 150, 190))


def _cupula(img, cx, cy, z, frac, tile, ox, oy, c):
    """Cúpula azul: meia esfera em isométrico (elipse + meio disco), com brilho."""
    x, y = _iso(cx, cy, z, tile, ox, oy)
    rx = frac * tile * 0.5 * 0.92
    ry = rx * 0.5
    hh = rx * 0.95
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=c["cupula"])
    d.pieslice((x - rx, y - hh, x + rx, y + hh), 180, 360, fill=c["cupula"])
    d.ellipse((x - rx * 0.55, y - hh * 0.8, x - rx * 0.05, y - hh * 0.35), fill=c["cupula_luz"] + (150,))
    img.alpha_composite(lay)


def _peao(img, cx, cy, z, cor, tile, ox, oy, sombra=True):
    x, y = _iso(cx, cy, z, tile, ox, oy)
    esc, luz = PEOES[cor]
    s = tile / 150
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if sombra:
        d.ellipse((x - 30 * s, y - 10 * s, x + 30 * s, y + 10 * s), fill=(0, 0, 0, 70))
    d.ellipse((x - 24 * s, y - 12 * s, x + 24 * s, y + 6 * s), fill=esc)              # base
    d.polygon([(x - 17 * s, y - 6 * s), (x + 17 * s, y - 6 * s), (x + 9 * s, y - 52 * s), (x - 9 * s, y - 52 * s)],
              fill=esc)                                                               # corpo
    d.polygon([(x - 13 * s, y - 8 * s), (x - 2 * s, y - 8 * s), (x - 3 * s, y - 50 * s), (x - 8 * s, y - 50 * s)],
              fill=luz)                                                               # brilho
    d.ellipse((x - 15 * s, y - 78 * s, x + 15 * s, y - 48 * s), fill=esc)             # cabeça
    d.ellipse((x - 9 * s, y - 74 * s, x + 1 * s, y - 62 * s), fill=luz)
    img.alpha_composite(lay)


def ilha(estado=None, cupulas=(), peoes=None, tile=150, luz="dia", destaque=None, extra=None):
    """Desenha a ilha. destaque = {(x, y): (r, g, b, a)} pinta casas (setas/alcance). extra(d, iso) desenha por cima."""
    estado = estado or {}
    peoes = peoes or {}
    c = PALETA[luz]
    W = int(tile * N + tile * 0.6)
    H = int(tile * N / 2 + tile * 2.6)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = W / 2, tile * 1.55
    d = ImageDraw.Draw(img)
    # penhasco
    prof = tile * 0.55
    cantos = [_iso(-0.5, -0.5, 0, tile, ox, oy), _iso(N - 0.5, -0.5, 0, tile, ox, oy), _iso(N - 0.5, N - 0.5, 0, tile, ox, oy),
              _iso(-0.5, N - 0.5, 0, tile, ox, oy)]
    a, b, cc, e = cantos
    d.polygon([e, cc, (cc[0], cc[1] + prof), (e[0], e[1] + prof)], fill=c["rocha"])
    d.polygon([cc, b, (b[0], b[1] + prof), (cc[0], cc[1] + prof)], fill=c["rocha2"])
    rng = np.random.default_rng(3)
    for _ in range(40):  # ranhuras da rocha
        t = rng.random()
        lado = rng.random() < 0.5
        p0 = (e[0] + (cc[0] - e[0]) * t, e[1] + (cc[1] - e[1]) * t) if lado else (cc[0] + (b[0] - cc[0]) * t, cc[1] + (b[1] - cc[1]) * t)
        dz = prof * (0.2 + 0.7 * rng.random())
        d.line([(p0[0], p0[1] + prof * 0.1), (p0[0], p0[1] + dz)], fill=c["rocha2"] if lado else c["rocha"], width=3)
    d.polygon(cantos, fill=c["grama"])
    for x in range(N):
        for y in range(N):
            q = [_iso(x + dx, y + dy, 0, tile, ox, oy) for dx, dy in [(-0.46, -0.46), (0.46, -0.46), (0.46, 0.46), (-0.46, 0.46)]]
            col = c["grama2"] if (x + y) % 2 else c["grama"]
            if destaque and (x, y) in destaque:
                d.polygon(q, fill=col)
                lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ImageDraw.Draw(lay).polygon(q, fill=destaque[(x, y)])
                img.alpha_composite(lay)
                d = ImageDraw.Draw(img)
            else:
                d.polygon(q, fill=col)
            d.line(q + [q[0]], fill=(236, 230, 210), width=max(1, int(tile / 60)))
    # peças de trás para a frente
    for s in range(2 * N - 1):
        for x in range(N):
            y = s - x
            if not 0 <= y < N:
                continue
            nv = estado.get((x, y), 0)
            z = 0
            for lv in range(1, nv + 1):
                _prisma(d, x, y, z, z + ALT[lv] * tile / 150, LARG[lv] * 0.92, tile, ox, oy, c)
                _janelas(d, x, y, z, z + ALT[lv] * tile / 150, LARG[lv] * 0.92, tile, ox, oy, c)
                z += ALT[lv] * tile / 150
            if (x, y) in cupulas:
                _cupula(img, x, y, z, LARG[min(3, nv + 1)] * 0.92, tile, ox, oy, c)
                d = ImageDraw.Draw(img)
            if (x, y) in peoes:
                _peao(img, x, y, z, peoes[(x, y)], tile, ox, oy)
                d = ImageDraw.Draw(img)
    if extra:
        extra(ImageDraw.Draw(img), lambda x, y, z=0: _iso(x, y, z, tile, ox, oy), img)
    return img


def altura(nv, tile=150):
    return sum(ALT[1:nv + 1]) * tile / 150


def mar(W, H, topo=(124, 206, 236), fundo=(18, 90, 168), ondas=True, seed=1):
    """Mar em degradê com reflexos de onda (cartoon, sem ruído)."""
    yy = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(topo) * (1 - yy) + np.array(fundo) * yy) * np.ones((1, W, 1))
    img = Image.fromarray(a.astype(np.uint8), "RGB").convert("RGBA")
    if ondas:
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(seed)
        for _ in range(70):
            x, y = rng.random() * W, rng.random() * H
            w = 30 + rng.random() * 60
            d.arc((x - w, y - 8, x + w, y + 8), 200, 340, fill=(255, 255, 255, 90), width=3)
    return img


def ceu(W, H, cores=((255, 196, 140), (250, 142, 120), (120, 96, 168))):
    yy = np.linspace(0, 1, H)
    out = np.zeros((H, W, 3))
    for i in range(H):
        u = yy[i] * (len(cores) - 1)
        k = min(int(u), len(cores) - 2)
        f = u - k
        out[i] = np.array(cores[k]) * (1 - f) + np.array(cores[k + 1]) * f
    return Image.fromarray(out.astype(np.uint8), "RGB").convert("RGBA")
