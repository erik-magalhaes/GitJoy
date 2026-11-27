#!/usr/bin/env python3
"""BLACK FRIDAY da Sua Vez (27 a 29/nov/2026): "ALUGUE 3 JOGOS, O MAIS BARATO É POR NOSSA CONTA" (promoção do site:
Item Mais Barato, mínimo 3 itens, não combina com cupom; válida até domingo 29/11, 23:59). Sem preço na arte (o site
novo tem 5 ou 7 dias com preços diferentes). Visual: preto com brilho dourado e confete, identidade da Jéssica (Lilita/
Figtree, contorno marrom, sombra sólida), 3 caixas com a menor ganhando o carimbo "GRÁTIS".

    /usr/bin/python3 black_friday.py            # out/black_friday/: stories + post + carrossel
    /usr/bin/python3 black_friday.py --reels    # out/black_friday/bf_{com_som,para_musica}_final.mp4 (+ --stories)
"""
import math
import os
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "assinatura-reels"))
import estilo as E  # noqa: E402

AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
OUT = os.path.join(ROOT, "out", "black_friday")
W = 1080
PRETO = (16, 14, 18)
OURO = (255, 199, 31)
VERMELHO = (226, 52, 52)
BRANCO = (255, 255, 255)
CAIXAS = [os.path.join(AC, f) for f in ("clank_catacombs.png", "king_of_tokyo.png", "hive.png")]  # a última = a "grátis"
LINK = "suavez.acervodejogos.com.br"


@lru_cache(None)
def _fundo(h, semente):
    img = Image.new("RGB", (W, h), PRETO)
    a = np.zeros((h, W), np.float32)
    yy, xx = np.mgrid[0:h, 0:W].astype(np.float32)
    for cx, cy, r, k in [(W * 0.15, h * 0.12, 520, 0.35), (W * 0.9, h * 0.45, 600, 0.25), (W * 0.3, h * 0.92, 560, 0.3)]:
        a += k * np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r))
    luz = np.clip(a, 0, 1)[..., None] * np.array([95, 66, 10], np.float32)
    img = Image.fromarray(np.clip(np.asarray(img, np.float32) + luz, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(semente)
    for _ in range(70):  # confete dourado e laranja, mais nas bordas
        x = rnd.choice([rnd.randint(0, 170), rnd.randint(W - 170, W), rnd.randint(0, W)])
        y = rnd.randint(0, h)
        cor = rnd.choice([OURO, E.LARANJA, (255, 236, 160), BRANCO])
        s = rnd.randint(7, 15)
        ang = rnd.uniform(0, math.pi)
        pts = [(x + s * math.cos(ang + k * math.pi / 2) * (1 if k % 2 == 0 else 0.45),
                y + s * math.sin(ang + k * math.pi / 2) * (1 if k % 2 == 0 else 0.45)) for k in range(4)]
        d.polygon(pts, fill=cor)
    return img


def fundo(h, semente=1):
    return _fundo(h, semente).copy()


def centro(img, im, cx, y):
    img.alpha_composite(im, (int(cx - im.width / 2), int(y)))


def faixa_bf(w=900, s=118):
    """Faixa preta e dourada "BLACK FRIDAY" girada, cara de fita de liquidação."""
    t = E.titulo("BLACK FRIDAY", s, cor=OURO, contorno=(0, 0, 0), sw=8, sombra=0)
    b = Image.new("RGBA", (max(w, t.width + 80), t.height + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(b)
    d.rectangle((0, 0, b.width, b.height), fill=(0, 0, 0, 255))
    for x in range(-60, b.width + 60, 60):  # listras de fita nas bordas
        d.polygon([(x, 0), (x + 30, 0), (x + 10, 14), (x - 20, 14)], fill=OURO)
        d.polygon([(x, b.height - 14), (x + 30, b.height - 14), (x + 10, b.height), (x - 20, b.height)], fill=OURO)
    b.alpha_composite(t, ((b.width - t.width) // 2, 25))
    return b.rotate(-4, expand=True, resample=Image.BICUBIC)


def carimbo(txt="GRÁTIS", s=64, ang=14):
    f = E.lilita(s)
    tw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=f)
    w, h = int(tw + 60), int(s * 1.45)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), radius=18, fill=VERMELHO, outline=BRANCO, width=7)
    d.text((10 + w / 2, 10 + h / 2 + 3), txt, font=f, fill=BRANCO, anchor="mm")
    return im.rotate(ang, expand=True, resample=Image.BICUBIC)


def tres_caixas(h=330, gratis=True, k_gratis=1.0):
    """As 3 caixas lado a lado; a menor (a mais barata) com o carimbo GRÁTIS."""
    ims = [E.jogo(p, h, int(h * 1.05)) for p in CAIXAS]
    ims[2] = E.jogo(CAIXAS[2], int(h * 0.82), int(h * 0.9))
    gap = 18
    w = sum(i.width for i in ims) + 2 * gap
    out = Image.new("RGBA", (w + 60, h + 160), (0, 0, 0, 0))
    x = 30
    for i, im in enumerate(ims):
        y = 60 + (h - im.height)
        out.alpha_composite(im.rotate([3, -2, -5][i], expand=True, resample=Image.BICUBIC), (x, y))
        x += im.width + gap
    if gratis and k_gratis > 0.02:
        c = carimbo()
        c = c.resize((max(2, int(c.width * k_gratis)), max(2, int(c.height * k_gratis))), Image.BICUBIC)
        cx = 30 + ims[0].width + ims[1].width + 2 * gap + ims[2].width / 2
        out.alpha_composite(c, (int(cx - c.width / 2), int(60 + h - ims[2].height - c.height * 0.55)))
    return out


def seta_link(img, y, txt="garanta os seus aqui:"):
    t = E.texto(txt, 44, cor=BRANCO, peso=900)
    centro(img, t, W / 2, y)
    d = ImageDraw.Draw(img)
    cx, yy = W // 2, y + t.height + 8
    d.polygon([(cx - 38, yy), (cx + 38, yy), (cx, yy + 52)], fill=OURO, outline=(0, 0, 0), width=5)
    return yy + 52


def logo_topo(img, y=60, w=210):
    lg = E.logo(w)
    centro(img, lg, W / 2, y)
    return y + lg.height


# ------------------------------------------------------------------------------------------------ STORIES
def story_promo():
    H = 1920
    img = fundo(H, 1)
    y = logo_topo(img, 150, 220) + 30
    fb = faixa_bf()
    centro(img, fb, W / 2, y)
    y += fb.height - 10
    t = E.titulo("ALUGUE 3 JOGOS,\nO MAIS BARATO\nÉ POR NOSSA CONTA!", 92, cor=BRANCO, larg_max=1000)
    centro(img, t, W / 2, y)
    y += t.height - 10
    cx = tres_caixas(280)
    centro(img, cx, W / 2, y - 40)
    # espaço do adesivo de link: y ≈ 1350–1580 (livre)
    seta_link(img, 1240)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11", 44, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, 1610)
    return img


def story_como():
    H = 1920
    img = fundo(H, 2)
    y = logo_topo(img, 150, 200) + 30
    t = E.titulo("COMO FUNCIONA?", 100, cor=OURO, larg_max=980)
    centro(img, t, W / 2, y)
    y += t.height + 10
    passos = [("1", "Escolha 3 jogos ou mais no site", E.LARANJA),
              ("2", "No carrinho, o mais barato sai de graça", E.PETROLEO),
              ("3", "Retire em Mauá ou receba em casa", (120, 70, 160))]
    for n, txt, cor in passos:
        card = E.bloco(900, 170, (255, 248, 232), raio=34, ow=7, sombra=10)
        d = ImageDraw.Draw(card)
        d.ellipse((30, 25, 150, 145), fill=cor, outline=E.MARROM, width=6)
        d.text((90, 88), n, font=E.lilita(80), fill=BRANCO, anchor="mm")
        tx = E.texto(txt, 42, cor=E.MARROM, peso=800, larg_max=680, alinha="lm")
        card.alpha_composite(tx, (180, (170 - tx.height) // 2))
        centro(img, card, W / 2, y)
        y += 200
    cx = tres_caixas(190)
    centro(img, cx, W / 2, y - 90)
    seta_link(img, 1290, "corre pro site:")
    pl = E.pilula("BLACK FRIDAY · SÓ ATÉ DOMINGO, 29/11", 36, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, 1610)
    return img


def story_ultimo():
    H = 1920
    img = fundo(H, 3)
    y = logo_topo(img, 150, 200) + 40
    t = E.titulo("ÚLTIMO DIA!", 150, cor=OURO, larg_max=980)
    centro(img, t, W / 2, y)
    y += t.height
    t2 = E.titulo("BLACK FRIDAY ACABA HOJE,\nÀS 23:59", 66, cor=BRANCO, larg_max=980)
    centro(img, t2, W / 2, y)
    y += t2.height + 10
    t3 = E.texto("3 jogos no carrinho = o mais barato sai de graça", 40, cor=BRANCO, peso=800, larg_max=880)
    centro(img, t3, W / 2, y)
    cx = tres_caixas(230)
    centro(img, cx, W / 2, y + t3.height - 20)
    seta_link(img, 1240)
    return img


# ------------------------------------------------------------------------------------------------ POST / CARROSSEL
def post():
    H = 1350
    img = fundo(H, 4)
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 36, 36))
    fb = faixa_bf(820, 108)
    centro(img, fb, W / 2 - 40, 60)
    t = E.titulo("ALUGUE 3 JOGOS,\nO MAIS BARATO\nÉ POR NOSSA CONTA!", 88, cor=BRANCO, larg_max=1000)
    centro(img, t, W / 2, 60 + fb.height - 10)
    cx = tres_caixas(270)
    centro(img, cx, W / 2, 60 + fb.height + t.height - 60)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11 · LINK NA BIO", 38, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, H - pl.height - 50)
    return img


def post_como():
    H = 1350
    img = fundo(H, 6)
    lg = E.logo(170)
    img.alpha_composite(lg, (W - lg.width - 36, 36))
    t = E.titulo("COMO FUNCIONA?", 100, cor=OURO, larg_max=760)
    img.alpha_composite(t, (50, 60))
    y = 60 + t.height + 30
    passos = [("1", "Escolha 3 jogos ou mais no site", E.LARANJA),
              ("2", "No carrinho, o mais barato sai de graça", E.PETROLEO),
              ("3", "Retire em Mauá ou receba em casa", (120, 70, 160))]
    for n, txt, cor in passos:
        card = E.bloco(900, 170, (255, 248, 232), raio=34, ow=7, sombra=10)
        d = ImageDraw.Draw(card)
        d.ellipse((30, 25, 150, 145), fill=cor, outline=E.MARROM, width=6)
        d.text((90, 88), n, font=E.lilita(80), fill=BRANCO, anchor="mm")
        tx = E.texto(txt, 42, cor=E.MARROM, peso=800, larg_max=680, alinha="lm")
        card.alpha_composite(tx, (180, (170 - tx.height) // 2))
        centro(img, card, W / 2, y)
        y += 200
    cx = tres_caixas(210)
    centro(img, cx, W / 2, y - 80)
    pl = E.pilula("SÓ ATÉ DOMINGO, 29/11 · LINK NA BIO", 38, OURO, E.MARROM, fonte_titulo=True)
    centro(img, pl, W / 2, H - pl.height - 40)
    return img


def story_de(tela, semente):
    st = fundo(1920, semente)
    st.alpha_composite(tela, (0, 285))
    return st


# ------------------------------------------------------------------------------------------------ REELS (curto)
def ease(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def back(x):
    x = min(max(x, 0), 1)
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


DUR = 12.0


def quadro_reels(t, stories=False):
    H = 1920
    img = fundo(H, 5)
    lg = E.logo(200)
    centro(img, lg, W / 2, 140)
    # 0–1,2: faixa BLACK FRIDAY bate
    k = back(t / 0.45)
    fb = faixa_bf()
    if k > 0.02:
        s = 0.4 + 0.6 * k if t < 0.45 else 1.0
        f2 = fb.resize((int(fb.width * s), int(fb.height * s)), Image.BICUBIC)
        centro(img, f2, W / 2, 330 + (fb.height - f2.height) / 2)
    # 0,8: título linha a linha
    linhas = ["ALUGUE 3 JOGOS,", "O MAIS BARATO", "É POR NOSSA CONTA!"]
    y = 330 + fb.height
    for i, l in enumerate(linhas):
        kk = ease((t - 0.8 - i * 0.35) / 0.3)
        if kk > 0:
            tt = E.titulo(l, 92, cor=OURO if i == 2 else BRANCO, larg_max=1000)
            tt2 = tt.copy()
            tt2.putalpha(tt.getchannel("A").point(lambda v: int(v * kk)))
            centro(img, tt2, W / 2, y + (1 - kk) * 40)
        y += 100
    # 2,2: caixas caem uma a uma; 4,0: carimbo GRÁTIS
    ims = [E.jogo(p, 280, 300) for p in CAIXAS]
    ims[2] = E.jogo(CAIXAS[2], 230, 250)
    xs = [W / 2 - 330, W / 2, W / 2 + 320]
    base = 1180
    for i, im in enumerate(ims):
        kk = back((t - 2.2 - i * 0.35) / 0.4)
        if kk > 0.01:
            im2 = im.rotate([3, -2, -5][i], expand=True, resample=Image.BICUBIC)
            img.alpha_composite(im2, (int(xs[i] - im2.width / 2), int(base - im2.height - (1 - kk) * 500)))
    kg = back((t - 3.8) / 0.35)
    if kg > 0.02:
        c = carimbo(s=60)
        c = c.resize((max(2, int(c.width * kg)), max(2, int(c.height * kg))), Image.BICUBIC)
        centro(img, c, xs[2], base - ims[2].height - c.height * 0.4)
    # 5,0: regra e prazo
    if t > 5.0:
        a = ease((t - 5.0) / 0.4)
        tx = E.texto("3 jogos ou mais no carrinho:\no mais barato sai de graça!", 44, cor=BRANCO, peso=800, larg_max=900)
        tx2 = tx.copy()
        tx2.putalpha(tx.getchannel("A").point(lambda v: int(v * a)))
        centro(img, tx2, W / 2, 1220)
    if t > 6.5:
        kk = back((t - 6.5) / 0.35)
        pl = E.pilula("SÓ ATÉ DOMINGO, 29/11", 48, OURO, E.MARROM, fonte_titulo=True)
        pl = pl.resize((max(2, int(pl.width * kk)), max(2, int(pl.height * kk))), Image.BICUBIC)
        centro(img, pl, W / 2, 1400)
    if t > 8.0:
        kk = ease((t - 8.0) / 0.4)
        if stories:
            seta = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
            seta_link(seta, 0, "garanta os seus aqui:")
            seta.putalpha(seta.getchannel("A").point(lambda v: int(v * kk)))
            img.alpha_composite(seta, (0, 1500))
        else:
            pl = E.pilula("RESERVE PELO LINK NA BIO · @SUAVEZ_BG", 36, E.LARANJA, BRANCO, fonte_titulo=True)
            pl.putalpha(pl.getchannel("A").point(lambda v: int(v * kk)))
            centro(img, pl, W / 2, 1530)
            c = E.texto("Comenta: quais 3 você levaria?", 40, cor=OURO, peso=900)
            c.putalpha(c.getchannel("A").point(lambda v: int(v * kk)))
            centro(img, c, W / 2, 1640)
    return img


def reels(stories=False):
    import subprocess
    import imageio_ffmpeg
    sys.path.insert(0, os.path.join(REPO, "becas-reels"))
    import sons as S
    FF = imageio_ffmpeg.get_ffmpeg_exe()
    nome = "bf_stories" if stories else "bf"
    ev = [(0.0, S.estouro(), 0.6)] + [(2.2 + i * 0.35, S.louca(1800 - i * 200), 0.5) for i in range(3)] + \
         [(3.8, S.carimbo() if hasattr(S, "carimbo") else S.estouro(), 0.7), (6.5, S.plim(), 0.5), (8.0, S.sino(), 0.4)]
    mus = S.musica_pop(DUR + 1, 0.0)
    com, sem = os.path.join(OUT, f"_{nome}_com.wav"), os.path.join(OUT, f"_{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.45, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    for wav, suf in ((com, "com_som"), (sem, "para_musica")):
        tmp = os.path.join(OUT, f"_{nome}_{suf}.mp4")
        wr = imageio_ffmpeg.write_frames(tmp, (W, 1920), fps=30, codec="libx264", quality=None,
                                         output_params=["-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p"],
                                         audio_path=wav, audio_codec="aac")
        wr.send(None)
        for i in range(int(DUR * 30)):
            wr.send(quadro_reels(i / 30, stories).convert("RGB").tobytes())
        wr.close()
        final = os.path.join(OUT, f"{nome}_{suf}_final.mp4")
        subprocess.run([FF, "-v", "error", "-y", "-i", tmp, "-c:v", "copy", "-af", "loudnorm=I=-15.5:TP=-2:LRA=11",
                        "-ar", "44100", "-c:a", "aac", "-b:a", "192k", final], check=True)
        print("ok", final)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--reels" in sys.argv:
        reels("--stories" in sys.argv)
        return
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        ims = [quadro_reels(t).convert("RGB").resize((360, 640)) for t in ts]
        f = Image.new("RGB", (370 * len(ims), 640), (255, 255, 255))
        for i, im in enumerate(ims):
            f.paste(im, (i * 370, 0))
        f.save(os.path.join(OUT, "frames.jpg"), quality=88)
        return
    saidas = {"story_1_promo": story_promo(), "story_2_como_funciona": story_como(), "story_3_ultimo_dia": story_ultimo(),
              "post_1": post(), "post_2_como_funciona": post_como()}
    for n, im in saidas.items():
        im.convert("RGB").save(os.path.join(OUT, n + ".png"))
    os.makedirs(os.path.join(OUT, "stories_do_carrossel"), exist_ok=True)
    for i, n in enumerate(("post_1", "post_2_como_funciona")):
        story_de(saidas[n], 10 + i).convert("RGB").save(os.path.join(OUT, "stories_do_carrossel", f"story_{i + 1:02d}.png"))
    f = Image.new("RGB", (3 * 400 + 2 * 420 + 60, 760), (255, 255, 255))
    x = 10
    for n in ("story_1_promo", "story_2_como_funciona", "story_3_ultimo_dia"):
        f.paste(saidas[n].convert("RGB").resize((400, 711)), (x, 10))
        x += 410
    for n in ("post_1", "post_2_como_funciona"):
        f.paste(saidas[n].convert("RGB").resize((420, 525)), (x, 10))
        x += 430
    f.save(os.path.join(OUT, "previa.jpg"), quality=88)
    print("ok")


if __name__ == "__main__":
    main()
