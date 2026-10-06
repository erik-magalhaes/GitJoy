#!/usr/bin/env python3
"""Nekojima ANIME com peças recortadas se mexendo (pedido do dono: "não pode parecer foto da internet").

A torre balança e desaba, os dados rolam e quicam, o poste cai do alto e encaixa, os cubos pulam para o
marcador de nível e o gatinho voa até o fio e fica balançando. Reaproveita o visual de anime do anime.py
(céu, linhas de velocidade, onomatopeias, sakura, VS) e o roteiro/narração do neko.py.

    python3 anime_rec.py --frame 3 14 42     # quadros de teste
    python3 anime_rec.py --only preview      # prévia com legendas
    python3 anime_rec.py                     # com e sem legendas
"""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import anime
from anime import (SCENES, seg, ease, lerp, out_back, paste_c, sky, speed_lines, petals, sparkles, bolt,
                   circle_mark, vs_screen, impact, draw_elements, panel, sfx_img, tag_img, jit, box_img,
                   POSE, W, H, INK, WHITE, PINK, TEAL, YELLOW, RED, scene_of)

PE = os.path.join(anime.ROOT, "assets", "pecas")


@lru_cache(None)
def piece(name):
    return Image.open(os.path.join(PE, name)).convert("RGBA")


@lru_cache(None)
def outlined(name, h):
    """Recorte com borda branca e contorno escuro, como figura recortada de anime."""
    im = piece(name)
    im = im.resize((max(2, int(im.width * h / im.height)), int(h)), Image.LANCZOS)
    pad = 16
    a = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    a.paste(im.getchannel("A"), (pad, pad))
    white = a.filter(ImageFilter.MaxFilter(9))
    dark = white.filter(ImageFilter.MaxFilter(5))
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    out.paste(INK + (255,), (0, 0), dark)
    out.paste(WHITE + (255,), (0, 0), white)
    out.alpha_composite(im, (pad, pad))
    return out


def place_pivot(img, im, px, py, ang, piv=(0.5, 0.5), scale=1.0, shadow=True):
    """Gira a peça em torno de um ponto (fração da imagem) e põe esse ponto em (px, py)."""
    if scale != 1.0:
        im = im.resize((max(2, int(im.width * scale)), max(2, int(im.height * scale))), Image.BICUBIC)
    vx, vy = piv[0] * im.width, piv[1] * im.height
    R = int(math.hypot(max(vx, im.width - vx), max(vy, im.height - vy))) + 4
    can = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    can.paste(im, (int(R - vx), int(R - vy)))
    if abs(ang) > 0.05:
        can = can.rotate(ang, resample=Image.BICUBIC, center=(R, R))
    if shadow:
        sh = Image.new("RGBA", can.size, (0, 0, 0, 0))
        sh.putalpha(can.getchannel("A").point(lambda v: int(v * 0.35)).filter(ImageFilter.GaussianBlur(10)))
        img.paste((30, 10, 40), (int(px - R + 14), int(py - R + 20)), sh.getchannel("A"))
    img.paste(can, (int(px - R), int(py - R)), can)


def rot_point(px, py, cx, cy, ang):
    a = math.radians(-ang)  # PIL gira no sentido anti-horário para ângulo positivo
    dx, dy = px - cx, py - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


def hop(u, p0, p1, h):
    e = ease(u)
    return lerp(p0[0], p1[0], e), lerp(p0[1], p1[1], e) - math.sin(math.pi * e) * h


def bounce(u, p0, p1, h, n=3):
    e = 1 - (1 - u) ** 2
    x, y = lerp(p0[0], p1[0], e), lerp(p0[1], p1[1], e)
    return x, y - abs(math.sin(math.pi * n * e)) * h * (1 - e) ** 1.3


def pose(t):
    return int(t * POSE) / POSE  # movimento "a 12 poses", com cara de animação


# ---------------------------------------------------------------- dados montados com as faces reais
@lru_cache(None)
def die_img(face, size=230):
    wood = piece("madeira.png").convert("RGB").resize((size, size), Image.BICUBIC)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((8, 8, size * 4 - 8, size * 4 - 8), radius=size * 4 // 5, fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    body = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    body.paste(wood, (0, 0), m)
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 0))  # luz de cima, sombra embaixo
    d = ImageDraw.Draw(sh)
    for k in range(size):
        d.line((0, k, size, k), fill=(255, 255, 255, int(40 * (1 - k / size))) if k < size / 2 else
               (60, 30, 10, int(70 * (k / size - 0.5))))
    sh.putalpha(Image.fromarray(np.minimum(np.asarray(sh.getchannel("A")), np.asarray(m))))
    body.alpha_composite(sh)
    f = piece(face).resize((int(size * 0.72), int(size * 0.72)), Image.LANCZOS)
    body.alpha_composite(f, ((size - f.width) // 2, (size - f.height) // 2))
    pad = 12
    out = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", out.size, 0)
    a.paste(m, (pad, pad))
    out.paste(INK + (255,), (0, 0), a.filter(ImageFilter.MaxFilter(7)))
    out.alpha_composite(body, (pad, pad))
    return out


FACES = ["face_arcoiris.png", "face_torii.png", "face_adaga.png"]


def die(img, t, t0, dur, p0, p1, final, seed):
    u = seg(t, t0, t0 + dur)
    if t < t0:
        return
    x, y = bounce(u, p0, p1, 320, 3)
    k = int((t - t0) * POSE)
    face = final if u >= 0.85 else FACES[(k + seed) % 3]
    rot = (1 - ease(u)) * 720 * (1 if seed % 2 else -1) + (8 if seed % 2 else -10)
    sq = 1.0 if u >= 1 else 1 + 0.12 * math.sin(k * 2.1)
    im = die_img(face)
    place_pivot(img, im.resize((int(im.width * sq), int(im.height / sq))), x, y, pose(rot) if u < 1 else rot)


# ---------------------------------------------------------------- torre
TOWER = "torre.png"
BASE = (540, 1470)
HOOK_T = (300, 125)  # fio rosa no alto da torre (coordenadas da imagem recortada)
HOOK_C = (0.16, 0.05)  # gancho do gato (fração da imagem do gato)


def tower_angle(t, amp):
    return amp * math.sin(pose(t) * 6.5) + jit(t, amp * 0.25, 7)[0]


def draw_tower(img, t, h=1050, amp=1.5, base=BASE, ang=None):
    im = outlined(TOWER, h)
    ang = tower_angle(t, amp) if ang is None else ang
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((base[0] - 300, base[1] - 30, base[0] + 300, base[1] + 34), fill=(30, 10, 40, 90))
    place_pivot(img, im, base[0], base[1], ang, (0.5, 0.985), shadow=False)
    return im, ang


def tower_point(px, py, h, ang, base=BASE):
    s = h / piece(TOWER).height
    w = piece(TOWER).width * s
    x = base[0] - w / 2 + px * s
    y = base[1] - h * 0.985 + py * s + 16
    return rot_point(x + 16 * 0, y, base[0], base[1], ang)


def crash(img, t, t0, h=1050):
    """A torre desaba: tomba, os postes voam e tudo fica espalhado no chão."""
    u = seg(t, t0, t0 + 0.55)
    if t < t0:
        draw_tower(img, t, h, amp=lerp(1.0, 7.0, seg(t, t0 - 2.4, t0)))
        return
    ang = lerp(0, 82, u ** 2)
    base = (lerp(BASE[0], BASE[0] - 120, u), BASE[1] + 60 * u)
    draw_tower(img, t, h, base=base, ang=pose(ang) if u < 1 else 82)
    for k, (dx, dy, spin) in enumerate(((420, -520, 540), (-460, -380, -400), (300, -150, 300))):
        v = seg(t, t0 + 0.05 * k, t0 + 0.9 + 0.1 * k)
        x0, y0 = BASE[0], BASE[1] - h * 0.7
        x, y = hop(v, (x0, y0), (x0 + dx, BASE[1] + 20 - k * 30), 260)
        rot = spin * ease(v) + 30 * k
        place_pivot(img, outlined("poste_rosa.png", 330), x, y, pose(rot) if v < 1 else rot)
    v = seg(t, t0 + 0.1, t0 + 1.0)  # o gatinho sai voando
    x, y = hop(v, (BASE[0] + 120, BASE[1] - h * 0.55), (BASE[0] + 330, BASE[1] - 10), 420)
    place_pivot(img, outlined("gato.png", 220), x, y, pose(-260 * ease(v)) if v < 1 else -260)


# ---------------------------------------------------------------- cubos
CUBE_COL = {"rosa": (236, 60, 120), "branco": (245, 245, 240), "azul": (40, 190, 185), "preto": (30, 30, 40)}


@lru_cache(None)
def cube_img(col, s=90):
    c = np.array(CUBE_COL[col], np.float32)
    im = Image.new("RGBA", (int(s * 1.8), int(s * 2.0)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, top = s * 0.9, s * 0.15
    A, B, C = (cx, top), (cx + s * 0.8, top + s * 0.45), (cx, top + s * 0.9)
    D = (cx - s * 0.8, top + s * 0.45)
    E, F, G = (cx + s * 0.8, top + s * 1.35), (cx, top + s * 1.8), (cx - s * 0.8, top + s * 1.35)
    sh = lambda k: tuple(int(v) for v in np.clip(c * k, 0, 255))
    d.polygon([A, B, C, D], fill=sh(1.1), outline=INK, width=4)
    d.polygon([D, C, F, G], fill=sh(0.85), outline=INK, width=4)
    d.polygon([C, B, E, F], fill=sh(0.65), outline=INK, width=4)
    return im


# ---------------------------------------------------------------- cenas
def frame_at(t):
    i = scene_of(t)
    img = anime.sky(i).copy()
    k = int(t * POSE) % 4
    if i not in (1, 8):
        img.paste(speed_lines(i, k), (0, 0), speed_lines(i, k))
    if i == 0:
        crash(img, t, 2.6)
    elif i == 1:
        petals(img, t)
        d = ImageDraw.Draw(img, "RGBA")  # fio esticado no alto com o gatinho pendurado
        ry = lambda x: 300 + 70 * math.sin(math.pi * x / W)
        pts = [(x, ry(x)) for x in range(-20, W + 40, 40)]
        d.line(pts, fill=INK, width=14)
        d.line(pts, fill=PINK, width=8)
        u = ease(seg(t, 5.7, 6.3))  # a caixa entra girando
        place_pivot(img, box_img(680), lerp(1500, 610, u), 900, pose(lerp(40, -4, u)) if u < 1 else -4)
        sw = 16 * math.sin(pose(t) * 3.2)
        place_pivot(img, outlined("gato.png", 280), 150, ry(150), sw, HOOK_C)
        petals(img, t, 18, 7)
        paste_c(img, sfx_img("猫島", 170, PINK), 800, 1260 + 6 * math.sin(t * 3), -6)
    elif i == 2:
        die(img, t, 12.6, 1.6, (-200, 500), (380, 980), "face_arcoiris.png", 0)
        die(img, t, 12.8, 1.6, (1300, 560), (720, 1040), "face_adaga.png", 1)
        circle_mark(img, (380, 980), 175, seg(t, 14.6, 15.1))
        circle_mark(img, (720, 1040), 175, seg(t, 14.8, 15.3), PINK)
        if t >= 16.2:
            g = 0.5 + 0.5 * math.sin(t * 10)
            circle_mark(img, (720, 1040), 190 + 10 * g, 1.0, RED)
    elif i == 3:
        place_pivot(img, outlined("nivel.png", 520), 540, 900, -4)
        slots = [(500, 760), (560, 730), (620, 700)]
        for kk, (col, t0) in enumerate((("rosa", 20.0), ("preto", 20.8), ("azul", 21.4))):
            if t >= t0:
                v = seg(t, t0, t0 + 0.6)
                x, y = hop(v, (300 + kk * 220, 1750), slots[kk], 420)
                place_pivot(img, cube_img(col), x, y, pose(360 * (1 - ease(v))))
                if 0 < v < 1:
                    paste_c(img, sfx_img("ポン!", 80, YELLOW), x + 90, y - 90, 8)
        for kk, (col, lab) in enumerate(((PINK, "ROSA = FIO CURTO"), (WHITE, "BRANCO = FIO MÉDIO"),
                                         (TEAL, "AZUL = FIO LONGO"))):
            t0 = 22.4 + kk * 0.8
            if t >= t0:
                paste_c(img, tag_img(lab, 42, col, INK), lerp(-400, 400 + kk * 60, ease(seg(t, t0, t0 + 0.3))),
                        1220 + kk * 120, -3 + kk * 2)
    elif i == 4:
        amp = 1.2 if t < 28.2 else lerp(4, 1.5, seg(t, 28.2, 29.5))
        if 31.0 <= t < 33.8:
            amp = 3.5
        _, ang = draw_tower(img, t, amp=amp)
        top = tower_point(205, 30, 1050, ang)
        if t >= 27.2:  # o poste cai do alto e encaixa no topo
            v = seg(t, 27.2, 28.2)
            x, y = hop(v, (top[0] + 300, -300), (top[0], top[1] - 120), 120)
            place_pivot(img, outlined("poste_rosa.png", 330), x, y, pose(lerp(200, 12, ease(v))) if v < 1 else 12 + ang)
            if 28.2 <= t < 28.8:
                paste_c(img, sfx_img("トン!", 100, YELLOW), top[0] + 160, top[1] - 200, 10)
        if 31.0 <= t < 33.8:
            bolt(img, t, (260, 420), (520, 900), 1)
            bolt(img, t, (900, 380), (620, 820), 2)
    elif i == 5:
        draw_tower(img, t, h=1600, amp=0.8, base=(560, 2050))
    elif i == 6:
        t_land = 42.7
        amp = 1.0 if t < t_land else lerp(5, 2.2, seg(t, t_land, t_land + 1.5)) + 1.4 * seg(t, 44.8, 46.0)
        _, ang = draw_tower(img, t, amp=amp)
        hx, hy = tower_point(*HOOK_T, 1050, ang)
        if t < t_land:
            v = seg(t, 41.9, t_land)
            if t >= 41.9:
                x, y = hop(v, (1300, 300), (hx, hy), 300)
                place_pivot(img, outlined("gato.png", 230), x, y, pose(lerp(-200, 0, ease(v))), HOOK_C)
        else:
            sw = 22 * math.exp(-(t - t_land) * 0.8) * math.sin((t - t_land) * 7) + 4 * math.sin(t * 3)
            place_pivot(img, outlined("gato.png", 230), hx, hy, pose(sw), HOOK_C)
            if t_land <= t < t_land + 0.5:
                sparkles(img, t, hx, hy + 100, 120, 6, 4)
    elif i == 7:
        if t < 51.7:
            crash(img, t, 48.6)
        elif t < 54.4:
            draw_tower(img, t, h=1150, amp=0.8)
            hx, hy = tower_point(*HOOK_T, 1150, 0)
            place_pivot(img, outlined("gato.png", 230), hx, hy, 6 * math.sin(t * 3), HOOK_C)
            sparkles(img, t, 540, 800, 380, 12, 8)
        else:
            vs_screen(img, t, 54.4)
    elif i == 8:
        petals(img, t, 18, 5)
        u = ease(seg(t, 58.9, 59.5))
        if u > 0:
            paste_c(img, box_img(440), lerp(-300, 310, u), 1130, -5)
    draw_elements(img, t, i)
    img = impact(img, t, 2.6)
    img = impact(img, t, 31.0, 0.1)
    img = impact(img, t, 48.6, 0.12)
    a, _ = SCENES[i]
    if i > 0 and a <= t < a + 0.12:
        img = Image.blend(img, Image.new("RGB", img.size, WHITE), 0.8 * (1 - seg(t, a, a + 0.12)))
    return img


# textos que mudam nesta versão (posições dos dados e a face especial do dado: preta com adaga)
def _ajusta_textos():
    els = []
    for e in anime.ELS:
        e = list(e)
        txt = e[2][0] if isinstance(e[2][0], str) else ""
        if txt == "= OS BAIRROS DOS POSTES":
            e[3], e[4] = 540, 1290
        if txt.startswith("TORII PRETO"):
            e[2] = ("FACE PRETA? QUEM ESCOLHE É O DA DIREITA!",) + tuple(e[2][1:])
        if txt == "PODE EMPILHAR!":
            e[3], e[4] = 300, 520
        els.append(tuple(e))
    els.append((28.2, "tag", ("UM EM CADA BAIRRO", 40, WHITE, INK), 760, 1560, 2, 31.0))
    anime.ELS[:] = els


_ajusta_textos()
anime.frame_at = frame_at  # o render do anime.py passa a usar estas cenas
anime.CUES += [(12.6, "dice", 0.8), (13.3, "cube", 0.5), (13.8, "cube", 0.4), (20.0, "pop", 0.5),
               (20.8, "pop", 0.5), (21.4, "pop", 0.5), (28.2, "wood", 0.8), (42.7, "wood", 0.5)]

if __name__ == "__main__":
    import sys
    sys.argv = [sys.argv[0]] + sys.argv[1:]
    out_names = {"anime_preview.mp4": "anime_rec_preview.mp4", "anime_limpo.mp4": "anime_rec_limpo.mp4"}
    _render = anime.render
    anime.render = lambda path, wav, subs, workers=4: _render(
        os.path.join(os.path.dirname(path), out_names.get(os.path.basename(path), os.path.basename(path))),
        wav, subs, workers)
    anime.main()
