#!/usr/bin/env python3
"""Reels 9:16 "Como alugar no site" (14/out/2026), versão em vídeo do carrossel como_alugar.py: as MESMAS telas do site
(redesenhadas das telas reais), agora animadas — a tela troca deslizando dentro do celular, a mão entra, toca o botão
(onda de toque + som) e a dica aparece embaixo. Passos: escolher → Alugar → carrinho → entrar/criar conta → finalizar
(retirada ou entrega, Pix ou cartão) → assinatura (Planos → WhatsApp com a mensagem pronta) → CTA.
Sem narração, tudo escrito na tela; duas versões: _com_trilha (gameshow) e _para_musica (só efeitos), −15,5 LUFS.

    python3 como_alugar_video.py --frame 1 4 8 12 17 21 26 30 34
    python3 como_alugar_video.py
"""
import argparse
import json
import math
import os
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, ROOT)
from motor import FPS, seg, ease, lerp, pop, encode, folha  # noqa: E402
import som  # noqa: E402
import como_alugar as ca  # noqa: E402
from estilo import (MARROM, PETROLEO, LARANJA, AMARELO, BRANCO, titulo, texto, bloco, pilula, logo, dado, peao,  # noqa
                    cola)

OUT = os.path.join(ROOT, "out")
W, H = 1080, 1920
T_PASSOS = 2.8
D_PASSO = 4.2
PASSOS = [  # (nº, rótulo, cor do selo, título, subtítulo, tela, toque (coord. da tela), dica)
    (1, "PASSO", AMARELO, "ESCOLHA O JOGO", "Busque pelo nome ou use os filtros do acervo.", "acervo", (300, 406),
     "Filtre por jogadores, categoria e complexidade"),
    (2, "PASSO", AMARELO, "TOQUE EM “ALUGAR”", "Na página do jogo você vê jogadores, tempo e preço.", "jogo",
     (250, 590), "R$ 15, 30, 45 ou 60 por 5 dias"),
    (3, "PASSO", AMARELO, "MONTE SEU CARRINHO", "Quanto mais jogos, mais dias pra todos.", "carrinho", (285, 625),
     "3 jogos = 7 dias · 5 = 10 dias · 7 = 15 dias"),
    (4, "PASSO", AMARELO, "ENTRE NA SUA CONTA", "Primeira vez? Toque em “Criar conta”.", "login", (265, 560),
     "Os dados e o endereço só na primeira vez"),
    (5, "PASSO", AMARELO, "FINALIZE O PEDIDO", None, None, None, None),
    (1, "ASSINATURA", LARANJA, "QUER ASSINAR?", "No menu, toque em “Planos” e escolha o seu.", "planos", (265, 493),
     "Trocas sem limite no mês"),
    (2, "ASSINATURA", LARANJA, "ABRE O WHATSAPP", "A mensagem já vem pronta: é só enviar.", "zap", (354, 452),
     "Silver R$ 49 · Gold R$ 89 · Platinum R$ 139"),
]
T_FINAL = T_PASSOS + len(PASSOS) * D_PASSO
DUR = T_FINAL + 4.0
FONE_CY = 1075
TOQUE = 1.75  # segundos depois do início do passo


@lru_cache(None)
def fundo():
    img = Image.new("RGBA", (W, H), PETROLEO + (255,))
    d = ImageDraw.Draw(img)
    for y in range(30, H, 54):
        for x in range(30 + (27 if (y // 54) % 2 else 0), W, 54):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(40, 141, 168))
    return img


def trilha(img, t, y0=1840):
    """Trilha amarela tracejada andando (o tracejado corre da esquerda pra direita)."""
    d = ImageDraw.Draw(img)
    fase = (t * 160) % 56
    pts = [(x, y0 + 22 * math.sin(x / W * math.pi * 2 + 0.6)) for x in range(-60, W + 61, 4)]
    acc = -fase
    for (x0, y0_), (x1, y1) in zip(pts, pts[1:]):
        acc += math.hypot(x1 - x0, y1 - y0_)
        if (acc % 56) < 34:
            d.line((x0, y0_, x1, y1), fill=AMARELO, width=12)


@lru_cache(None)
def tela(nome):
    return {"acervo": ca.tela_acervo, "jogo": ca.tela_jogo, "carrinho": ca.tela_carrinho, "login": ca.tela_login,
            "planos": ca.tela_planos, "zap": ca.tela_zap}[nome]()


def celular_com(scr_a, scr_b, u):
    """Celular com a tela A saindo pra esquerda e a B entrando pela direita (u = 0 → 1)."""
    if scr_a is None or u >= 1:
        return ca.celular(scr_b)
    sc = Image.new("RGBA", scr_b.size, (255, 255, 255, 255))
    dx = int(ease(u) * scr_b.width)
    sc.alpha_composite(scr_a, (-dx, 0))
    sc.alpha_composite(scr_b, (scr_b.width - dx, 0))
    return ca.celular(sc)


@lru_cache(None)
def mao():
    """A mão da tela de toque (a mesma do carrossel, sem as ondas, que aqui são animadas)."""
    im = Image.new("RGBA", (260, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pele, ow = (255, 214, 170), 7
    d.rounded_rectangle((40, 40, 96, 230), radius=28, fill=pele, outline=MARROM, width=ow)
    d.rounded_rectangle((60, 150, 230, 320), radius=60, fill=pele, outline=MARROM, width=ow)
    d.rounded_rectangle((47, 140, 89, 225), radius=20, fill=pele)
    for x in (110, 150, 190):
        d.rounded_rectangle((x - 6, 128, x + 34, 210), radius=20, fill=pele, outline=MARROM, width=ow)
    d.rectangle((70, 196, 222, 240), fill=pele)
    d.arc((54, 46, 82, 74), 200, 340, fill=(240, 180, 140), width=5)
    return im


def onda(img, x, y, u):
    if not 0 < u < 1:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(2):
        v = u - k * 0.25
        if 0 < v < 1:
            r = 20 + 90 * v
            d.ellipse((x - r, y - r, x + r, y + r), outline=BRANCO + (int(230 * (1 - v)),), width=9)
    img.alpha_composite(lay)


@lru_cache(None)
def selo(n, rot, cor):
    return ca.selo(n, cor, MARROM if cor == AMARELO else BRANCO, rot)


@lru_cache(None)
def tit(txt):
    return titulo(txt, 84, BRANCO, larg_max=560)


@lru_cache(None)
def sub(txt):
    return texto(txt, 36, BRANCO, 700, larg_max=600)


@lru_cache(None)
def dica(txt):
    return pilula(txt, 34, AMARELO, MARROM, pad=(30, 12))


def cabecalho(img, t, t0, n, rot, cor, ti, su):
    cola(img, selo(n, rot, cor), 135, 175, 0, pop(t, t0 + 0.05))
    a = tit(ti)
    cola(img, a, 590, 85 + a.height / 2, -2, pop(t, t0 + 0.15))
    if su:
        s = sub(su)
        cola(img, s, 590, 95 + a.height + s.height / 2, 0, 1, min(1, seg(t, t0 + 0.35, t0 + 0.6)))


def passo(img, t, k):
    n, rot, cor, ti, su, nome, toque, dc = PASSOS[k]
    t0 = T_PASSOS + k * D_PASSO
    u = t - t0
    cabecalho(img, t, t0, n, rot, cor, ti, su)
    if nome is None:
        finalize(img, t, t0)
        return
    ant = PASSOS[k - 1][5] if k > 0 else None
    entra = ease(seg(u, 0, 0.45)) if ant is None else 1.0
    fone = celular_com(tela(ant) if ant else None, tela(nome), seg(u, 0.0, 0.45) if ant else 1.0)
    fy = FONE_CY + (1 - entra) * 1200
    cola(img, fone, W / 2, fy)
    fx0, fy0 = W / 2 - fone.width / 2, fy - fone.height / 2
    tx, ty = fx0 + 22 + ca.u(toque[0]), fy0 + 34 + ca.u(toque[1])
    # mão: entra pela direita de baixo, toca, fica
    v = ease(seg(u, 0.75, TOQUE - 0.1))
    aperta = 1 - 0.1 * math.sin(math.pi * seg(u, TOQUE - 0.05, TOQUE + 0.17))
    if u > 0.75 and u < D_PASSO - 0.15:
        hx, hy = lerp(W + 200, tx, v), lerp(H + 150, ty, v)
        e = 0.78 * aperta
        cola(img, mao(), hx + (130 - 60) * e, hy + (165 - 60) * e, 12, e)
    onda(img, tx, ty, seg(u, TOQUE, TOQUE + 0.6))
    if dc and u > TOQUE + 0.25:
        cola(img, dica(dc), W / 2, 1745, -1.5, pop(t, t0 + TOQUE + 0.25))


def finalize(img, t, t0):
    for k, (ti, desc, cor, ct) in enumerate((("RETIRE EM MAUÁ", "é só passar na loja", AMARELO, MARROM),
                                             ("OU RECEBA EM CASA", "o frete é combinado no pedido", LARANJA, BRANCO))):
        b = _cartao(ti, desc, cor, ct)
        q = ease(seg(t, t0 + 0.3 + 0.3 * k, t0 + 0.75 + 0.3 * k))
        cola(img, b, lerp((-700, W + 700)[k], W / 2 + (-20, 25)[k], q), 640 + k * 290, (-1.5, 1.2)[k])
    cola(img, pilula("PAGUE NO PIX OU NO CARTÃO", 52, BRANCO, MARROM, pad=(36, 16), fonte_titulo=True), W / 2, 1210,
         -2, pop(t, t0 + 1.3))
    cola(img, titulo("E BORA JOGAR!", 110, AMARELO), W / 2, 1420, 2, pop(t, t0 + 1.9))
    q = ease(seg(t, t0 + 2.1, t0 + 2.6))
    cola(img, peao(170, LARANJA), lerp(-150, 170, q), 1610, -10)
    cola(img, dado(130, 6, BRANCO), lerp(W + 150, 910, q), 1620, 12 + 200 * (1 - q))


@lru_cache(None)
def _cartao(ti, desc, cor, ct):
    b = bloco(840, 230, cor, raio=36, ow=8, sombra=12)
    cola(b, titulo(ti, 70, BRANCO if cor == AMARELO else AMARELO, sw=6, sombra=6), 420, 85)
    cola(b, texto(desc, 38, ct, 800), 420, 170)
    return b


def gancho(img, t):
    cola(img, pilula("PASSO A PASSO", 44, AMARELO, MARROM, pad=(30, 12), fonte_titulo=True), W / 2, 330, 3,
         pop(t, 0.05))
    cola(img, titulo("COMO ALUGAR\nJOGOS NO SITE?", 130, BRANCO, larg_max=960), W / 2, 560, -2, pop(t, 0.2))
    cola(img, texto("Do celular, em poucos toques.", 50, BRANCO, 800), W / 2, 790, 0, 1, min(1, seg(t, 0.6, 0.9)))
    q = ease(seg(t, 0.9, 1.8))
    fone = ca.celular(tela("acervo"))
    cola(img, fone, W / 2 + 60, lerp(H + 700, 1500, q), -6)


def final(img, t):
    u = t - T_FINAL
    cola(img, logo(420), W / 2, 330, -2, pop(t, T_FINAL))
    cola(img, titulo("PRONTO!\nAGORA É A\nSUA VEZ!", 140, BRANCO, larg_max=960), W / 2, 730, -2, pop(t, T_FINAL + 0.2))
    itens = [(0.6, pilula("ALUGUE PELO LINK NA BIO", 58, AMARELO, MARROM, pad=(40, 18), fonte_titulo=True), 1080),
             (0.8, texto("suavez.acervodejogos.com.br", 46, BRANCO, 800), 1215),
             (0.95, texto("@suavez_bg", 52, AMARELO, 900), 1300),
             (1.1, pilula("RETIRE EM MAUÁ OU RECEBA EM CASA", 38, BRANCO, MARROM, pad=(30, 12)), 1420)]
    for t0, im, y in itens:
        if u >= t0:
            cola(img, im, W / 2, y, 0, pop(t, T_FINAL + t0))
    q = ease(seg(t, T_FINAL + 1.3, T_FINAL + 1.8))
    cola(img, dado(140, 5, AMARELO), lerp(-150, 200, q), 1620, -12 + 200 * (1 - q))
    cola(img, peao(180, LARANJA), lerp(W + 150, 880, q), 1610, 10)


def frame(t):
    img = fundo().copy()
    trilha(img, t)
    if t < T_PASSOS:
        gancho(img, t)
    elif t < T_FINAL:
        passo(img, t, min(len(PASSOS) - 1, int((t - T_PASSOS) // D_PASSO)))
    else:
        final(img, t)
    if t < T_FINAL:
        cola(img, logo(150), W - 95, 80, 0)
    return img.convert("RGB")


def render_frame(fi):
    return frame(fi / FPS).tobytes()


def cues():
    c = [(0.05, "pop", 0.4), (0.2, "chime", 0.4), (0.9, "whoosh", 0.4)]
    for k, p in enumerate(PASSOS):
        t0 = T_PASSOS + k * D_PASSO
        c += [(t0, "whoosh", 0.45), (t0 + 0.05, "pop", 0.35)]
        if p[5]:
            c += [(t0 + TOQUE, "tick", 0.7), (t0 + TOQUE + 0.25, "ding", 0.35)]
        else:
            c += [(t0 + 0.3, "whoosh", 0.35), (t0 + 0.6, "whoosh", 0.35), (t0 + 1.3, "pop", 0.4),
                  (t0 + 1.9, "boing", 0.35)]
    c += [(T_FINAL, "reveal", 0.6), (T_FINAL + 0.6, "pop", 0.4), (T_FINAL + 1.3, "ding", 0.45)]
    return c


def loudness(src, dst, alvo=-15.5):
    """loudnorm LINEAR em 2 passadas (o mesmo acabamento dos outros vídeos sem narração)."""
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    r = subprocess.run([ff, "-hide_banner", "-i", src, "-af", f"loudnorm=I={alvo}:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    af = (f"loudnorm=I={alvo}:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-c:v", "copy", "-af", af, "-ar", "44100",
                    "-c:a", "aac", "-b:a", "192k", dst], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        folha([frame(x) for x in a.frame], os.path.join(OUT, "frames.jpg"))
        return
    n = int(DUR * FPS)
    for nome, musica in (("com_trilha", "gameshow"), ("para_musica", None)):
        wav = os.path.join(OUT, f"como_alugar_{nome}.wav")
        som.build(wav, DUR, cues(), musica=musica, fx_ganho=0.5, musica_ganho=0.25)
        mp4 = os.path.join(OUT, f"como_alugar_{nome}.mp4")
        encode(mp4, render_frame, list(range(n)), wav)
        loudness(mp4, mp4.replace(".mp4", "_final.mp4"))


if __name__ == "__main__":
    main()
