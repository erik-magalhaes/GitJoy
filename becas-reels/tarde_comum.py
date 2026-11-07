#!/usr/bin/env python3
"""ROTEIRO DELE (7/nov/2026): "uma tarde comum → uma experiência diferente", com as gravações do Beca’s + os vídeos dos
jogos na mesa, transições criativas entre a cafeteria e os jogos (match cut: o objeto redondo do café vira o do jogo).

    0     GANCHO (pergunta dele): "Você é do time que vai à cafeteria só pelo café... ou também pela diversão?"
    1     o ambiente mais bonito: "Já imaginou transformar uma tarde comum em uma experiência diferente?"
    2     o desejo (cardápio, vitrine, cookies, bolo nuvem): "Um café gostoso..."
    3     a virada (a placa redonda com a xícara → íris abre na mesa do Art Society; a mesinha vazia do pátio recebe
          as caixas): "...uma mesa cheia de possibilidades..."
    4     a experiência (bolo nuvem → íris → carta de doce do Sushi Go; Unlock abrindo, mãos nas peças do Sky Team,
          fichas do Critter Kitchen, cartas do Canvas, Take Time): "...e boas histórias pra contar!"
    5     os dois universos juntos (tela dividida café/jogo) + "Café, jogos e boas companhias. Você vem?" + convite.

Não há gravação de XÍCARA sendo servida: a "xícara" é a do logo na placa redonda do Beca’s (avisar).
Reels (padrão) e Stories (`--stories`, espaço do adesivo de link no meio).
NARRAÇÃO dele (7/nov): `narracao_tarde/frase_NN.wav` (tratar_tarde.py). Cada fala entra no começo do seu bloco; o gancho,
a tela dividida e o convite esticam para caber a fala; a trilha abaixa sob a voz. Fala que falta: o bloco fica só com texto.
`--sem-legenda` tira os textos falados da tela.

    /usr/bin/python3 tarde_comum.py --frame 1 5 9 13 15 20 24 30 34
    /usr/bin/python3 tarde_comum.py [--stories]
"""
import json
import math
import os
import sys
import wave

import numpy as np

from PIL import Image, ImageDraw, ImageFilter

import no_becas as NB
import cafe_e_jogo as CJ
from no_becas import K, S, E, W, H, FPS, MAR, PET, LAR, AMA, BR, Plano, etq, tit, out_back, ease

OUT = K.OUT
FMT = "reels"
P = Plano

# (plano, íris no começo: (cx, cy) do objeto redondo do plano ANTERIOR, ou None)
CENAS = [  # 2ª versão (7/nov): ele achou repetido → cada trecho só UMA vez, com a parede, a chegada e o bolo nuvem
    # 0 gancho: a parede pintada do café
    (P("parede", 0.2, 3.2, 1.0, z=(1.0, 1.08), ay=0.4), None),  # estica para a fala 1 (mais abaixo)
    # 1 ambiente: chegando da rua (bandeira), o pátio de guarda-chuvinhas, o teto do salão
    (P("rota", 36.6, 2.4, 2.0, z=(1.0, 1.04)), None),
    (P("rota", 49.6, 2.0, 1.0, z=(1.0, 1.06)), None),
    (P("parede", 5.2, 1.8, 1.2), None),
    # 2 desejo
    (P("menu", 1.0, 1.0, 0.6, z=(1.08, 1.0)), None),
    (P("vitrine", 2.4, 1.0, 1.0, z=(1.0, 1.05)), None),
    (P("vitrine", 8.2, 1.0, 1.0, z=(1.08, 1.0)), None),
    (P("bolo2", 1.0, 1.2, 1.2), None),
    (P("bolo2", 5.0, 1.2, 1.0), None),  # a Jéssica comendo o bolo nuvem
    # 3 virada
    (P("rota", 43.6, 1.4, 0.7, z=(1.0, 1.05)), None),
    (P("art", 0.0, 1.6, 1.0, z=(1.06, 1.0)), (525, 830)),  # placa redonda (xícara do logo) → íris
    (P("passaporte", 0.3, 1.2, 1.0, z=(1.0, 1.05)), None),
    # 4 experiência
    (P("menu", 3.4, 1.0, 0.7, z=(1.0, 1.06)), None),  # 7/nov: no lugar da mãozinha com a colher, a página do cardápio
    (P("sushi", 2.0, 1.4, 1.0), (540, 960)),  # cardápio → íris → carta de doce
    (P("unlock", 0.3, 2.0, 1.2), None),
    (P("sky_dados", 4.0, 1.6, 1.5), None),
    (P("critter", 2.0, 1.4, 1.0), None),
    (P("canvas", 2.0, 1.5, 1.2), None),
    (P("taketime2", 1.0, 1.2, 1.0), None),
]
K.CLIPES["parede"] = (os.path.join(NB.NOV, "20261106_150726.mp4"), "BECA’S")
K.CLIPES["bolo2"] = (os.path.join(NB.NOV, "20261106_151311.mp4"), "BECA’S")
K.CLIPES["menu"] = (os.path.join(NB.NOV, "20261106_150936.mp4"), "BECA’S")
NARR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "narracao_tarde")


def voz(n):
    p = os.path.join(NARR, f"frase_{n:02d}.wav")
    return p if os.path.exists(p) else None


def dur_wav(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


def dvoz(n):
    return dur_wav(voz(n)) if voz(n) else 0.0


PAL = json.load(open(os.path.join(NARR, "palavras.json"))) if os.path.exists(os.path.join(NARR, "palavras.json")) else {}


def palavra(n, w, padrao):
    """Início (s) da 1ª palavra w na fala n, ou padrao."""
    for a, _, x in PAL.get(f"{n:02d}", []):
        if x.lower().strip(",.?!") == w:
            return a
    return padrao


V1 = 0.2  # a fala 1 começa aqui
if voz(1):  # o gancho dura a fala inteira + respiro
    CENAS[0][0].d = max(CENAS[0][0].d, V1 + dvoz(1) + 0.4)
PL = [c for c, _ in CENAS]
INI = NB.inicios(PL)
VID = sum(p.d for p in PL)
JUNTOS = max(2.4, 0.1 + dvoz(6) + 0.4)  # cena 5: tela dividida (fala 6)
J_CAFE = P("bolo2", 22.0, JUNTOS, 0.65)  # a Jéssica rindo com a colherada
J_JOGO = P("sushi", 4.4, JUNTOS, 1.0)
T_FIM = VID + JUNTOS
V7 = 0.15  # a fala 7 começa no convite
DUR = T_FIM + max(5.6, V7 + dvoz(7) + 1.0)
# quando cada fala começa (tempo do vídeo)
VOZ_EM = {1: V1, 2: INI[1] + 0.25, 3: INI[4] + 0.25, 4: INI[10] + 0.15, 5: INI[13] + 0.3, 6: VID + 0.1, 7: T_FIM + V7}
T_OU = V1 + palavra(1, "ou", 1.4) if voz(1) else 1.6  # "...ou também pela diversão?"
T_VEM = T_FIM + V7 + palavra(7, "você", -0.05) if voz(7) else T_FIM + 0.1
T_CARD = T_FIM + V7 + palavra(7, "tarde", 0.2) if voz(7) else T_FIM + 0.35
LEG = True
IRIS = 0.4
MESA = NB.G_MESA
CAIXAS = NB.G_CAIXAS

# legendas: (início, fim, texto, tamanho, cor)
TEXTOS = [
    (0.15, INI[1], "VOCÊ É DO TIME QUE VAI\nÀ CAFETERIA SÓ PELO CAFÉ...", 70, BR),
    (INI[1] + 0.2, INI[4], "JÁ IMAGINOU TRANSFORMAR\nUMA TARDE COMUM EM UMA\nEXPERIÊNCIA DIFERENTE?", 66, BR),
    (INI[4] + 0.2, INI[10], "UM CAFÉ GOSTOSO...", 92, AMA),
    (INI[10] + 0.15, INI[12], "...UMA MESA CHEIA\nDE POSSIBILIDADES...", 84, AMA),
    (INI[13] + 0.3, VID, "...E BOAS HISTÓRIAS\nPRA CONTAR!", 88, AMA),
]


def iris(a, b, u, cx, cy):
    """b aparece dentro de um círculo que cresce a partir de (cx, cy), com aro branco."""
    r = ease(min(1.0, u)) * math.hypot(max(cx, W - cx), max(cy, H - cy)) + 1
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    out = Image.composite(b, a, m)
    ImageDraw.Draw(out).ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 250, 240), width=max(2, int(14 * (1 - u))))
    return out


def video(t):
    k = max(i for i in range(len(PL)) if INI[i] <= t) if t < VID else len(PL) - 1
    u = t - INI[k]
    im = PL[k].quadro(u)
    ir = CENAS[k][1]
    if ir and u < IRIS:
        ant = PL[k - 1].quadro(PL[k - 1].d - 0.01)
        im = iris(ant, im, u / IRIS, *ir)
    return im, k, u


def legenda(img, t):
    if not LEG:
        return
    for a, b, txt, s, cor in TEXTOS:
        if a <= t < b:
            n = txt.count("\n") + 1
            K.escurece(img, 1260 - 55 * n, 1730, 140)
            K.poe(img, tit(txt, s, cor), W / 2, 1490 - 30 * (n - 1), t, a, -1.5)


def quadro(t):
    if t < VID:
        img, k, u = video(t)
        legenda(img, t)
        if t < INI[1] and LEG:
            K.poe(img, etq("...OU TAMBÉM PELA DIVERSÃO?", 54, AMA, MAR), W / 2, 1660, t, T_OU, 2)
        K.marca(img)
        return img.convert("RGB")
    if t < T_FIM:
        u = t - VID
        a, b = J_CAFE.quadro(u), J_JOGO.quadro(u)
        img = Image.new("RGBA", (W, H))
        img.paste(CJ.metade(a, 0.15), (0, 0))
        img.paste(CJ.metade(b, 0.5), (0, CJ.HM))
        ImageDraw.Draw(img).rectangle((0, CJ.HM - 7, W, CJ.HM + 7), fill=MAR)
        if LEG:
            K.poe(img, tit("CAFÉ, JOGOS E\nBOAS COMPANHIAS.", 90, BR), W / 2, CJ.HM, t, VID + 0.1, -1.5)
        K.marca(img)
        return img.convert("RGB")
    img = PL[0].quadro(1.0).filter(ImageFilter.GaussianBlur(12))
    u = t - T_FIM
    NB.escuro(img, min(140, u * 400))
    NB.balanco(img, t)
    if FMT == "stories":
        K.poe(img, tit("VOCÊ VEM?", 130, AMA), W / 2, 400, t, T_VEM, -2)
        K.poe(img, NB.card_convite(), W / 2, 880, t, T_CARD, 1)
        NB.linha_link(img, t, T_FIM + 0.9, 1200)
        K.poe(img, etq("MANDA PRA QUEM VAI COM VOCÊ!", 40, BR, MAR), W / 2, 1660, t, T_FIM + 1.1, -1.5)
    else:
        K.poe(img, tit("VOCÊ VEM?", 130, AMA), W / 2, 520, t, T_VEM, -2)
        K.poe(img, NB.card_convite(), W / 2, 1020, t, T_CARD, 1)
        K.poe(img, etq("COMENTA: TIME DO CAFÉ OU DA DIVERSÃO?", 38, BR, MAR), W / 2, 1440, t, T_FIM + 1.0, -1.5)
    return img.convert("RGB")


def audio():
    ev = [(0.15, S.cartao(), 0.35), (1.6, S.plim(), 0.4)]
    for a, *_ in TEXTOS[1:]:
        ev.append((a, S.cartao(), 0.3))
    for k, (_, ir) in enumerate(CENAS):
        if ir:
            ev.append((INI[k], S.sopro(0.4), 0.45))
    ev += [(INI[15], S.dado(), 0.35), (VID, S.sopro(0.3), 0.35), (VID + 0.1, S.cartao(), 0.3),
           (T_FIM, S.sino(), 0.45), (T_CARD, S.cartao(), 0.4), (T_FIM + 1.0, S.cartao(), 0.3)]
    return ev, S.musica_cafe(DUR + 0.5), 0.45


def le_wav(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
        return a.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else a


def faixa_voz():
    n = int(DUR * S.SR)
    vz = np.zeros(n)
    for k, t0 in VOZ_EM.items():
        if voz(k):
            S.add(vz, le_wav(voz(k)), t0, 1.0)
    return vz


def poe_voz(path, vz, g=0.95):
    """Soma a voz por cima do wav já mixado (sem passar pela saturação da mixagem) e limita o pico."""
    with wave.open(path) as w:
        st = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float).reshape(-1, 2) / 32768
    m = st + vz[:len(st), None] * g
    m = m / max(1.0, np.abs(m).max() / 0.95)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(S.SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


_QF = quadro


def render(fi):
    return quadro(fi / FPS).tobytes()


def main():
    global FMT, LEG
    FMT = "stories" if "--stories" in sys.argv else "reels"
    LEG = "--sem-legenda" not in sys.argv
    nome = "tarde_comum" + ("_stories" if FMT == "stories" else "") + ("" if LEG else "_sem_legenda")
    K.prepara([p.trecho() for p in PL + [J_CAFE, J_JOGO]])
    os.makedirs(OUT, exist_ok=True)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        K.folha([quadro(x) for x in ts], os.path.join(OUT, f"frames_{nome}.jpg"))
        print("ok", DUR, [round(x, 2) for x in INI], {k: round(v, 2) for k, v in VOZ_EM.items()})
        return
    ev, mus, mg = audio()
    com, sem = os.path.join(OUT, f"{nome}_com.wav"), os.path.join(OUT, f"{nome}_sem.wav")
    vz = faixa_voz()
    if vz.any():  # trilha abaixa quando tem voz
        env = np.convolve((np.abs(vz) > 0.02).astype(float), np.ones(int(0.3 * S.SR)) / int(0.3 * S.SR), "same")
        mus = mus[:len(vz)] * (1 - 0.7 * np.clip(env * 3, 0, 1))
    S.grava(com, DUR, ev, mus, musica_ganho=mg, fx_ganho=0.8)
    S.grava(sem, DUR, ev, None, fx_ganho=0.8)
    if vz.any():
        poe_voz(com, vz)
        poe_voz(sem, vz)
    K.entrega(nome, DUR, render, com, sem)
    print("ok", nome, DUR)


if __name__ == "__main__":
    main()
