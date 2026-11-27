#!/usr/bin/env python3
""""QUAL JOGO EU DARIA DE PRESENTE PRA..." (Jéssica, gravado em 23/nov, 7 vídeos VID_20261123_* → brutos/nov23/).
Ela sorteia papelzinhos (mãe, Eric, irmão, sogra, sobrinha, cunhada) e diz o jogo + o porquê. Ela gravou fora de casa,
SEM as caixas: a caixa OFICIAL entra embaixo à direita quando ela fala o nome. Cortes pelas palavras do Whisper (só as
falas boas; "Vamos pro próximo" e as pausas de abrir o papel saem), punch-in alternado nos cortes, etiqueta de presente
"PRA:" no alto quando ela lê o papel, legenda palavra a palavra, pisca-pisca no alto (estilo do Natal), "comenta" e tela
final no fundo vermelho natalino.

    /usr/bin/python3 presente.py --frame 2 20 40 [..]
    /usr/bin/python3 presente.py           # out/presente_{legendado,sem_legenda}_final.mp4
"""
import json
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import domingo as D
import kit as K
import sons as S
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA
from motor import FPS, ffmpeg, encode
from base import final_loudness

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
BR_ = os.path.join(ROOT, "brutos", "nov23")
OUT = D.OUT
CACHE = os.path.join(OUT, "_cache_presente")
VERDE = (24, 110, 66)
SR = 44100
ARQ = {k: os.path.join(BR_, f"VID_20261123_{k}.mp4") for k in
       ("065924_439", "070049_321", "070245_594", "070457_044", "070814_536", "071027_220", "071525_306")}
AC = os.path.join(REPO, "hobby-reels", "assets", "acervo")
T10 = os.path.join(REPO, "gravados-reels", "assets", "top10")
JOGO_ERIK = None   # o "Takta" que ela fala pro Eric: esperando o nome certo (o Whisper ouve "Takta"; não está no site)

# blocos: (pessoa na etiqueta, caixa, nome do jogo, [(arquivo, ini, fim)], palavra que faz a caixa aparecer)
BLOCOS = [
    (None, None, None, [("065924_439", 1.62, 4.45), ("065924_439", 4.62, 7.15), ("065924_439", 11.5, 13.75),
                        ("065924_439", 15.6, 20.95), ("065924_439", 30.2, 31.2)], None),
    ("MINHA MÃE", os.path.join(AC, "art_society.png"), "ART SOCIETY",
     [("070049_321", 1.5, 3.55), ("070049_321", 6.4, 6.95), ("070049_321", 11.95, 15.5), ("070049_321", 15.95, 19.1),
      ("070049_321", 19.55, 22.95), ("070049_321", 25.5, 27.95)], "Art"),
    ("O ERIC", JOGO_ERIK, "TAKTA", [("070245_594", 5.5, 6.3), ("070245_594", 18.35, 21.95), ("070245_594", 22.65, 26.25),
                                    ("070245_594", 30.6, 36.95)], "Tacta"),
    ("MEU IRMÃO", os.path.join(AC, "hitster.png"), "HITSTER",
     [("070457_044", 5.1, 5.95), ("070457_044", 7.75, 9.95), ("070457_044", 16.95, 19.4), ("070457_044", 20.75, 21.95),
      ("070457_044", 23.05, 23.75), ("070457_044", 24.45, 26.9), ("070457_044", 27.35, 28.4),
      ("070457_044", 31.25, 32.45)], "hitster,"),
    ("MINHA SOGRA", os.path.join(T10, "flip_7_a_vinganca.png"), "FLIP 7",
     [("070814_536", 6.35, 6.95), ("070814_536", 7.85, 12.2), ("070814_536", 18.45, 19.25), ("070814_536", 20.95, 24.45),
      ("070814_536", 25.05, 29.45), ("070814_536", 30.65, 33.4), ("070814_536", 33.75, 37.1)], "Flip"),
    ("MINHA SOBRINHA", os.path.join(AC, "tapalavras.png"), "TAPALAVRAS",
     [("071027_220", 5.05, 5.8), ("071027_220", 6.45, 11.1), ("071027_220", 12.15, 13.75), ("071027_220", 14.25, 15.95),
      ("071027_220", 18.75, 21.4), ("071027_220", 24.7, 25.45)], "palavras"),
    ("MINHA CUNHADA", os.path.join(AC, "root.png"), "ROOT",
     [("071525_306", 1.75, 7.35), ("071525_306", 8.15, 10.95), ("071525_306", 14.55, 21.65),
      ("071525_306", 28.65, 30.65)], "Ruti,"),
    (None, None, None, [("071525_306", 31.05, 38.35), ("071525_306", 38.95, 42.25), ("071525_306", 43.85, 46.35),
                        ("071525_306", 46.85, 49.85), ("071525_306", 52.05, 53.15)], None),
]
CORRIGE = {"Ruti,": "Root,", "Ruti.": "Root.", "tá": "Tapalavras", "palavras": "", "hitster,": "Hitster,",
           "hitster": "Hitster", "sobro.": "sogro.", "estratégista,": "estrategista,", "Tacta,": "Takta,",
           "Cunhada.": "cunhada.", "Cunhada": "cunhada", "filmar": "", "a": "a"}

# ---------------------------------------------------------------- linha do tempo
PECAS = []   # (bloco, arquivo, ini, fim, t0 na saída)
_t = 0.0
for bi, b in enumerate(BLOCOS):
    for arq, a, z in b[3]:
        PECAS.append((bi, arq, a, z, _t))
        _t += z - a
T_FALA = _t
T_COMENTA = T_FALA
T_FIM = T_COMENTA + 3.6
DUR = T_FIM + 5.0
INI_BLOCO = {}
FIM_BLOCO = {}
for bi, arq, a, z, t0 in PECAS:
    INI_BLOCO.setdefault(bi, t0)
    FIM_BLOCO[bi] = t0 + (z - a)

TRANSC = json.load(open(os.path.join(BR_, "transc.json")))


def palavras():
    """Palavras com o tempo na SAÍDA, já corrigidas."""
    L = []
    for bi, arq, a, z, t0 in PECAS:
        ws = [w for s in TRANSC[f"VID_20261123_{arq}.wav"] for w in s["pal"]]
        for ws_, we, txt in ws:
            if a - 0.05 <= ws_ < z - 0.05:
                txt = txt.strip()
                txt = CORRIGE.get(txt, txt)
                if txt:
                    L.append((t0 + ws_ - a, t0 + min(we, z) - a, txt, bi))
    return L


PAL = palavras()


def t_caixa(bi):
    """Momento em que ela fala o nome do jogo do bloco."""
    gat = BLOCOS[bi][4]
    for bj, arq, a, z, t0 in PECAS:
        if bj != bi:
            continue
        ws = [w for s in TRANSC[f"VID_20261123_{arq}.wav"] for w in s["pal"]]
        for ws_, we, txt in ws:
            if a <= ws_ < z and txt.strip() == gat:
                return t0 + ws_ - a
    return None


# ---------------------------------------------------------------- vídeo
GRADE = "hqdn3d=3:3:4:4,eq=contrast=1.03:saturation=1.04:gamma=1.02,unsharp=5:5:0.35"


def prepara():
    os.makedirs(CACHE, exist_ok=True)
    for bi, arq, a, z, t0 in PECAS:
        pasta = os.path.join(CACHE, f"{arq}_{a:.2f}_{z:.2f}")
        if os.path.isdir(pasta) and os.listdir(pasta):
            continue
        os.makedirs(pasta)
        subprocess.run([ffmpeg(), "-v", "error", "-ss", str(a), "-t", str(z - a + 0.1), "-i", ARQ[arq], "-vf",
                        f"fps={FPS},{GRADE}", "-q:v", "2", os.path.join(pasta, "%04d.jpg")], check=True)


@lru_cache(maxsize=16)
def _abre(p):
    return Image.open(p).convert("RGB")


def quadro_video(t):
    k = max(i for i, p in enumerate(PECAS) if p[4] <= t + 1e-6)
    bi, arq, a, z, t0 = PECAS[k]
    pasta = os.path.join(CACHE, f"{arq}_{a:.2f}_{z:.2f}")
    n = len(os.listdir(pasta))
    im = _abre(os.path.join(pasta, f"{max(0, min(n - 1, int((t - t0) * FPS))) + 1:04d}.jpg"))
    if k % 2:  # punch-in alternado nos cortes (ancorado no alto, onde está o rosto)
        z_ = 1.07
        cw, ch = W / z_, H / z_
        im = im.crop((int((W - cw) / 2), int(H * 0.12 * (1 - 1 / z_)), int((W + cw) / 2),
                      int(H * 0.12 * (1 - 1 / z_) + ch))).resize((W, H), Image.BICUBIC)
    return im.convert("RGBA")


# ---------------------------------------------------------------- peças gráficas
@lru_cache(None)
def etiqueta(pessoa):
    """Etiqueta de presente (kraft) com barbante: PRA: MINHA MÃE."""
    w, h = max(560, int(E.lilita(70).getlength(pessoa)) + 160), 190
    im = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(60 + 10, 12), (w + 10, 12), (w + 10, h + 12), (60 + 10, h + 12), (10, h / 2 + 12)],
                               fill=(60, 30, 15, 150))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    d = ImageDraw.Draw(im)
    d.polygon([(60, 0), (w, 0), (w, h), (60, h), (0, h / 2)], fill=(222, 190, 140), outline=MAR, width=5)
    d.ellipse((36, h / 2 - 14, 64, h / 2 + 14), fill=BR, outline=MAR, width=4)
    d.text((110, 62), "PRA:", font=E.fig(46, 900), fill=VERDE, anchor="lm")
    d.text((110, 128), pessoa, font=E.lilita(70), fill=D.VERM, anchor="lm",
           stroke_width=3, stroke_fill=MAR)
    return im


@lru_cache(None)
def caixa_presente(path, nome):
    """Caixa oficial com laço vermelho e o nome numa pílula."""
    cx = Image.open(path).convert("RGBA")
    cx = cx.crop(cx.getbbox())
    h = 500
    cx = cx.resize((int(cx.width * h / cx.height), h), Image.LANCZOS)
    if cx.width > 520:
        cx = cx.resize((520, int(cx.height * 520 / cx.width)), Image.LANCZOS)
    pil = E.pilula(nome, 46, VERDE, BR, fonte_titulo=True)
    w = max(cx.width, pil.width) + 40
    im = Image.new("RGBA", (w, cx.height + pil.height + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, 110), (int(w / 2 - cx.width / 2) + 14, 18), cx.getchannel("A"))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    im.alpha_composite(cx, (int(w / 2 - cx.width / 2), 0))
    im.alpha_composite(pil, (int(w / 2 - pil.width / 2), cx.height - 10))
    return im


@lru_cache(None)
def luzes():
    return D._luzes(0), D._luzes(1)


@lru_cache(None)
def gancho():
    return K.titulo("QUAL JOGO EU DARIA\nDE PRESENTE PRA...", 92, AMA)


def _grupos():
    G, cur = [], []
    for p in PAL:
        if cur and (len(cur) == 3 or p[3] != cur[-1][3] or p[0] - cur[-1][1] > 0.6):
            G.append(cur)
            cur = []
        cur.append(p)
    if cur:
        G.append(cur)
    return G


GRUPOS = _grupos()


def legenda(img, t):
    grupo = None
    for g in GRUPOS:
        if g[0][0] - 0.05 <= t < g[-1][1] + 0.3:
            grupo = g
    if not grupo:
        return
    f = E.lilita(64)
    partes = [g[2] for g in grupo]
    larg = sum(f.getlength(p + " ") for p in partes)
    x = W / 2 - larg / 2
    d = ImageDraw.Draw(img)
    for g, p in zip(grupo, partes):
        cor = AMA if g[0] <= t else BR
        d.text((x, 1555), p, font=f, fill=cor, anchor="lm", stroke_width=7, stroke_fill=MAR)
        x += f.getlength(p + " ")


def overlay(img, t, com_legenda):
    bi = max(b for b, t0 in INI_BLOCO.items() if t0 <= t + 1e-6) if t < T_FALA else None
    if t < T_FALA:
        a, b = luzes()
        img.alpha_composite(a if int(t * 2.5) % 2 == 0 else b)
    if bi == 0:
        K.poe(img, gancho(), W / 2, 235, t, 0.0, -2, d=0.25)
    if bi is not None and BLOCOS[bi][0]:
        K.poe(img, etiqueta(BLOCOS[bi][0]), 340, 250, t, INI_BLOCO[bi] + 0.1, -4)
        tc = t_caixa(bi)
        caixa = BLOCOS[bi][1]
        if tc is not None and caixa and t >= tc:
            K.poe(img, caixa_presente(caixa, BLOCOS[bi][2]), 810, 1160, t, tc, 5)
    if t < T_FALA:
        K.marca(img)
        if com_legenda:
            legenda(img, t)


def cena_comenta(img, t):
    img.alpha_composite(D.fundo(t))
    K.poe(img, K.titulo("E VOCÊ?", 160, AMA), W / 2, 650, t, T_COMENTA + 0.05, -2)
    K.poe(img, E.pilula("Qual jogo você daria pra quem?", 56, BR, MAR), W / 2, 860, t, T_COMENTA + 0.4, 1)
    K.poe(img, E.pilula("COMENTA AQUI!", 64, VERDE, BR, fonte_titulo=True), W / 2, 990, t, T_COMENTA + 0.8, -1)


@lru_cache(None)
def mosaico():
    cs = [b[1] for b in BLOCOS if b[1]]
    im = Image.new("RGBA", (980, 560), (0, 0, 0, 0))
    n = len(cs)
    for k, p in enumerate(cs):
        cx = Image.open(p).convert("RGBA")
        cx = cx.crop(cx.getbbox())
        h = 250
        cx = cx.resize((int(cx.width * h / cx.height), h), Image.LANCZOS)
        if cx.width > 300:
            cx = cx.resize((300, int(cx.height * 300 / cx.width)), Image.LANCZOS)
        col, lin = k % 3, k // 3
        im.alpha_composite(cx, (int(160 + col * 330 - cx.width / 2), int(140 + lin * 280 - cx.height / 2)))
    return im


def cena_fim(img, t):
    img.alpha_composite(D.fundo(t))
    K.poe(img, TB.parceria(100) if False else K.logo(260), W / 2, 330, t, T_FIM + 0.05)
    K.poe(img, K.titulo("ALUGUE O PRESENTE\nANTES DE DAR!", 104, AMA), W / 2, 560, t, T_FIM + 0.2, -2)
    E.cola(img, mosaico(), W / 2, 1030, 0, 1, 1)
    K.poe(img, E.pilula("RETIRE EM MAUÁ OU RECEBA EM CASA · 5 DIAS DE JOGO", 34, BR, MAR, fonte_titulo=True), W / 2,
          1390, t, T_FIM + 0.6)
    K.poe(img, E.pilula("LINK NA BIO · @SUAVEZ_BG", 46, VERDE, BR, fonte_titulo=True), W / 2, 1480, t, T_FIM + 0.8)


def quadro(t, com_legenda=True):
    if t < T_FALA:
        img = quadro_video(t)
        overlay(img, t, com_legenda)
    else:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        if t < T_FIM:
            cena_comenta(img, t)
        else:
            cena_fim(img, t)
        for tb in (T_COMENTA, T_FIM):
            if 0 <= t - tb < 0.12:
                img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (t - tb) / 0.12)))))
    return img.convert("RGB")


def render_leg(fi):
    return quadro(fi / FPS, True).tobytes()


def render_sem(fi):
    return quadro(fi / FPS, False).tobytes()


# ---------------------------------------------------------------- áudio
def voz():
    """Os pedaços de fala, tratados (denoise leve + EQ suave), com 12 ms de fade em cada corte."""
    partes = []
    for bi, arq, a, z, t0 in PECAS:
        tmp = os.path.join(CACHE, f"v_{arq}_{a:.2f}.wav")
        if not os.path.exists(tmp):
            subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(a), "-t", str(z - a), "-i", ARQ[arq], "-ac", "1",
                            "-ar", str(SR), "-af",
                            "highpass=f=80,afftdn=nr=10:nf=-45,equalizer=f=300:t=q:w=1:g=-2,"
                            "acompressor=threshold=-22dB:ratio=2:attack=8:release=150", tmp], check=True)
        w = wave.open(tmp)
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        n = int((z - a) * SR)
        x = np.pad(x, (0, max(0, n - len(x))))[:n]
        f = int(0.012 * SR)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        partes.append(x)
    v = np.concatenate(partes)
    return v / (np.abs(v).max() + 1e-9) * 0.9


def audio():
    n = int(DUR * SR)
    v = voz()
    v = np.pad(v, (0, n - len(v)))[:n]
    mus = S.musica_cafe(DUR + 0.5)[:n]
    mus = mus / (np.abs(mus).max() + 1e-9)
    env = np.ones(n) * 0.10
    env[:int(T_FALA * SR)] = 0.06
    ev = np.zeros(n)
    for bi in range(len(BLOCOS)):
        tc = t_caixa(bi)
        if tc is not None and BLOCOS[bi][1]:
            S.add(ev, S.plim(), tc, 0.25)
    S.add(ev, S.sino(), T_COMENTA, 0.35)
    S.add(ev, S.carta_vira(), T_FIM, 0.35)
    mix = v + mus * env + ev
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.85
    p = os.path.join(OUT, "presente_mix.wav")
    st = np.repeat((mix * 32767).astype(np.int16)[:, None], 2, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())
    return p


def main():
    args = sys.argv[1:]
    prepara()
    if "--frame" in args:
        ts = [float(a) for a in args[args.index("--frame") + 1:] if not a.startswith("--")]
        K.folha([quadro(t) for t in ts], os.path.join(OUT, "frames_presente.jpg"))
        print("DUR", round(DUR, 1), "fala", round(T_FALA, 1), {b: round(INI_BLOCO[b], 1) for b in INI_BLOCO})
        return
    wav = audio()
    nq = int(round(DUR * FPS))
    for nome, fn in (("legendado", render_leg), ("sem_legenda", render_sem)):
        base = os.path.join(OUT, f"presente_{nome}.mp4")
        encode(base, fn, list(range(nq)), wav)
        final_loudness(base, base.replace(".mp4", "_final.mp4"))
    print("ok", DUR)


if __name__ == "__main__":
    main()
