#!/usr/bin/env python3
"""Série "A CAIXA GANHA VIDA" (7/nov/2026): capa animada no Gemini (Veo, prompt meu, imagem inicial 9:16 em fundo creme
`coffee-reels/out/<jogo>_9x16.png`) + gancho, texto no meio e tela final de ALUGUEL (logo, caixa, "ALUGUE O ...", ficha do
site, 5 dias, retirada em Mauá ou entrega, link na bio). Episódio 1 (Coffee Rush) é o `cafe_rush.py` (convite da tarde).

    /usr/bin/python3 serie_caixa.py king [--stories] [--frame 0.5 3 7 12]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

import no_becas as NB
import cafe_rush as CR
from no_becas import K, S, E, W, H, FPS, MAR, PET, LAR, AMA, BR, Plano, etq, tit

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(AQUI)
OUT = K.OUT
SITE = json.load(open(os.path.join(ROOT, "comum", "dados", "acervo_site.json"), encoding="utf-8"))

EPS = {
    "king": dict(clipe="gemini2.mp4", jogo="King of Tokyo", nome="KING OF TOKYO",
                 caixa="hobby-reels/assets/caixas/king_of_tokyo.png",
                 gancho="TEM UM MONSTRO\nNA SUA MESA?", meio="ELE SAIU DA CAIXA!", t_meio=6.6,
                 comenta="COMENTA: QUAL MONSTRO VOCÊ SERIA?", musica="pop"),
    "boop": dict(clipe="gemini3.mp4", jogo="boop.", nome="BOOP.",
                 caixa="hobby-reels/assets/caixas/boop.png",
                 gancho="GATOS SÃO\nASSIM MESMO...", meio="EMPURRA-EMPURRA DE GATO!", t_meio=6.6,
                 comenta="MARCA ALGUÉM QUE TEM UM GATO DESSES!", musica="marimba", deitado=True),
}
EP = None
CLIPE = None
VID = 10.0
DUR = VID + 5.6
FMT = "reels"


def configura(ep):
    global EP, CLIPE
    EP = EPS[ep]
    K.CLIPES["serie_" + ep] = (os.path.join(ROOT, "coffee-reels", "brutos", EP["clipe"]), EP["nome"])
    CLIPE = Plano("serie_" + ep, 0.0, VID, 1.0)
    if EP.get("deitado"):  # o Gemini devolveu 16:9: cena grande no meio, o próprio vídeo desfocado de fundo (nada cortado)
        K.GRADE = ("split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:2,"
                   "eq=brightness=-0.06:saturation=0.9[bg];[b]scale=-2:760,crop=1080:760,hqdn3d=2:2:3:3,"
                   "unsharp=5:5:0.4[fg];[bg][fg]overlay=0:(H-h)/2+90")


def ficha():
    f = SITE[EP["jogo"]]
    j = f["jogadores"].replace("–", " A ")
    a, b = j.split(" A ")
    jog = f"{a} JOGADORES" if a == b else f"{a} A {b} JOGADORES"
    return jog, f["tempo"].replace("min", " MIN"), f["preco"]


def card_aluguel(w=920):
    jog, tempo, preco = ficha()
    c = E.bloco(w, 560, NB.CREME if hasattr(NB, "CREME") else (250, 244, 232), raio=40, ow=8, sombra=14).copy()
    d = ImageDraw.Draw(c)
    lg = E.logo(230)
    c.alpha_composite(lg, (int(w / 2 - lg.width / 2), 26))
    d.text((w / 2, 196), f"ALUGUE O {EP['nome']}", font=E.lilita(70 if len(EP["nome"]) < 12 else 60), fill=LAR,
           anchor="mm", stroke_width=4, stroke_fill=MAR)
    d.text((w / 2, 268), f"{jog} · {tempo}", font=E.fig(36, 800), fill=MAR, anchor="mm")
    d.text((w / 2, 318), f"R$ {preco} · 5 DIAS DE JOGO", font=E.fig(36, 900), fill=PET, anchor="mm")
    d.text((w / 2, 372), "Reserve online · retire em Mauá ou receba em casa", font=E.fig(30, 700), fill=MAR, anchor="mm")
    d.rounded_rectangle((60, 430, w - 60, 510), 30, fill=PET)
    d.text((w / 2, 470), "LINK NA BIO · @SUAVEZ_BG", font=E.lilita(42), fill=BR, anchor="mm")
    return c


def caixa(h=430):
    im = Image.open(os.path.join(ROOT, EP["caixa"])).convert("RGBA")
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def quadro(t):
    if t < VID:
        img = CR.tira_preto(CLIPE.quadro(t))
        if t < 3.6:
            K.escurece(img, 160, 520, 100)
            K.poe(img, tit(EP["gancho"], 86, BR), W / 2, 330, t, 0.2, -1.5)
        if t >= EP["t_meio"]:
            K.poe(img, etq(EP["meio"], 52, AMA, MAR), W / 2, 330, t, EP["t_meio"], -2)
        K.marca(img)
        return img.convert("RGB")
    img = CLIPE.quadro(VID - 0.01).filter(ImageFilter.GaussianBlur(12))
    u = t - VID
    NB.escuro(img, min(150, u * 400))
    if FMT == "stories":
        K.poe(img, caixa(380), W / 2, 330, t, VID + 0.1, -3)
        K.poe(img, card_aluguel(), W / 2, 820, t, VID + 0.35, 1)
        NB.linha_link(img, t, VID + 0.9, 1200, "aluga aqui:")
        K.poe(img, etq(EP["comenta"].replace("COMENTA: ", ""), 36, BR, MAR), W / 2, 1660, t, VID + 1.1, -1.5)
    else:
        K.poe(img, caixa(430), W / 2, 420, t, VID + 0.1, -3)
        K.poe(img, card_aluguel(), W / 2, 980, t, VID + 0.35, 1)
        K.poe(img, etq(EP["comenta"], 38, BR, MAR), W / 2, 1400, t, VID + 1.0, -1.5)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def main():
    global FMT
    ep = sys.argv[1]
    configura(ep)
    FMT = "stories" if "--stories" in sys.argv else "reels"
    nome = f"caixa_{ep}" + ("_stories" if FMT == "stories" else "")
    K.prepara([CLIPE.trecho()])
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, f"frames_{nome}.jpg"))
        print("ok", DUR, ficha())
        return
    CR.GEMINI = K.CLIPES["serie_" + ep][0]
    ev = [(0.0, CR.ambiente(), 0.6), (0.2, S.cartao(), 0.35), (EP["t_meio"], S.plim(), 0.35),
          (VID, S.sino(), 0.45), (VID + 0.35, S.cartao(), 0.4), (VID + 1.0, S.cartao(), 0.3)]
    mus = S.musica_pop(DUR + 0.5, 0.0) if EP["musica"] == "pop" else S.musica_marimba_pop(DUR + 0.5)
    com, sem = os.path.join(OUT, f"{nome}_com.wav"), os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.36, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    K.entrega(nome, DUR, render, com, sem)
    print("ok", nome, DUR)


if __name__ == "__main__":
    main()
