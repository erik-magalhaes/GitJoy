#!/usr/bin/env python3
"""CONVITE dos MEEPLES de madeira (8/nov/2026, ideia dele): no Gemini (modo Vídeos, NÃO o modelo "Convite para festa",
que força feltro), dois meeples de madeira (laranja e petróleo, as cores do logo) com guarda-chuvinhas de papel atravessam
a mesa de um café cheio de guarda-chuvinhas no teto, abrem um envelope verde e o cartão em BRANCO fica parado de frente.
Eu escrevo o convite NO cartão (o Gemini erra letra/acento). Clipe `coffee-reels/brutos/meeple_a.mp4` (720x1280, 10 s);
o cartão fica imóvel de 7,3 s em diante em x 280–806, y 648–1364 (medido em 1080x1920). `meeple_b.mp4` = versão de feltro.

    0–10 s   clipe + gancho; o texto do convite aparece no cartão a partir de 7,4 s
    10–15 s  quadro parado com aproximação lenta no cartão + WhatsApp / comenta (Reels) ou espaço do link (Stories)

    /usr/bin/python3 convite_meeple.py [--stories] [--frame 1 8 11 14]
"""
import os
import sys
from functools import lru_cache

import numpy as np
from scipy import ndimage

from PIL import Image, ImageDraw

import no_becas as NB
import cafe_rush as CR
from no_becas import K, S, E, TB, W, H, FPS, MAR, PET, LAR, AMA, BR, Plano, etq, tit

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = K.OUT
CLIPE_ARQ = os.path.join(AQUI, "..", "coffee-reels", "brutos", "meeple_a.mp4")
K.CLIPES["meeple"] = (os.path.abspath(CLIPE_ARQ), "CONVITE")
CLIPE = Plano("meeple", 0.0, 10.0, 1.0)
VID = CLIPE.d
DUR = VID + 5.0
CARTAO = (292, 648, 793, 1362)  # parado, de 6,8 s em diante (medido no cache 1080x1920)
T_TXT = 6.0  # 8/nov, pedido dele: o texto já aparece quando o papel SOBE do envelope e acompanha o papel
T_PARADO = 6.8
RAZAO = (CARTAO[3] - CARTAO[1]) / (CARTAO[2] - CARTAO[0])
FMT = "reels"


def texto_cartao(alfa=1.0):
    """O convite escrito no cartão (transparente fora das letras), do tamanho do cartão."""
    x0, y0, x1, y1 = CARTAO
    w, h = x1 - x0, y1 - y0
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w / 2
    p = TB.parceria(58)
    im.alpha_composite(p, (int(cx - p.width / 2), 40))
    d.text((cx, 172), "VOCÊ ESTÁ CONVIDADO PRA", font=E.fig(24, 800), fill=MAR, anchor="mm")
    d.text((cx, 240), "TARDE", font=E.lilita(96), fill=LAR, anchor="mm", stroke_width=5, stroke_fill=MAR)
    d.text((cx, 330), "DE JOGOS", font=E.lilita(84), fill=LAR, anchor="mm", stroke_width=5, stroke_fill=MAR)
    d.rounded_rectangle((44, 392, w - 44, 452), 30, fill=PET)
    d.text((cx, 422), "SEXTA, 20/11 (FERIADO)", font=E.lilita(36), fill=BR, anchor="mm")
    d.text((cx, 492), "13H ÀS 19H", font=E.lilita(44), fill=MAR, anchor="mm")
    d.text((cx, 548), "Beca’s Café · Rua Sorocaba, 35 · Mauá", font=E.fig(23, 800), fill=MAR, anchor="mm")
    d.text((cx, 590), "R$ 30, e R$ 15 viram consumação", font=E.fig(23, 700), fill=PET, anchor="mm")
    d.text((cx, 650), "a gente leva os jogos e ensina!", font=E.fig(24, 800), fill=MAR, anchor="mm")
    if alfa < 1:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alfa)))
    return im


def mascara_cartao(img):
    """Pixels do papel creme (sem o envelope, os meeples e os guarda-chuvinhas na frente)."""
    f = np.asarray(img.convert("RGB")).astype(int)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    m = (R > 175) & (G > 160) & (B > 125) & ((R - B) < 75) & ((R - G) < 40)
    m[:350] = 0
    m[1500:] = 0
    m[:, :200] = 0
    m[:, 880:] = 0
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m)
    if n == 0:
        return None, None
    tam = ndimage.sum(m, lab, range(1, n + 1))
    k = int(np.argmax(tam)) + 1
    m = ndimage.binary_fill_holes(ndimage.binary_closing(lab == k, iterations=4))
    ys, xs = np.where(m)
    return m, (int(np.percentile(xs, 1)), int(ys.min()))


@lru_cache(None)
def _texto(w, h):
    return texto_cartao().resize((w, h), Image.LANCZOS)


def poe_no_cartao(img, alfa):
    if alfa <= 0:
        return
    m, canto = mascara_cartao(img)
    if m is None:
        return
    if img_t_parado(img):
        x0, y0, x1, y1 = CARTAO
    else:  # subindo: largura do papel inteiro, topo e esquerda medidos no quadro
        w = 460
        x0, y0 = canto
        x1, y1 = x0 + w, int(y0 + w * RAZAO)
    tx = _texto(x1 - x0, y1 - y0)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(tx, (x0, y0))
    a = np.asarray(lay.getchannel("A")).astype(np.float32)
    mm = ndimage.gaussian_filter(m.astype(np.float32), 1.2)
    lay.putalpha(Image.fromarray((a * mm * alfa).astype(np.uint8)))
    img.alpha_composite(lay)


_T = [0.0]


def img_t_parado(img):
    return _T[0] >= T_PARADO


def zoom(img, z, cx, cy):
    if z <= 1.0001:
        return img
    w, h = int(W / z), int(H / z)
    x0 = min(max(0, int(cx - w / 2)), W - w)
    y0 = min(max(0, int(cy - h / 2)), H - h)
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.LANCZOS)


def quadro(t):
    _T[0] = t
    img = CLIPE.quadro(min(t, VID - 0.01))  # sem tira_preto: aqui o escuro da borda é o próprio café
    if t >= T_TXT:  # o convite já vem escrito no papel que sobe do envelope
        poe_no_cartao(img, min(1.0, (t - T_TXT) / 0.2))
    if t > VID:
        u = min(1.0, (t - VID) / 4.5)
        img = zoom(img, 1 + 0.07 * NB.ease(u), (CARTAO[0] + CARTAO[2]) / 2, (CARTAO[1] + CARTAO[3]) / 2 + 60)
    if t < 3.6:
        K.escurece(img, 120, 520, 110)
        K.poe(img, tit("CHEGOU UM\nCONVITE PRA VOCÊ!", 84, BR), W / 2, 320, t, 0.2, -1.5)
    if t >= VID:
        if FMT == "stories":
            NB.linha_link(img, t, VID + 0.3, 1440)
            K.poe(img, etq("MANDA PRA QUEM VAI COM VOCÊ!", 40, BR, MAR), W / 2, 1700, t, VID + 0.6, -1.5)
        else:
            K.poe(img, etq("GARANTA SUA MESA: WHATSAPP (11) 97793-3910", 36, BR, PET), W / 2, 1480, t, VID + 0.2, 1)
            K.poe(img, etq("COMENTA: QUEM VOCÊ LEVA COM VOCÊ?", 40, BR, MAR), W / 2, 1590, t, VID + 0.6, -1.5)
    K.marca(img)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def main():
    global FMT
    FMT = "stories" if "--stories" in sys.argv else "reels"
    nome = "convite_meeple" + ("_stories" if FMT == "stories" else "")
    K.prepara([CLIPE.trecho()])
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, f"frames_{nome}.jpg"))
        print("ok", DUR)
        return
    CR.GEMINI = K.CLIPES["meeple"][0]
    ev = [(0.0, CR.ambiente(), 0.6), (0.2, S.cartao(), 0.35), (T_TXT, S.plim(), 0.4), (VID, S.sino(), 0.4),
          (VID + 0.2, S.cartao(), 0.35), (VID + 0.6, S.cartao(), 0.3)]
    com, sem = os.path.join(OUT, f"{nome}_com.wav"), os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, S.musica_cafe(DUR + 0.5), musica_ganho=0.38, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    K.entrega(nome, DUR, render, com, sem)
    print("ok", nome, DUR)


if __name__ == "__main__":
    main()
