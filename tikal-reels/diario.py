#!/usr/bin/env python3
"""Tikal, "DIÁRIO DA EXPEDIÇÃO" (10/nov/2026, pedido dele): o caderno realista (caderno.py/papel.py), mas SÓ com as
imagens e POUCAS anotações; ele narra em 1ª pessoa, como quem documenta a expedição. Falas novas (`TEXTO`), gravador
`gravador/Gravar_narracao_TikalDiario.html` (arquivos `tikaldiario_narracao_NN`). Sem narração, cada página dura o
tempo estimado da fala (14 letras/s + folga); com `narracao_diario/timeline.json` as páginas esticam para a fala real.
Regras conferidas no manual (ver CLAUDE.md). Nada se mexe: as fotos/recortes só aparecem; a caneta escreve pouco.

    /usr/bin/python3 diario.py --frame 2 8 15 ...   # out/frames_diario.jpg
    /usr/bin/python3 diario.py                      # out/diario_previa_final.mp4 (sem voz, legenda das falas)
"""
import argparse
import json
import math
import os
import sys

from PIL import Image

import caderno as C
import papel as PP
import tikal as T
from caderno import (escreve, poe, poe_foto, recorte, postit, carimbo, carimba, caneta, circulo, seta, caixinhas,
                     sublinha, linha, AZUL_C, VERM_C, GRAFITE)
from pecas import W, H
from tikal import E, S, FPS, encode, final_loudness, seg

OUT = T.OUT
TEXTO = [
    "Diário de expedição, dia um. Cheguei a Tikal… e dizem que tem templos perdidos nessa selva.",
    "A cada turno, eu exploro um pedaço novo: um templo, uma ruína com tesouro… ou um vulcão.",
    "Tenho dez pontos de ação por turno. Pôr um explorador no acampamento custa um; cada pedra do caminho, mais um.",
    "Achei um templo! Com dois pontos, escavo mais um andar, e ele passa a valer mais.",
    "Nas ruínas, cavar um tesouro custa três. Um vale um, um par vale três, três iguais valem seis.",
    "Mas o templo só conta pra quem tem mais exploradores nele… e o meu chefe vale por três.",
    "Pus um guardião por cinco pontos: o templo é meu até o fim. E troquei um tesouro com o rival… ele não pôde "
    "recusar.",
    "Quando aparece um vulcão, é hora de contar: os templos que eu domino e os meus tesouros. No fim, mais pontos "
    "vence.",
    "Fim do diário… por enquanto. E você, escavaria templos ou roubaria tesouros? Comenta aí! E aluga o Tikal na Sua "
    "Vez, o link tá na bio.",
]
NOMES = ["gancho", "hexagono", "pa", "templo", "tesouro", "maioria", "guardiao", "vulcao", "cta"]
CPS, FOLGA = 15.5, 0.8
TELA_FINAL = 3.2  # a tela final fica depois da última fala


def linha_do_tempo():
    tl = os.path.join(T.P.ROOT, "narracao_diario", "timeline.json")
    if os.path.exists(tl) and "--previa" not in sys.argv:
        return json.load(open(tl))
    t, out = 0.0, []
    for k, (n, txt) in enumerate(zip(NOMES, TEXTO)):
        d = len(txt) / CPS + FOLGA + (TELA_FINAL if n == "cta" else 0)
        out.append({"cena": n, "ini": t, "dur": d, "fala": None})
        t += d
    return out


# o tikal.py desenha a legenda e acha a cena pela TL/TEXTO dele: troca pelas do diário
T.TEXTO[:] = TEXTO
T.TL[:] = linha_do_tempo()
T.DUR = T.TL[-1]["ini"] + T.TL[-1]["dur"]
DUR = T.DUR
_cta = T.TL[-1]
T.T_COMENTA = _cta.get("t_comenta", _cta["dur"] - TELA_FINAL)
COM_VOZ = all(c.get("fala") for c in T.TL)


# ------------------------------------------------------------------------------------------------ páginas
def titulo(img, txt, u):
    escreve(img, txt, 185, 0, seg(u, 0.05, 0.05 + len(txt) / 20), AZUL_C, 76, 640)


def pg_gancho(img, t, u, dur):
    titulo(img, "Dia 1 · Tikal", u)
    poe_foto(img, "capa", 560, 800, 2, u, 0.0, 800, 900, 1)
    poe(img, recorte("logo:x", 150), 760, 1420, -5, u, dur * 0.65)


def pg_hexagono(img, t, u, dur):
    titulo(img, "A selva cresce", u)
    pos = [(320, 640, -4), (790, 690, 4), (330, 1180, 3), (780, 1230, -3)]
    nomes = ["templo", "ruína", "clareira", "vulcão!"]
    tipos = ["templo", "ruina", "clareira", "vulcao"]
    passo = (dur - 0.8) / 4
    for k, ((x, y, r), nome, tp) in enumerate(zip(pos, nomes, tipos)):
        tk = 0.3 + k * passo
        poe_foto(img, tp, x, y, r, u, tk, 400, 360, k)
        escreve(img, nome, x, 0, seg(u, tk + 0.3, tk + 0.9), VERM_C if k == 3 else AZUL_C, 50, centro=True,
                base=y + 218)


def pg_pa(img, t, u, dur):
    titulo(img, "10 pontos de ação", u)
    a, b = (330, 820), (780, 820)
    poe_foto(img, "clareira", a[0], a[1], -4, u, 0.2, 380, 340, 1)
    poe_foto(img, "templo", b[0], b[1], 4, u, 0.2, 380, 340, 2)
    t_entra, t_anda = dur * 0.35, dur * 0.62
    q = seg(u, t_anda, dur - 0.5)
    for k in range(2):
        x = 525 + k * 76
        caneta(img, [(x - 24, 805), (x + 24, 803), (x + 25, 845), (x - 23, 847), (x - 24, 805)], 1, GRAFITE, 4)
    gasto = 0.0
    if u >= t_entra:
        gasto = 1.0 + 2 * q
        poe(img, recorte("meeple:vermelho", 170), b[0] if q >= 1 else a[0], a[1] - 30, -6, u, t_entra)
        escreve(img, "1", a[0], 0, seg(u, t_entra + 0.2, t_entra + 0.5), VERM_C, 110, 700, centro=True, base=a[1] + 330)
        if u > t_anda:
            pts = [(a[0] + 60 + (b[0] - a[0] - 120) * s_, a[1] - 210 - 70 * math.sin(s_ * math.pi))
                   for s_ in [i / 39 for i in range(40)]]
            caneta(img, pts, q, GRAFITE, 4)
            escreve(img, "+1 por pedra", 540, 0, seg(u, t_anda + 0.3, t_anda + 1.0), VERM_C, 64, 650, centro=True,
                    base=a[1] + 330)
    caixinhas(img, gasto, 190, 1440)


def pg_templo(img, t, u, dur):
    titulo(img, "Dia 2 · achei um templo!", u)
    poe_foto(img, "templo", 540, 860, -2, u, 0.0, 700, 620, 2)
    k1, k2 = dur * 0.4, dur * 0.62
    for j, kk in enumerate((k1, k2)):
        poe(img, T.andar_templo(5 + j, 200), 540, 820, 0, u, kk)
    valor = 4 + (u >= k1) + (u >= k2)
    escreve(img, " → ".join(str(v) for v in range(4, valor + 1)).replace(" → ", "  >  "), 260, 0, 1, VERM_C, 96, 700,
            base=1440)
    escreve(img, "2 PA por andar", 260, 0, seg(u, k1 + 0.2, k1 + 0.9), AZUL_C, 62, base=1560)


def pg_tesouro(img, t, u, dur):
    titulo(img, "Ruínas e tesouros", u)
    poe_foto(img, "ruina", 380, 620, -4, u, 0.0, 520, 460, 3)
    poe(img, recorte("tesouro:4", 170), 830, 560, 6, u, dur * 0.2)
    escreve(img, "3 PA", 830, 0, seg(u, dur * 0.2 + 0.2, dur * 0.2 + 0.6), VERM_C, 74, 700, centro=True, base=740)
    t0 = dur * 0.5
    grupos = [([4], "1"), ([4, 4], "3"), ([4, 4, 4], "6")]
    for j, (fichas, pts_) in enumerate(grupos):
        tj = t0 + j * (dur - t0 - 0.6) / 3
        y = 1080 + j * 175
        for i, f in enumerate(fichas):
            poe(img, recorte(f"tesouro:{f}", 140), 260 + i * 110, y, (i - 1) * 7, u, tj + i * 0.12)
        escreve(img, "= " + pts_, 640, 0, seg(u, tj + 0.3, tj + 0.6), VERM_C, 100, 700, base=y + 40)


def pg_maioria(img, t, u, dur):
    titulo(img, "Dia 3 · quem manda no templo?", u)
    poe_foto(img, "templo", 540, 860, 2, u, 0.0, 700, 620, 4)
    t_chefe = dur * 0.55
    for k, (x, y) in enumerate([(760, 900), (850, 820), (820, 1000)]):
        poe(img, recorte("meeple:azul", 140), x, y, 4, u, 0.3 + 0.2 * k)
    for k, (x, y) in enumerate([(330, 900), (410, 1000)]):
        poe(img, recorte("meeple:vermelho", 140), x, y, -4, u, 0.9 + 0.2 * k)
    poe(img, recorte("meeple:vermelho", 210), 300, 730, -6, u, t_chefe)
    if u > t_chefe:
        caneta(img, circulo(300, 730, 125, 140, 5), seg(u, t_chefe + 0.2, t_chefe + 0.6))
        escreve(img, "chefe = 3", 190, 0, seg(u, t_chefe + 0.5, t_chefe + 1.0), VERM_C, 84, 700, base=470)
    carimba(img, carimbo("5 × 3", 110), W / 2, 1450, -4, u, t_chefe + 1.0)


def pg_guardiao(img, t, u, dur):
    meio = dur * 0.45
    if u < meio:
        titulo(img, "Guardião", u)
        poe_foto(img, "templo", 540, 860, -2, u, 0.0, 700, 620, 5)
        poe(img, recorte("meeple:vermelho", 220), 540, 800, 0, u, 0.4)
        escreve(img, "5 PA", 860, 0, seg(u, 0.8, 1.2), VERM_C, 84, 700, centro=True, base=520)
        carimba(img, carimbo("GUARDADO", 100), 540, 1440, -8, u, meio * 0.6)
        return
    v = u - meio
    titulo(img, "Troca com o rival", v)
    poe(img, recorte("meeple:vermelho", 280), 300, 700, -5, v, 0.0)
    poe(img, recorte("meeple:azul", 280), 780, 700, 5, v, 0.0)
    trocou = v >= 1.6
    for f, x0, x1 in ((1, 300, 780), (5, 780, 300)):
        poe(img, recorte(f"tesouro:{f}", 190), x1 if trocou else x0, 1110, 0, v, 0.2)
    seta(img, (400, 1250), (690, 1250), seg(v, 0.6, 1.2), VERM_C, -0.25)
    seta(img, (690, 970), (400, 970), seg(v, 0.8, 1.4), VERM_C, -0.25)
    escreve(img, "3 PA", W / 2, 0, seg(v, 1.4, 1.8), VERM_C, 84, 700, centro=True, base=1480)


def pg_vulcao(img, t, u, dur):
    titulo(img, "Vulcão!", u)
    poe_foto(img, "vulcao", 540, 780, -3, u, 0.0, 640, 560, 6)
    carimba(img, carimbo("CONTAGEM!", 100), 760, 1150, 9, u, 0.8)
    t1 = dur * 0.35
    poe_foto(img, "templo", 280, 1400, -6, u, t1, 240, 210, 7)
    poe(img, recorte("tesouro:4", 130), 560, 1400, 4, u, t1 + 0.6)
    poe(img, recorte("tesouro:1", 130), 660, 1420, -6, u, t1 + 0.7)
    escreve(img, "+", 430, 0, seg(u, t1 + 0.5, t1 + 0.7), VERM_C, 110, 700, centro=True, base=1440)


def pg_cta(img, t, u, dur):
    if u < T.T_COMENTA:
        titulo(img, "Fim do diário... por enquanto", u)
        poe(img, recorte("meeple:vermelho", 300), 320, 900, -6, u, dur * 0.12)
        poe(img, recorte("tesouro:0", 300), 780, 900, 8, u, dur * 0.12)
        escreve(img, "ou", 540, 0, seg(u, dur * 0.15, dur * 0.2), VERM_C, 96, 700, centro=True, base=930)
        carimba(img, carimbo("COMENTA AQUI!", 100), W / 2, 1370, -4, u, dur * 0.3)
        return
    v = u - T.T_COMENTA
    img.alpha_composite(E.logo(200), (W - 250, 70))
    poe_foto(img, "caixa", 330, 760, -4, v, 0.0, 420, 460, 8)
    linhas_ = [("Alugue o Tikal", VERM_C, 82), ("2 a 4 jogadores", AZUL_C, 62), ("90 min", AZUL_C, 62),
               ("5 dias de jogo", AZUL_C, 62)]
    for k, (li, cor, s) in enumerate(linhas_):
        escreve(img, li, 600, 5 + 2 * k, 1, cor, s, 650 if k == 0 else 520)
    escreve(img, "Reserve online · retire em Mauá\nou receba em casa", 190, 15, 1)
    carimba(img, carimbo("LINK NA BIO · @SUAVEZ_BG", 62, AZUL_C), W / 2, 1470, -3, v, 0.0)


PG = {"gancho": pg_gancho, "hexagono": pg_hexagono, "pa": pg_pa, "templo": pg_templo, "tesouro": pg_tesouro,
      "maioria": pg_maioria, "guardiao": pg_guardiao, "vulcao": pg_vulcao, "cta": pg_cta}


def quadro(t):
    cena, u, dur = T.cena_em(t)
    k = NOMES.index(cena)
    img = PP.folha(k).copy()
    PG[cena](img, t, u, dur)
    if not (cena == "cta" and u >= T.T_COMENTA):
        img.alpha_composite(E.logo(170), (W - 205, 40))
    T.legenda(img, t)
    return img.convert("RGB")


def render(fi):
    return quadro(fi / FPS).tobytes()


def cues():
    ev = []
    for i, c in enumerate(T.TL):
        ini = c["ini"]
        if i > 0:
            ev.append((ini, C.folha_vira(), 0.45))
        ev.append((ini + 0.1, C.rabisco(0.5, i), 0.3))
        ev.append((ini + 0.05, C.papel_pousa(), 0.4))
    ev.append((T.TL[-1]["ini"] + T.T_COMENTA * 0.3, T.baque(0.3), 0.5))
    return ev


def mixa_voz(path):
    """Trilha + efeitos (S.grava) abaixando sob a voz dele; a voz entra depois, sem saturar."""
    import wave
    import numpy as np
    from scipy.ndimage import uniform_filter1d
    base = path.replace(".wav", "_base.wav")
    S.grava(base, DUR, cues(), C.trilha(DUR + 0.5), musica_ganho=0.36, fx_ganho=0.8)
    with wave.open(base) as w:
        b = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2)[:, 0].astype(np.float64) / 32768
    SR = S.SR
    voz = np.zeros(len(b))
    for c in T.TL:
        with wave.open(os.path.join(T.P.ROOT, "narracao_diario", f"frase_{c['fala']:02d}.wav")) as w:
            v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        i0 = int(c["voz_em"] * SR)
        v = v[:max(0, len(voz) - i0)]
        voz[i0:i0 + len(v)] += v
    env = uniform_filter1d((np.abs(voz) > 0.02).astype(float), int(0.25 * SR))
    duck = 1 - 0.72 * np.clip(env * 3, 0, 1)
    mix = b * duck * 0.8 + voz * 0.95
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.95
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--sem-legenda", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frame:
        ims = [quadro(x) for x in a.frame]
        cols = min(6, len(ims))
        rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows))
        for k, im in enumerate(ims):
            sh.paste(im.resize((360, 640), Image.LANCZOS), (360 * (k % cols), 640 * (k // cols)))
        sh.save(os.path.join(OUT, "frames_diario.jpg"), quality=88)
        print("ok", round(DUR, 1), [round(c["ini"], 1) for c in T.TL])
        return
    if COM_VOZ:
        nome = "diario_sem_legenda" if a.sem_legenda else "diario_legendado"
        com = os.path.join(OUT, "diario_voz.wav")
        if not os.path.exists(com) or a.sem_legenda is False:
            mixa_voz(com)
    else:
        nome = "diario_previa"
        com = os.path.join(OUT, f"{nome}_com.wav")
        S.grava(com, DUR, cues(), C.trilha(DUR + 0.5), musica_ganho=0.36, fx_ganho=0.8)
    n = int(round(DUR * FPS))
    base = os.path.join(OUT, f"{nome}.mp4")
    encode(base, render, list(range(n)), com)
    final_loudness(base, base.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
