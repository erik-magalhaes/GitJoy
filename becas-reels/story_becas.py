#!/usr/bin/env python3
"""STORY em vídeo da TARDE DE JOGOS NO BECAS (5/nov/2026). Pedido dele: "vamos seguir com o visual dos guarda-chuvinhas;
queria um vídeo para o Stories, porque vou PROMOVER o Stories; pode ser narrado".

~16 s (anúncio de Stories: curto, a mensagem inteira nos primeiros segundos). Guarda-chuvinhas balançando no alto (os de
`tarde.py`) e a ideia nova de `promo/becas_chuva.py`: um guarda-chuva grande SEGURA as coisas pelo cabo e tudo balança
junto como pêndulo (polaroide com as cenas REAIS deles jogando, etiqueta de preço). Área segura do Stories patrocinado:
nada importante acima de y≈300 (barra/perfil) nem abaixo de y≈1560 (botão "Saiba mais"/"Enviar mensagem").

Narração: 4 falas curtas gravadas por ELES (gravador `gravador/Gravar_narracao_Story.html`, arquivos
`becasstory_narracao_NN`). Enquanto não chegam, sai a versão só com trilha (texto na tela carrega a mensagem).
Ao receber: pôr os .webm em `narracao_story/raw/`, tratar (cadeia de voz do CLAUDE.md, 44,1 kHz) em
`narracao_story/frase_NN.wav` e rodar de novo: cada cena estica para caber a fala e entra a legenda.

    /usr/bin/python3 story_becas.py --frame 1 5 9 13 15.5   # out/frames_story.jpg
    /usr/bin/python3 story_becas.py                         # out/story_becas_{com_som,para_musica}_final.mp4
"""
import math
import os
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA, ease, out_back

from motor import FPS  # noqa: E402
OUT = T.OUT
NARR = os.path.join(T.ROOT, "narracao_story")
FALAS = [
    "Bora jogar num café? Sexta, dia 20, feriado, tem Tarde de Jogos no Becas!",
    "A gente leva os jogos e ensina tudo na mesa. Não precisa saber jogar nada!",
    "Trinta reais, e quinze viram consumação no café.",
    "Das 13 às 19h. Garante a sua mesa pelo WhatsApp!",
]
DUR_PADRAO = [3.6, 4.4, 3.4, 4.6]  # sem narração
CLIPS = [("canvas", 1.4), ("sushi", 1.0), ("unlock", 1.0), ("critter", 0.6)]  # (clipe, início no bruto)
DC = 1.15  # cada cena real na polaroide


def voz(k):
    p = os.path.join(NARR, f"frase_{k + 1:02d}.wav")
    return p if os.path.exists(p) else None


def dur_wav(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


TEM_VOZ = all(voz(k) for k in range(len(FALAS)))
LEAD, TAIL = 0.25, 0.35
DURS = [max(DUR_PADRAO[k] * 0.8, LEAD + dur_wav(voz(k)) + TAIL) for k in range(len(FALAS))] if TEM_VOZ else DUR_PADRAO
DURS[-1] += 1.2 if TEM_VOZ else 0  # o CTA fica um pouco mais na tela
INI = [0.0]
for d_ in DURS:
    INI.append(INI[-1] + d_)
DUR = INI[-1]
TRANS = 0.28


# ---------------------------------------------------------------- pêndulo: guarda-chuva grande segurando algo
@lru_cache(None)
def sprite_pendulo(w_umb, cor, fio, obj_key, gap=34):
    """Fio do pivô até o guarda-chuva + guarda-chuva + argola + objeto. Pivô no CENTRO da imagem (para girar)."""
    umb = TB.guarda_chuva(w_umb, cor, 3)
    obj = OBJ[obj_key]() if obj_key else None
    ow, oh = (obj.width, obj.height) if obj else (0, 0)
    hx_rel = -0.055 * w_umb  # gancho do cabo em relação ao eixo
    h_umb_hook = 14 + 0.75 * w_umb + 2
    alt = fio + h_umb_hook + gap + oh + 10
    lw = int(max(umb.width, ow) + 40)
    S_ = int(2 * max(alt, lw) + 20)
    im = Image.new("RGBA", (S_, S_), (0, 0, 0, 0))
    cx, cy = S_ / 2, S_ / 2
    d = ImageDraw.Draw(im)
    d.line([(cx, cy), (cx, cy + fio)], fill=(150, 120, 100), width=4)
    im.alpha_composite(umb, (int(cx - umb.width / 2), int(cy + fio - 6)))
    if obj:
        hx, hy = cx + hx_rel, cy + fio - 6 + h_umb_hook
        top = hy + gap
        d.line([(hx, hy - 4), (hx, top + 14)], fill=MAR, width=4)
        im.alpha_composite(obj, (int(hx - ow / 2), int(top)))
        d.ellipse((hx - 9, top + 4, hx + 9, top + 22), fill=BR, outline=MAR, width=4)
    return im


def pendulo(img, x, ang, w_umb, cor, fio, obj_key, extra=None):
    """Desenha o pêndulo com pivô em (x, 0) girado `ang` graus. `extra(im)` desenha por cima do objeto (vídeo)."""
    sp = sprite_pendulo(w_umb, cor, fio, obj_key)
    if extra:
        sp = sp.copy()
        extra(sp)
    r = sp.rotate(ang, resample=Image.BICUBIC)
    img.alpha_composite(r, (int(x - r.width / 2), int(-r.height / 2)))


def balanco(u, amp=4.0, per=2.3, fase=0.0):
    """Cai do teto com quique e fica num vaivém suave."""
    amort = 1 + 3 * math.exp(-u * 2.2)
    return amp * amort * math.sin(2 * math.pi * u / per + fase)


# ---------------------------------------------------------------- objetos pendurados
POL_W, POL_H, FOTO_W, FOTO_H = 600, 760, 540, 640


def polaroide():
    im = Image.new("RGBA", (POL_W + 14, POL_H + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, POL_W + 13, POL_H + 13), fill=MAR + (110,))
    im = im.filter(ImageFilter.GaussianBlur(5))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, POL_W, POL_H), fill=(252, 250, 244), outline=(205, 195, 180), width=2)
    from PIL import ImageFont
    mao = ImageFont.truetype(os.path.join(T.REPO, "taco-reels", "assets", "fonts", "PatrickHand-Regular.ttf"), 50)
    d.text((POL_W / 2, POL_H - 52), "jogando de verdade!", font=mao, fill=MAR, anchor="mm", stroke_width=1,
           stroke_fill=MAR)
    return im


def etiqueta():
    return E.bloco(600, 430, AMA, raio=34, ow=7, sombra=11).copy()


OBJ = {"pol": polaroide, "etq": etiqueta}


def foto_clip(t):
    """Quadro da cena real (troca a cada DC) recortado para a janela da polaroide."""
    k = int(t // DC) % len(CLIPS)
    nome, t0 = CLIPS[k]
    q = K.quadro_clip(nome, t0, DC, 1.0, t % DC)
    q = q.crop((0, 300, 1080, 300 + int(1080 * FOTO_H / FOTO_W)))
    return q.resize((FOTO_W, FOTO_H), Image.LANCZOS)


def desenha_foto(t):
    def f(sp):
        S_ = sp.width
        cx, cy = S_ / 2, S_ / 2
        w_umb, fio = 300, 300
        hx = cx - 0.055 * w_umb
        top = cy + fio - 6 + 14 + 0.75 * w_umb + 2 + 34
        x0, y0 = int(hx - POL_W / 2 + (POL_W - FOTO_W) / 2), int(top + (POL_W - FOTO_W) / 2)
        sp.paste(foto_clip(t).convert("RGBA"), (x0, y0))
    return f


def escreve_etiqueta(sp):
    S_ = sp.width
    cx, cy = S_ / 2, S_ / 2
    w_umb, fio = 340, 240
    hx = cx - 0.055 * w_umb
    top = cy + fio - 6 + 14 + 0.75 * w_umb + 2 + 34
    x0 = hx - 300
    d = ImageDraw.Draw(sp)
    d.text((x0 + 300, top + 125), "R$ 30", font=E.lilita(190), fill=LAR, anchor="mm", stroke_width=7, stroke_fill=MAR)
    d.text((x0 + 300, top + 250), "por pessoa", font=E.fig(46, 900), fill=MAR, anchor="mm")
    d.text((x0 + 300, top + 315), "R$ 15 viram", font=E.fig(46, 900), fill=PET, anchor="mm")
    d.text((x0 + 300, top + 370), "consumação no café", font=E.fig(46, 900), fill=PET, anchor="mm")


# ---------------------------------------------------------------- cenas (conteúdo entre y 300 e 1560)
def poe(img, im, x, y, t, t0, rot=0.0, d=0.35):
    T.poe(img, im, x, y, t, t0, rot, d)


def c_gancho(img, t):
    poe(img, E.pilula("SUA VEZ  ×  BECAS CAFÉ", 40, BR, MAR, fonte_titulo=True), W / 2, 560, t, 0.25, -1.5)
    poe(img, T.titulo("BORA JOGAR\nNUM CAFÉ?", 160, LAR), W / 2, 830, t, 0.0, -3)
    poe(img, T.titulo("TARDE\nDE JOGOS", 130, PET), W / 2, 1180, t, 0.9, 2)
    poe(img, E.pilula("SEXTA, 20/11 · FERIADO", 46, AMA, MAR, fonte_titulo=True), W / 2, 1430, t, 1.5, 2)


def c_jogos(img, t):
    ang = balanco(t, 3.5, 2.4)
    pendulo(img, W / 2 + 10, ang, 300, ROSA, 300, "pol", desenha_foto(t))
    poe(img, E.pilula("A GENTE LEVA OS JOGOS", 46, PET, BR, fonte_titulo=True), W / 2, 1440, t, 0.4, -1.5)
    poe(img, E.pilula("E ENSINA TUDO NA MESA!", 46, LAR, BR, fonte_titulo=True), W / 2, 1530, t, 0.9, 1.5)


def c_preco(img, t):
    ang = balanco(t, 4.0, 2.2, 0.5)
    pendulo(img, W / 2, ang, 340, PET, 240, "etq", escreve_etiqueta)
    poe(img, T.titulo("METADE VIRA\nCAFÉ!", 110, ROSA), W / 2, 1380, t, 0.9, -2)


def c_cta(img, t):
    poe(img, T.logo(250), W / 2, 420, t, 0.0)
    poe(img, T.titulo("TARDE DE JOGOS\nNO BECAS CAFÉ", 100, LAR), W / 2, 660, t, 0.25, -2)
    poe(img, TB.selo_data(42), W / 2, 830, t, 0.6, 2)
    poe(img, TB.selo_endereco(32), W / 2, 912, t, 0.8, -1)
    poe(img, T.inscricao(), W / 2, 1120, t, 1.0, 0)
    poe(img, E.pilula("Manda pra quem vai com você!", 40, AMA, MAR), W / 2, 1360, t, 1.6, -1.5)


CENAS = [c_gancho, c_jogos, c_preco, c_cta]


# ---------------------------------------------------------------- legenda (só com narração)
@lru_cache(None)
def palavras():
    import json
    p = os.path.join(NARR, "palavras.json")
    return json.load(open(p)) if os.path.exists(p) else None


def legenda(img, k, u):
    """Fala k: mostra o pedaço (até ~26 letras) que está sendo dito; tempo proporcional às letras."""
    txt = FALAS[k]
    pal = txt.split()
    blocos, cur = [], ""
    for p in pal:
        if len(cur) + len(p) + 1 > 26 and cur:
            blocos.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    blocos.append(cur)
    d_fala = dur_wav(voz(k))
    v = (u - LEAD) / d_fala
    if v < 0 or v > 1.02:
        return
    tot = sum(len(b) for b in blocos)
    acc = 0
    for b in blocos:
        acc += len(b)
        if v <= acc / tot:
            break
    f = E.fig(50, 900)
    dd = ImageDraw.Draw(img)
    tw = dd.textlength(b, font=f)
    y = 1600 - 330  # acima do botão do anúncio, abaixo do conteúdo principal
    y = 300 if CENAS[k] is c_cta else y
    dd.rounded_rectangle((W / 2 - tw / 2 - 26, y - 40, W / 2 + tw / 2 + 26, y + 40), 22, fill=MAR + (225,))
    dd.text((W / 2, y), b, font=f, fill=BR, anchor="mm")


def quadro(t):
    k = max(i for i in range(len(CENAS)) if INI[i] <= t) if t < DUR else len(CENAS) - 1
    f, d = CENAS[k], DURS[k]
    u = t - INI[k]
    img = T.fundo().copy()
    cena = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f(cena, u)
    if k < len(CENAS) - 1 and u > d - TRANS:
        q = ease((u - (d - TRANS)) / TRANS)
        img.alpha_composite(cena, (int(-q * W), 0))
    elif k > 0 and u < TRANS:
        q = ease(u / TRANS)
        img.alpha_composite(cena, (int((1 - q) * W), 0))
    else:
        img.alpha_composite(cena)
    T.guarda_chuvas(img, t)
    if TEM_VOZ and CENAS[k] is not c_cta:
        legenda(img, k, u)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


# ---------------------------------------------------------------- som
def le_voz(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(1)
    return a


def audio():
    ev = [(0.08 * k + 0.4, S.sino() * 0.25, 0.25) for k in range(len(T.CHUVAS))]
    ev += [(INI[k] + 0.02, S.sopro(0.35), 0.35) for k in range(1, len(CENAS))]
    ev += [(INI[1] + DC * j, S.obturador(), 0.35) for j in range(int(DURS[1] / DC) + 1)]
    ev += [(INI[2] + 0.3, S.louca(), 0.5), (INI[3] + 0.6, S.sino(), 0.5)]
    mus = S.musica_cafe(DUR + 0.5)
    com = os.path.join(OUT, "story_becas_com.wav")
    sem = os.path.join(OUT, "story_becas_sem.wav")
    if TEM_VOZ:
        n = int(DUR * S.SR)
        vz = np.zeros(n)
        for k in range(len(FALAS)):
            S.add(vz, le_voz(voz(k)), INI[k] + LEAD, 1.0)
        env = np.convolve((np.abs(vz) > 0.02).astype(float), np.ones(int(0.25 * S.SR)) / int(0.25 * S.SR), "same")
        mus = mus[:n] * (1 - 0.65 * np.clip(env * 3, 0, 1))  # trilha abaixa quando tem voz
        ev += [(0.0, vz, 2.2)]
    S.grava(com, DUR, ev, mus, musica_ganho=0.32 if TEM_VOZ else 0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    return com, sem


def main():
    os.makedirs(OUT, exist_ok=True)
    K.prepara([(n, t0, DC, 1.0) for n, t0 in CLIPS])
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, "frames_story.jpg"))
        print("ok", round(DUR, 2), "voz" if TEM_VOZ else "sem voz")
        return
    com, sem = audio()
    K.entrega("story_becas", DUR, render, com, sem)
    print("ok", round(DUR, 2))


if __name__ == "__main__":
    main()
