#!/usr/bin/env python3
"""4 peças com as GRAVAÇÕES DELES NO BECA’S (6/nov/2026; brutos em brutos/nov06/, fora do git). Pedido dele: "pode
fazer todos", com cuidado com ROSTOS (clientes, criança) e PLACAS DE CARRO.

    revela   Story/Reels ~14,5 s para SÁBADO AO MEIO-DIA: continua o mistério do save_date_sv (a carta "?" treme, vira e
             abre em tela cheia), a caminhada pelo portão e pelas guarda-chuvinhas e a revelação "TARDE DE JOGOS NO
             BECA’S CAFÉ"; área y≈1350–1580 LIVRE para o adesivo de link.
    chegar   "Como chegar" ~22 s: o caminho acelerado (igreja → calçada → Alquifarma → bandeira → portão), barrinha de
             GPS no alto, e fecha com endereço, data e WhatsApp. O nome da igreja NÃO foi confirmado: só "a igreja".
    gostinho "Um gostinho do que te espera" ~25 s: entrada, guarda-chuvinhas, salão, vitrine, brownie, a careta da
             Jéssica, "agora imagina isso com um jogo na mesa..." e o convite.
    fotos    Carrossel 1080x1350 "Conheça o Beca’s" (5 telas) com quadros dos vídeos + o convite.

Privacidade: os trechos do caminho foram escolhidos ENTRE as placas legíveis (Clio 6–11 s, van 25,5–29,5 s, HB20
30–35,5 s, carro preto 36–37 s do 151125) e o salão cheio (55–57 s, mulher e criança perto) ficou de fora. Onde ainda
aparece gente ou carro, há desfoque suave (`BORRA`, caixas em tempo do bruto) e, no salão, desfoque de "tilt-shift"
abaixo do teto (só as luzes e a madeira ficam nítidas). Cardápio não entra (preço e reflexo).

    /usr/bin/python3 no_becas.py revela --frame 0.5 2.6 3.5 8 12
    /usr/bin/python3 no_becas.py revela      # out/revela_{com_som,para_musica}_final.mp4
"""
import math
import os
import random
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import kit as K
import sons as S
from kit import E, TB, W, H, FPS, MAR, PET, LAR, AMA, BR, ROSA, out_back, ease

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
NOV = os.path.join(ROOT, "brutos", "nov06")
OUT = K.OUT
CREME = TB.CREME
VERDE = (118, 176, 65)
OLIVA = (96, 104, 62)

for _n, _a in {"rota": "20261106_151125.mp4", "jardim": "20261106_150333.mp4", "vitrine": "20261106_150657.mp4",
               "brownie": "20261106_151353.mp4"}.items():
    K.CLIPES[_n] = (os.path.join(NOV, _a), "BECA’S")

# desfoque de privacidade: nome → [(t0, t1 do bruto, caixa 1080x1920)]
BORRA = {
    "rota": [(3.0, 5.8, (240, 800, 760, 1010)),  # gente pequena na porta da igreja
             (42.8, 45.6, (840, 940, 1080, 1280))],  # carro vermelho atrás do portão
    "jardim": [(14.6, 14.95, (760, 830, 1080, 1120)),  # cliente atrás da Jéssica (a câmera gira até ela)
               (14.95, 15.25, (850, 760, 1080, 1060)),
               (15.25, 16.2, (920, 700, 1080, 1030))],
    "vitrine": [(7.8, 10.8, (230, 120, 780, 820))],  # atendente atrás do vidro dos cookies
    "brownie": [(3.4, 6.0, (760, 380, 1080, 1120))],  # equipe do café ao fundo
}
TILT = {"salao": 760, "ceu": 1060, "entrada": 720}  # desfoque abaixo de y


def mascara_suave(box, r=40):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 40, fill=255)
    return m.filter(ImageFilter.GaussianBlur(r))


@lru_cache(None)
def _mask(box):
    return mascara_suave(box)


@lru_cache(None)
def _tilt_mask(y0, rampa=180):
    a = np.clip((np.arange(H) - y0) / rampa, 0, 1)
    return Image.fromarray(np.repeat((a * 255).astype(np.uint8)[:, None], W, axis=1))


def privado(img, nome, ts, tilt=None):
    for t0, t1, box in BORRA.get(nome, []):
        if t0 <= ts <= t1:
            img = Image.composite(img.filter(ImageFilter.GaussianBlur(26)), img, _mask(box))
    if tilt is not None:
        img = Image.composite(img.filter(ImageFilter.GaussianBlur(22)), img, _tilt_mask(tilt))
    return img


def zoom(img, z, ax=0.5, ay=0.5):
    if z <= 1.001:
        return img
    w, h = W / z, H / z
    x0, y0 = (W - w) * ax, (H - h) * ay
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))


class Plano:
    """Trecho de vídeo na tela: bruto `nome` a partir de t0, `d` segundos de tela, velocidade `vel`."""

    def __init__(self, nome, t0, d, vel=1.0, z=(1.0, 1.0), ay=0.5, tilt=None):
        self.nome, self.t0, self.d, self.vel, self.z, self.ay, self.tilt = nome, t0, d, vel, z, ay, tilt

    def trecho(self):
        return (self.nome, self.t0, self.d, self.vel)

    def quadro(self, u):
        u = max(0.0, min(self.d - 1e-3, u))
        im = K.quadro_clip(self.nome, self.t0, self.d, self.vel, u).convert("RGB")
        im = privado(im, self.nome, self.t0 + u * self.vel, self.tilt)
        z = self.z[0] + (self.z[1] - self.z[0]) * u / self.d
        return zoom(im, z, 0.5, self.ay).convert("RGBA")


def sequencia(planos, t, dis=0.18):
    """Planos em fila com dissolve curto; devolve (quadro, índice, u)."""
    a = 0.0
    for k, p in enumerate(planos):
        if t < a + p.d or k == len(planos) - 1:
            u = t - a
            im = p.quadro(u)
            if k > 0 and u < dis:
                ant = planos[k - 1].quadro(planos[k - 1].d - 1e-3)
                im = Image.blend(ant, im, u / dis)
            return im, k, u
        a += p.d
    raise ValueError


def inicios(planos):
    a, r = 0.0, []
    for p in planos:
        r.append(a)
        a += p.d
    return r


@lru_cache(None)
def etq(txt, s=50, cor=AMA, fg=MAR):
    return E.pilula(txt, s, cor, fg, fonte_titulo=True)


@lru_cache(None)
def tit(txt, s, cor=BR, larg=980):
    return E.titulo(txt, s, cor, larg_max=larg)


@lru_cache(None)
def seta(cor=BR, h=110):
    im = Image.new("RGBA", (100, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((50, 5, 50, h - 40), fill=cor, width=15)
    d.polygon([(10, h - 52), (90, h - 52), (50, h)], fill=cor)
    return im


def escuro(img, a):
    sh = Image.new("RGBA", (W, H), (25, 15, 8, int(a)))
    img.alpha_composite(sh)


@lru_cache(None)
def confete_pts(seed=5, n=90):
    rnd = random.Random(seed)
    cores = [LAR, AMA, ROSA, PET, VERDE, BR]
    return [(rnd.uniform(0, W), rnd.uniform(-300, -20), rnd.uniform(-160, 160), rnd.uniform(380, 720),
             rnd.choice(cores), rnd.uniform(14, 26), rnd.uniform(0, 6.28)) for _ in range(n)]


def confete(img, t, t0, seed=5):
    if t < t0:
        return
    u = t - t0
    d = ImageDraw.Draw(img)
    for x, y, vx, vy, c, s, f in confete_pts(seed):
        X = x + vx * u + 30 * math.sin(u * 3 + f)
        Y = y + vy * u + 120 * u * u
        if Y > H + 40:
            continue
        ang = u * 6 + f
        w2, h2 = s * abs(math.cos(ang)) + 3, s * 0.55
        d.polygon([(X - w2, Y - h2), (X + w2, Y - h2 * 0.6), (X + w2, Y + h2), (X - w2, Y + h2 * 0.6)], fill=c)


def balanco(img, t, alturas=(110, 190, 80, 160, 120, 210), y_teto=0):
    """Guarda-chuvinhas balançando no alto (assinatura visual das peças do Beca’s)."""
    cores = [LAR, PET, AMA, ROSA, VERDE, LAR]
    xs = [100, 270, 440, 610, 780, 960]
    for k, (x, comp) in enumerate(zip(xs, alturas)):
        g = gchuva(cores[k], k)
        ang = 7 * math.sin(t * 1.6 + k * 1.1)
        px, py = x, y_teto
        cx = px + comp * math.sin(math.radians(ang))
        cy = py + comp * math.cos(math.radians(ang))
        ImageDraw.Draw(img).line((px, py, cx, cy), fill=MAR, width=4)
        E.cola(img, g, cx, cy + g.height * 0.32, -ang)


@lru_cache(None)
def gchuva(cor, seed):
    return TB.guarda_chuva(130, cor, seed)


# ======================================================================== REVELAÇÃO
import save_date_sv as SV  # noqa: E402

R_FLIP = (1.7, 2.0)  # a carta vira até a metade
R_ABRE = (2.0, 2.55)  # e abre com o vídeo dentro, até a tela cheia
R_PL = [Plano("rota", 39.0, 4.6, 1.55, z=(1.06, 1.0)),  # bandeira → portão com a placa redonda
        Plano("jardim", 5.2, 2.6, 1.0, z=(1.25, 1.35), ay=0.15, tilt=TILT["ceu"])]
R_T0 = R_ABRE[0]
R_FUNDO = Plano("jardim", 5.0, 6.6, 0.6, z=(1.3, 1.3), ay=0.12, tilt=TILT["ceu"])
R_FIM = R_T0 + sum(p.d for p in R_PL)  # 9.2
R_DUR = R_FIM + 5.4


def r_carta_abrindo(img, t):
    if t < R_FLIP[0]:
        SV.carta(img, min(t, SV.T_VIRA[0] - 0.01) if t < SV.T_VIRA[0] else SV.T_VIRA[0] - 0.01)
        return
    if t < R_FLIP[1]:
        u = (t - R_FLIP[0]) / (R_FLIP[1] - R_FLIP[0])
        f = SV.verso()
        f = f.resize((max(2, int(f.width * math.cos(u * math.pi / 2) * SV.KC)), int(f.height * SV.KC)))
        E.cola(img, f, W / 2, SV.CY)
        return
    u = ease(min(1.0, (t - R_ABRE[0]) / (R_ABRE[1] - R_ABRE[0])))
    w0, h0 = SV.CW_ * SV.KC, SV.CH_ * SV.KC
    ww, hh = w0 + (W + 60 - w0) * u, h0 + (H + 60 - h0) * u
    sx = min(1.0, (t - R_ABRE[0]) / 0.12)
    ww = max(4, ww * sx)
    cy = SV.CY + (H / 2 - SV.CY) * u
    v, _, _ = sequencia(R_PL, t - R_T0)
    esc = max(ww / W, hh / H)
    v = v.resize((int(W * esc) + 1, int(H * esc) + 1))
    v = v.crop((int((v.width - ww) / 2), int((v.height - hh) / 2), int((v.width - ww) / 2 + ww),
                int((v.height - hh) / 2 + hh)))
    m = Image.new("L", v.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, v.width - 1, v.height - 1), int(44 * (1 - u) + 2), fill=255)
    cart = Image.new("RGBA", (v.width + 16, v.height + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(cart)
    d.rounded_rectangle((12, 12, v.width + 12, v.height + 12), int(44 * (1 - u) + 2), fill=MAR)
    cart.paste(v, (0, 0), m)
    ImageDraw.Draw(cart).rounded_rectangle((0, 0, v.width, v.height), int(44 * (1 - u) + 2), outline=MAR,
                                           width=max(1, int(8 * (1 - u))))
    img.alpha_composite(cart, (int(W / 2 - v.width / 2), int(cy - v.height / 2)))


def r_quadro(t):
    if t < R_ABRE[1]:
        img = SV.fundo().copy()
        SV.flutua(img, t)
        K.poe(img, K.logo(200), W / 2, 270, t, 0.05)
        K.poe(img, tit("A NOVIDADE\nCHEGOU!", 120, LAR), W / 2, 1300, t, 0.35, -2)
        K.poe(img, etq("LEMBRA DESSA CARTA?", 46, PET, BR), W / 2, 1490, t, 0.6, 1.5)
        r_carta_abrindo(img, t)
        return img.convert("RGB")
    if t < R_FIM:
        img, k, u = sequencia(R_PL, t - R_T0)
        K.marca(img)
        if k == 0:
            if u < 2.6:
                K.poe(img, etq("VEM COM A GENTE...", 54), W / 2, 1450, t, R_T0 + 0.4, -2)
            else:
                K.poe(img, etq("ENTRA AQUI!", 60, LAR, BR), W / 2, 1450, t, R_T0 + 2.6, 2)
        else:
            K.poe(img, tit("OLHA ESSE TETO!", 96, AMA), W / 2, 1420, t, R_T0 + R_PL[0].d + 0.2, -2)
        return img.convert("RGB")
    # revelação final
    u = t - R_FIM
    img = R_FUNDO.quadro(min(u, R_FUNDO.d - 0.01)).filter(ImageFilter.GaussianBlur(10))
    escuro(img, min(150, 60 + u * 300))
    flash = max(0.0, 1 - u / 0.25)
    K.poe(img, TB.parceria(118), W / 2, 260, t, R_FIM + 0.1)
    K.poe(img, tit("TARDE DE JOGOS", 128, AMA), W / 2, 480, t, R_FIM + 0.2, -2)
    K.poe(img, tit("NO BECA’S CAFÉ!", 108, BR), W / 2, 615, t, R_FIM + 0.4, 1)
    K.poe(img, TB.selo_data(44), W / 2, 760, t, R_FIM + 0.8, -1.5)
    K.poe(img, TB.selo_endereco(38), W / 2, 850, t, R_FIM + 1.0, 1)
    K.poe(img, etq("R$ 30 · R$ 15 VIRAM CONSUMAÇÃO NO CAFÉ", 36, BR, MAR), W / 2, 935, t, R_FIM + 1.2, -1)
    K.poe(img, etq("A GENTE LEVA OS JOGOS E ENSINA!", 40, LAR, BR), W / 2, 1025, t, R_FIM + 1.4, 1.5)
    if u > 1.9:
        a = min(1, (u - 1.9) / 0.3)
        bob = 8 * math.sin(2 * math.pi * (u - 1.9) / 1.2)
        lin = Image.new("RGBA", (W, 140), (0, 0, 0, 0))
        ImageDraw.Draw(lin).text((W / 2 - 60, 55), "garanta sua mesa aqui:", font=E.fig(44, 900), fill=BR,
                                 anchor="mm", stroke_width=4, stroke_fill=MAR)
        lin.alpha_composite(seta(BR), (int(W / 2 + 255), int(bob)))
        if a < 1:
            lin.putalpha(lin.getchannel("A").point(lambda v: int(v * a)))
        img.alpha_composite(lin, (0, 1185))
    # y≈1350–1580 LIVRE para o adesivo de link
    K.poe(img, etq(f"OU NO WHATSAPP {TB.WHATS}", 40, PET, BR), W / 2, 1660, t, R_FIM + 2.2)
    confete(img, t, R_FIM)
    if flash > 0:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * flash))))
    return img.convert("RGB")


def r_audio():
    ev = [(0.05, S.cartao(), 0.4), (0.35, S.cartao(), 0.35), (0.55, S.dado(), 0.3), (R_FLIP[0], S.carta_vira(), 0.7),
          (R_ABRE[0], S.sopro(0.5), 0.5), (R_T0 + 0.4, S.cartao(), 0.3), (R_T0 + 2.6, S.cartao(), 0.3),
          (R_T0 + R_PL[0].d, S.sopro(0.4), 0.35), (R_FIM, S.estouro(), 0.6), (R_FIM + 0.2, S.sino(), 0.45),
          (R_FIM + 0.8, S.plim(), 0.4), (R_FIM + 2.2, S.cartao(), 0.3)]
    return ev, S.musica_marimba_pop(R_DUR + 0.5), 0.42


# ======================================================================== COMO CHEGAR
C_PL = [Plano("rota", 0.0, 3.4, 1.62),  # esquina → igreja
        Plano("rota", 12.0, 6.2, 2.0),  # calçada, "ESCOLAR", Alquifarma
        Plano("rota", 39.0, 4.6, 1.55),  # bandeira do Beca’s → portão
        Plano("jardim", 5.2, 2.4, 1.0, z=(1.25, 1.35), ay=0.15, tilt=TILT["ceu"])]
C_ETQ = [  # (plano, u0, texto, cor, fg)
    (0, 0.3, "COMEÇA NA IGREJA", AMA, MAR),
    (1, 0.3, "SEGUE PELA CALÇADA...", AMA, MAR),
    (1, 3.6, "PASSA A ALQUIFARMA", BR, PET),
    (2, 0.3, "OLHA A BANDEIRA DO BECA’S!", AMA, MAR),
    (2, 2.7, "CHEGOU! É SÓ ENTRAR", LAR, BR),
    (3, 0.2, "E OLHA O QUE TE ESPERA...", AMA, MAR),
]
C_PARADAS = ["IGREJA", "ALQUIFARMA", "BANDEIRA", "BECA’S"]
C_INI = inicios(C_PL)
C_VID = sum(p.d for p in C_PL)
C_DUR = C_VID + 5.6


def gps(img, t):
    """Barrinha de GPS no alto: 4 paradas e o pino andando."""
    x0, x1, y = 90, 990, 300
    painel = E.bloco(x1 - x0 + 80, 150, CREME, raio=30, ow=6, sombra=8)
    img.alpha_composite(painel, (x0 - 40, y - 85))
    d = ImageDraw.Draw(img)
    xs = [x0 + 40 + k * (x1 - x0 - 80) / 3 for k in range(4)]
    marcos = [0.4, C_INI[1] + 3.6, C_INI[2] + 0.3, C_INI[2] + 2.7]  # chega em cada parada junto com a etiqueta
    prog = 3.0
    for k in range(3):
        if t < marcos[k + 1]:
            prog = k + max(0.0, (t - marcos[k])) / (marcos[k + 1] - marcos[k])
            break
    prog /= 3
    d.line((xs[0], y, xs[-1], y), fill=(205, 190, 170), width=12)
    xp = xs[0] + (xs[-1] - xs[0]) * prog
    d.line((xs[0], y, xp, y), fill=LAR, width=12)
    for k, x in enumerate(xs):
        on = xp >= x - 2
        d.ellipse((x - 17, y - 17, x + 17, y + 17), fill=LAR if on else BR, outline=MAR, width=4)
        d.text((x, y + 42), C_PARADAS[k], font=E.lilita(26), fill=MAR if on else (150, 130, 110), anchor="mm")
    # pino
    pin = Image.new("RGBA", (60, 80), (0, 0, 0, 0))
    dp = ImageDraw.Draw(pin)
    dp.polygon([(10, 30), (50, 30), (30, 76)], fill=ROSA, outline=MAR)
    dp.ellipse((4, 4, 56, 56), fill=ROSA, outline=MAR, width=4)
    dp.ellipse((20, 20, 40, 40), fill=BR)
    pul = 4 * abs(math.sin(t * 6))
    img.alpha_composite(pin, (int(xp - 30), int(y - 78 - pul)))


@lru_cache(None)
def card_convite(w=920, fala="garanta sua mesa"):
    c = E.bloco(w, 600, CREME, raio=40, ow=8, sombra=14).copy()
    d = ImageDraw.Draw(c)
    p = TB.parceria(84)
    c.alpha_composite(p, (int(w / 2 - p.width / 2), 34))
    d.text((w / 2, 190), "TARDE DE JOGOS", font=E.lilita(96), fill=LAR, anchor="mm", stroke_width=5, stroke_fill=MAR)
    s = TB.selo_data(38)
    c.alpha_composite(s, (int(w / 2 - s.width / 2), 250))
    d.text((w / 2, 362), "Rua Sorocaba, 35 · Mauá", font=E.fig(38, 900), fill=PET, anchor="mm")
    d.text((w / 2, 412), "R$ 30, e R$ 15 viram consumação no café", font=E.fig(33, 800), fill=MAR, anchor="mm")
    d.text((w / 2, 455), "a gente leva os jogos e ensina!", font=E.fig(33, 700), fill=MAR, anchor="mm")
    d.rounded_rectangle((50, 495, w - 50, 570), 30, fill=PET)
    d.text((w / 2, 533), f"{fala.upper()}: WHATSAPP {TB.WHATS}", font=E.lilita(36), fill=BR, anchor="mm")
    return c


def c_quadro(t):
    if t < C_VID:
        img, k, u = sequencia(C_PL, t)
        K.escurece(img, 1350, 1700, 120)
        for kp, u0, txt, cor, fg in C_ETQ:
            if kp == k and u >= u0:
                nxt = [e for e in C_ETQ if e[0] == k and e[1] > u0]
                if nxt and u >= nxt[0][1]:
                    continue
                K.poe(img, etq(txt, 56, cor, fg), W / 2, 1500, t, C_INI[k] + u0, (-2, 1.5)[len(txt) % 2])
        gps(img, t)
        if t < 2.6:
            K.poe(img, tit("COMO CHEGAR\nNO BECA’S CAFÉ", 108, BR), W / 2, 640, t, 0.1, -2)
        K.marca(img)
        return img.convert("RGB")
    u = t - C_VID
    img = C_PL[-1].quadro(C_PL[-1].d - 0.01).filter(ImageFilter.GaussianBlur(12))
    escuro(img, min(140, u * 400))
    balanco(img, t)
    K.poe(img, tit("ANOTA O ENDEREÇO!", 100, AMA), W / 2, 560, t, C_VID + 0.1, -2)
    K.poe(img, card_convite(), W / 2, 1020, t, C_VID + 0.35, 1)
    K.poe(img, etq("SALVA ESSE VÍDEO PRA NÃO SE PERDER!", 40, BR, MAR), W / 2, 1440, t, C_VID + 0.9, -1.5)
    return img.convert("RGB")


def c_audio():
    ev = [(0.1, S.cartao(), 0.4)]
    for kp, u0, *_ in C_ETQ:
        ev.append((C_INI[kp] + u0, S.cartao(), 0.32))
    for a in C_INI[1:]:
        ev.append((a - 0.05, S.sopro(0.3), 0.3))
    ev += [(C_INI[2] + 2.7, S.plim(), 0.45), (C_VID, S.sino(), 0.45), (C_VID + 0.35, S.cartao(), 0.4),
           (C_VID + 0.9, S.cartao(), 0.3)]
    return ev, S.musica_pop(C_DUR + 0.5, 0.0), 0.4


# ======================================================================== GOSTINHO
G_PL = [Plano("jardim", 5.0, 3.2, 0.9, z=(1.25, 1.38), ay=0.15, tilt=TILT["ceu"]),
        Plano("jardim", 11.4, 2.0, 0.9, z=(1.05, 1.12), ay=0.3, tilt=TILT["salao"]),
        Plano("vitrine", 2.4, 2.8, 1.0, z=(1.0, 1.06)),
        Plano("vitrine", 8.2, 2.2, 1.0, z=(1.08, 1.0)),
        Plano("brownie", 0.0, 3.4, 1.0, z=(1.0, 1.08)),
        Plano("brownie", 4.0, 2.0, 0.85),
        Plano("jardim", 14.85, 3.0, 0.3, z=(1.0, 1.05), ay=0.6)]
G_TXT = ["UM GOSTINHO DO QUE\nTE ESPERA NO BECA’S...", "SALÃO ACONCHEGANTE", "VITRINE DE DAR\nÁGUA NA BOCA",
         "COOKIES!", "BROWNIE COM CHANTILLY\nE MORANGO", "", "AGORA IMAGINA ISSO\nCOM UM JOGO NA MESA..."]
G_INI = inicios(G_PL)
G_VID = sum(p.d for p in G_PL)
G_DUR = G_VID + 5.8
G_CAIXAS = ["dixit", "hitster", "telma"]


@lru_cache(None)
def caixa(n, h=330):
    return E.jogo(os.path.join(REPO, "hobby-reels", "assets", "acervo", f"{n}.png"), h)


@lru_cache(None)
def carimbo(txt="APROVADO!"):
    f = E.lilita(92)
    w = int(f.getlength(txt)) + 80
    im = Image.new("RGBA", (w, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w - 6, 144), 26, outline=(220, 40, 60), width=10)
    d.text((w / 2, 75), txt, font=f, fill=(220, 40, 60), anchor="mm")
    return im


def g_quadro(t):
    if t < G_VID:
        img, k, u = sequencia(G_PL, t)
        txt = G_TXT[k]
        if txt:
            n = txt.count("\n") + 1
            if k == 6:
                K.escurece(img, 300, 640, 130)
            else:
                K.escurece(img, 1240 - 60 * n, 1720, 130)
            yt = 470 if k == 6 else 1500 - 40 * (n - 1)
            K.poe(img, tit(txt, 84 if n > 1 else 96, AMA if k % 2 == 0 else BR), W / 2, yt, t,
                  G_INI[k] + 0.15, (-2, 1.5)[k % 2])
        if k == 5:  # careta da Jéssica comendo
            K.poe(img, carimbo(), W / 2, 1420, t, G_INI[5] + 0.35, -8, d=0.22)
            K.poe(img, etq("TESTADO PELA JÉSSICA", 44, AMA, MAR), W / 2, 1560, t, G_INI[5] + 0.6, 2)
        if k == 6:  # caixas de jogo pousando na mesa dela
            for j, n in enumerate(G_CAIXAS):
                K.poe(img, caixa(n, 270), 170 + j * 250, 1590 + (j % 2) * 50, t, G_INI[6] + 1.0 + j * 0.3,
                      (-8, 5, -3)[j], d=0.28)
        K.marca(img)
        return img.convert("RGB")
    u = t - G_VID
    img = G_PL[-1].quadro(G_PL[-1].d - 0.01).filter(ImageFilter.GaussianBlur(12))
    escuro(img, min(140, u * 400))
    balanco(img, t)
    K.poe(img, tit("VEM JOGAR COM A GENTE!", 92, AMA), W / 2, 540, t, G_VID + 0.1, -2)
    K.poe(img, card_convite(), W / 2, 980, t, G_VID + 0.35, 1)
    K.poe(img, etq("COMENTA: QUAL DOCE VOCÊ PEDE PRIMEIRO?", 38, BR, MAR), W / 2, 1420, t, G_VID + 1.0, -1.5)
    return img.convert("RGB")


def g_audio():
    ev = [(G_INI[k] + 0.15, S.cartao(), 0.3) for k in range(len(G_PL)) if G_TXT[k]]
    ev += [(a - 0.05, S.sopro(0.3), 0.25) for a in G_INI[1:]]
    ev += [(G_INI[5] + 0.35, S.dado(), 0.5), (G_INI[5] + 0.6, S.plim(), 0.35)]
    ev += [(G_INI[6] + 1.0 + j * 0.3, S.cartao(), 0.4) for j in range(3)]
    ev += [(G_VID, S.sino(), 0.45), (G_VID + 0.35, S.cartao(), 0.4), (G_VID + 1.0, S.cartao(), 0.3)]
    return ev, S.musica_cafe(G_DUR + 0.5), 0.45


# ======================================================================== FOTOS (carrossel 1080x1350)
FW, FH = 1080, 1350


def quadro_bruto(arq, ts, nome=None, tilt=None):
    """Quadro em resolução cheia (1080x1920) do bruto no tempo ts, com a privacidade aplicada."""
    pasta = os.path.join(OUT, "_fotos")
    os.makedirs(pasta, exist_ok=True)
    dst = os.path.join(pasta, f"{os.path.basename(arq)}_{ts:.2f}.png")
    if not os.path.exists(dst):
        subprocess.run([K.ffmpeg(), "-v", "error", "-y", "-ss", str(ts), "-i", arq, "-frames:v", "1", "-vf",
                        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,hqdn3d=2:2:3:3,"
                        "eq=contrast=1.03:saturation=1.06,unsharp=5:5:0.4", dst], check=True)
    im = Image.open(dst).convert("RGB")
    if nome:
        im = privado(im, nome, ts, tilt)
    return im


def recorta(im, w, h, ay=0.5, z=1.0):
    esc = max(w / im.width, h / im.height) * z
    r = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    x0 = (r.width - w) / 2
    y0 = (r.height - h) * ay
    return r.crop((int(x0), int(y0), int(x0) + w, int(y0) + h))


def polaroide(im, w, h, legenda):
    f = recorta(im, w, h)
    c = Image.new("RGBA", (w + 60, h + 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((12, 12, w + 60, h + 150), fill=MAR)
    d.rectangle((0, 0, w + 48, h + 138), fill=(255, 252, 245), outline=MAR, width=6)
    c.paste(f, (24, 24))
    d.text(((w + 48) / 2, h + 82), legenda, font=E.lilita(52), fill=MAR, anchor="mm")
    return c


def fundo_foto():
    img = Image.new("RGBA", (FW, FH), CREME + (255,))
    rnd = random.Random(3)
    d = ImageDraw.Draw(img)
    for _ in range(60):
        x, y, s = rnd.uniform(0, FW), rnd.uniform(0, FH), rnd.uniform(8, 16)
        c = tuple(int(v + (255 - v) * 0.55) for v in rnd.choice([LAR, PET, AMA, ROSA, VERDE]))
        d.rounded_rectangle((x, y, x + s, y + s * 0.6), 3, fill=c)
    return img


def fotos():
    pasta = os.path.join(OUT, "conheca_becas")
    os.makedirs(pasta, exist_ok=True)
    jar, vit, bro, rota = (os.path.join(NOV, a) for a in ("20261106_150333.mp4", "20261106_150657.mp4",
                                                         "20261106_151353.mp4", "20261106_151125.mp4"))
    teto = quadro_bruto(jar, 7.6, "jardim", TILT["ceu"])
    telas = []
    # 1 capa: o teto de guarda-chuvinhas em tela cheia
    img = recorta(teto, FW, FH, ay=0.12, z=1.0).convert("RGBA")
    g = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    for y in range(700, FH):
        gd.line((0, y, FW, y), fill=(25, 15, 8, int(200 * (y - 700) / (FH - 700))))
    img.alpha_composite(g)
    E.cola(img, E.pilula("A GENTE FOI CONFERIR:", 44, AMA, MAR, fonte_titulo=True), FW / 2, 930, -2)
    E.cola(img, E.titulo("VOCÊ JÁ CONHECE\nO BECA’S CAFÉ?", 104, BR, larg_max=980), FW / 2, 1110, -1)
    E.cola(img, TB.logo_becas(120), FW - 150, 120, 4)
    telas.append(img)
    # 2..4 polaroides
    for k, (im, leg, tit_, frase, cor) in enumerate([
        (quadro_bruto(rota, 44.6, "rota"), "O PORTÃO", "CHEGOU, ENTROU!",
         "A plaquinha redonda do Beca’s fica\nno portão branco, bem no centro de Mauá.", PET),
        (quadro_bruto(vit, 4.2, "vitrine"), "A VITRINE", "DÁ VONTADE DE TUDO",
         "Tortas, brownies e cookies:\nescolher um só é o desafio.", LAR),
        (quadro_bruto(bro, 1.2, "brownie"), "O BROWNIE", "APROVADO!",
         "Brownie com chantilly e morango.\nA Jéssica testou (e aprovou).", ROSA),
    ]):
        img = fundo_foto()
        E.cola(img, E.titulo(tit_, 88, cor, larg_max=980), FW / 2, 92, -1.5)
        E.cola(img, polaroide(im, 580, 780, leg), FW / 2, 680, (-3, 2.5, -2)[k])
        E.cola(img, E.texto(frase, 36, MAR, 800, larg_max=960, entre=1.3), FW / 2, 1235, 0)
        telas.append(img)
    # 5 o convite
    img = fundo_foto()
    balanco(img, 0.6, alturas=(70, 130, 50, 115, 85, 150))
    E.cola(img, E.titulo("E NO DIA 20/11\nTEM JOGO LÁ!", 96, LAR, larg_max=980), FW / 2, 420, -1.5)
    E.cola(img, card_convite(920, "reserve"), FW / 2, 860, 1)
    E.cola(img, E.pilula("SALVA E MANDA PRA QUEM VAI COM VOCÊ!", 36, AMA, MAR, fonte_titulo=True), FW / 2, 1255, -1)
    telas.append(img)
    for k, im in enumerate(telas):
        im.convert("RGB").save(os.path.join(pasta, f"{k + 1:02d}.png"))
    w = 300
    sh = Image.new("RGB", (len(telas) * (w + 10) + 10, int(w * FH / FW) + 20), (240, 236, 228))
    for k, im in enumerate(telas):
        sh.paste(im.convert("RGB").resize((w, int(w * FH / FW)), Image.LANCZOS), (10 + k * (w + 10), 10))
    sh.save(os.path.join(pasta, "previa.jpg"), quality=88)
    print("ok", pasta)


# ======================================================================== main
PECAS = {"revela": (r_quadro, lambda: R_DUR, R_PL + [R_FUNDO], r_audio),
         "chegar": (c_quadro, lambda: C_DUR, C_PL, c_audio),
         "gostinho": (g_quadro, lambda: G_DUR, G_PL, g_audio)}


_QF = None


def render(fi):
    return _QF(fi / FPS).tobytes()


def main():
    global _QF
    peca = sys.argv[1]
    if peca == "fotos":
        fotos()
        return
    qf, durf, planos, audiof = PECAS[peca]
    _QF = qf
    K.prepara([p.trecho() for p in planos])
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]]
        K.folha([qf(x) for x in ts], os.path.join(OUT, f"frames_{peca}.jpg"))
        print("ok", durf())
        return
    ev, mus, mg = audiof()
    dur = durf()
    com, sem = os.path.join(OUT, f"{peca}_com.wav"), os.path.join(OUT, f"{peca}_sem.wav")
    S.grava(com, dur, ev, mus, musica_ganho=mg, fx_ganho=0.8)
    S.grava(sem, dur, ev, None, fx_ganho=0.8)
    K.entrega(peca, dur, render, com, sem)
    print("ok", peca, dur)


if __name__ == "__main__":
    main()
