#!/usr/bin/env python3
"""Reels "TOP 10 ÀS CEGAS" da Jéssica (1/nov/2026): o Erik (fora da câmera) fala um jogo e ela escolhe NA HORA a
posição dele no top 10, sem saber os próximos. Dois vídeos no Drive de brutos (brutos/nov01b/, fora do git): 151657
(Trio, Tikal, Mascarade, The Resistance, Nem a Pato, A Ilha do Tesouro) e 151838 (Coffee Rush, Telestrations na
Madruga, King of Tokyo Duel, Cartógrafos + "gostou do seu top 10? / gostei / parabéns").
Pedido dele: a imagem do jogo de um lado e a POSIÇÃO. Visual: ela no meio; à esquerda a escadinha 1–10 que vai se
preenchendo; quando o Erik fala o jogo, a caixa OFICIAL entra grande à direita com o nome; quando ela diz o número
(tempo da voz dela), a caixa voa para a casa e o número acende. Fim: o top 10 completo, "comenta" e tela final.
Nomes conferidos com eles: 7 = Tikal ("Chicão" no Whisper), 9 = Nem a Pato! (Grok; NÃO está no site, caixa da loja da Grok).

    python3 top10.py --frame 1 6 10 26 44
    python3 top10.py
"""
import argparse
import json
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
sys.path.insert(0, os.path.join(REPO, "listas-reels"))
from motor import W, H, FPS, WHITE, ease, seg, out_back, logo_card, cola, folha, ffmpeg, sombra  # noqa: E402
import som  # noqa: E402
from base import texto  # noqa: E402

BR = os.path.join(ROOT, "brutos", "nov01b")
AS = os.path.join(ROOT, "assets", "top10")
OUT = os.path.join(ROOT, "out")
INK, AMARELO, LARANJA, PETROLEO, ROSA = (40, 26, 18), (255, 199, 31), (244, 136, 37), (28, 124, 150), (219, 39, 119)
GRADE = "hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.3:5:5:0.0,eq=contrast=1.02:saturation=1.02"
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
CLIPES = [("151657", 26.43), ("151838", 16.69)]
# (clipe, quando ELE fala o jogo, quando ELA diz a posição (início da voz), caixa, nome na tela, posição)
JOGOS = [
    (0, 3.70, 5.30, "trio", "TRIO", 1),
    (0, 7.20, 9.45, "tikal", "TIKAL", 7),
    (0, 10.80, 12.80, "mascarade_second_edition", "MASCARADE", 5),
    (0, 13.70, 16.65, "the_resistance", "THE RESISTANCE", 8),
    (0, 18.80, 21.20, "nem_a_pato", "NEM A PATO!", 9),
    (0, 22.75, 25.20, "treasure_island", "A ILHA DO TESOURO", 4),
    (1, 0.75, 2.75, "coffee_rush", "COFFEE RUSH", 2),
    (1, 4.30, 6.90, "telestrations_madruga", "TELESTRATIONS NA MADRUGA", 10),
    (1, 7.80, 10.65, "king_of_tokyo_duel", "KING OF TOKYO DUEL", 3),
    (1, 11.60, 13.05, "cartographers", "CARTÓGRAFOS", 6),
]
# legenda escrita à mão (o Whisper errou muito: "Chicão", "Meia paz", "De Existence"): (clipe, de, até, texto)
LEG = [
    (0, 0.05, 2.60, "AMORZINHO, TOP 10!"), (0, 3.70, 4.40, "TRIO?"), (0, 5.30, 6.00, "UM."),
    (0, 7.20, 8.00, "TIKAL."), (0, 9.10, 10.30, "NOSSA... SETE."), (0, 10.80, 11.60, "MASCARADE."),
    (0, 12.80, 13.40, "CINCO."), (0, 13.70, 14.70, "THE RESISTANCE."), (0, 16.60, 18.10, "OITO, QUE JÁ DEU MUITA M*RDA."),
    (0, 18.80, 19.70, "NEM A PATO!"), (0, 20.40, 21.90, "AH, VOU COLOCAR NO 9."), (0, 22.70, 23.70, "A ILHA DO TESOURO?"),
    (0, 25.20, 25.90, "QUATRO."),
    (1, 0.75, 1.60, "COFFEE RUSH."), (1, 2.75, 3.40, "DOIS."), (1, 4.30, 6.00, "TELESTRATIONS NA MADRUGA."),
    (1, 6.90, 7.50, "DEZ."), (1, 7.80, 9.60, "KING OF TOKYO DUEL."), (1, 10.20, 11.00, "NOSSA, TRÊS."),
    (1, 11.60, 12.60, "E CARTÓGRAFOS?"), (1, 13.05, 13.70, "SEIS."), (1, 13.90, 14.90, "BOA, GOSTOU DO SEU TOP 10?"),
    (1, 15.00, 15.70, "GOSTEI."), (1, 15.85, 16.60, "PARABÉNS!"),
]
INICIO = [0.0, CLIPES[0][1]]  # tempo no vídeo em que cada clipe começa
FIM_GRAV = INICIO[1] + CLIPES[1][1]
RECAP, COMENTA, FINAL = 4.0, 3.2, 3.6
DUR = FIM_GRAV + RECAP + COMENTA + FINAL
VOO = 0.5  # a caixa voa até a casa em 0,5 s

# escadinha à esquerda
LX, LW, LY0, LH = 22, 262, 300, 113


def casa_xy(pos):
    return LX + LW / 2, LY0 + (pos - 1) * LH + LH / 2


def tv(clipe, t):
    return INICIO[clipe] + t


EVENTOS = [dict(nome=tv(c, a), pos_t=tv(c, b), caixa=cx, rot=rot, pos=p) for c, a, b, cx, rot, p in JOGOS]


# ---------------------------------------------------------------- imagens
@lru_cache(None)
def caixa(n, h, larg):
    im = Image.open(os.path.join(AS, n + ".png")).convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(h / im.height, larg / im.width)
    return im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)


@lru_cache(None)
def caixa_sombra(n, h, larg):
    im = caixa(n, h, larg)
    sh = sombra(im, 12, (0, 12), 0.5)
    sh.alpha_composite(im, (24, 24))
    return sh


@lru_cache(None)
def pilula(txt, s, cor, fg=WHITE):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 44, tx.height + 12), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=cor,
                                          outline=INK, width=6)
    im.alpha_composite(tx, (22, 6))
    return im


@lru_cache(None)
def numero(pos, aceso):
    s = 74
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((2, 2, s - 3, s - 3), fill=AMARELO if aceso else (250, 246, 238), outline=INK, width=5)
    tx = texto(str(pos), "lilita", 40 if pos < 10 else 34, INK)
    im.alpha_composite(tx, (int(s / 2 - tx.width / 2), int(s / 2 - tx.height / 2)))
    return im


@lru_cache(None)
def casa_vazia():
    im = Image.new("RGBA", (LW, LH - 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, LW - 1, LH - 11), radius=22, fill=(20, 16, 30, 120),
                                          outline=(255, 255, 255, 170), width=3)
    return im


@lru_cache(None)
def legenda_img(txt):
    return texto(txt, "lilita", 58, WHITE, INK, 8, 5, INK)


@lru_cache(None)
def cabecalho():
    return texto("TOP 10 ÀS CEGAS", "lilita", 74, AMARELO, INK, 8, 6, INK)


def escada(img, t, alpha=1.0):
    entra = ease(seg(t, 2.6, 3.3))
    if entra <= 0:
        return
    dx = -320 * (1 - entra)
    for pos in range(1, 11):
        x, y = casa_xy(pos)
        img.alpha_composite(casa_vazia(), (int(LX + dx), int(y - (LH - 10) / 2)))
        ev = next(e for e in EVENTOS if e["pos"] == pos)
        chegou = t >= ev["pos_t"] + VOO
        aceso = ev["pos_t"] <= t < ev["pos_t"] + VOO + 0.9
        cola(img, numero(pos, aceso), x - LW / 2 + 46 + dx, y, sc=1.0 + (0.18 if aceso else 0.0))
        if chegou:
            mini = caixa(ev["caixa"], LH - 22, LW - 110)
            pulo = out_back(seg(t, ev["pos_t"] + VOO, ev["pos_t"] + VOO + 0.25))
            cola(img, mini, x + 40 + dx, y, sc=0.8 + 0.2 * pulo)


def destaque(img, t):
    """A caixa do jogo que ele acabou de falar: grande à direita; no número dela, voa até a casa."""
    for ev in EVENTOS:
        a, b = ev["nome"], ev["pos_t"]
        if not (a <= t < b + VOO):
            continue
        big = caixa_sombra(ev["caixa"], 400, 330)
        x0, y0 = 880, 1120
        if t < b:
            sc = out_back(seg(t, a, a + 0.35))
            cola(img, big, x0, y0, rot=4, sc=sc)
            cola(img, pilula(ev["rot"], 40 if len(ev["rot"]) < 16 else 30, PETROLEO), x0 - 40, y0 + 270, rot=-3,
                 sc=out_back(seg(t, a + 0.1, a + 0.45)))
            cola(img, pilula("QUE POSIÇÃO?", 34, ROSA), x0 - 20, y0 - 270, rot=3, sc=out_back(seg(t, a + 0.5, a + 0.8)))
        else:
            u = ease(seg(t, b, b + VOO))
            cx, cy = casa_xy(ev["pos"])
            cx += 40
            x = x0 + (cx - x0) * u
            y = y0 + (cy - y0) * u + 220 * math.sin(math.pi * u)  # arco por BAIXO (por cima passava no rosto dela)
            alvo = (LH - 22) / big.height
            cola(img, big, x, y, rot=4 * (1 - u), sc=1 + (alvo - 1) * u)


def legenda(img, t):
    for c, a, b, txt in LEG:
        if tv(c, a) <= t < tv(c, b):
            sc = 0.85 + 0.15 * ease(seg(t, tv(c, a), tv(c, a) + 0.12))
            cola(img, legenda_img(txt), W / 2 + 120, 1545, sc=sc)
            return


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= FIM_GRAV:
        return img
    img.alpha_composite(logo_card(140), (W - 176, 40))
    cola(img, cabecalho(), 430, 120, rot=-2, sc=out_back(seg(t, 0.1, 0.5)))
    if t < 3.4:
        cola(img, pilula("ELA NÃO SABE OS PRÓXIMOS!", 38, ROSA), 450, 225, rot=2, sc=out_back(seg(t, 0.5, 0.9)))
    escada(img, t)
    destaque(img, t)
    legenda(img, t)
    return img


# ---------------------------------------------------------------- fim: o top 10 completo, comenta e tela final
@lru_cache(None)
def fundo_fim(base_bytes):
    base = Image.frombytes("RGB", (W, H), base_bytes).filter(ImageFilter.GaussianBlur(22))
    return Image.blend(base, Image.new("RGB", (W, H), (30, 20, 50)), 0.6).convert("RGBA")


def tela_fim(base, t):
    img = fundo_fim(base.tobytes()).copy()
    lt = t - FIM_GRAV
    if lt < RECAP:
        cola(img, texto("O TOP 10 DA JÉSSICA", "lilita", 84, AMARELO, INK, 8, 6, INK), W / 2, 230, rot=-2,
             sc=out_back(seg(lt, 0.0, 0.4)))
        for pos in range(1, 11):
            ev = next(e for e in EVENTOS if e["pos"] == pos)
            col, lin = (0 if pos <= 5 else 1), (pos - 1) % 5
            x, y = 285 + col * 510, 470 + lin * 255
            u = out_back(seg(lt, 0.25 + 0.12 * (pos - 1), 0.55 + 0.12 * (pos - 1)))
            cola(img, numero(pos, pos == 1), x - 150, y, sc=1.25 * u)
            cola(img, caixa_sombra(ev["caixa"], 215, 230), x + 40, y, rot=(-3 if pos % 2 else 3), sc=u)
        return img
    lt -= RECAP
    if lt < COMENTA:
        cola(img, texto("E O SEU Nº 1,\nQUAL SERIA?", "lilita", 104, WHITE, INK, 9, 8, INK, entre=1.05), W / 2, 820,
             rot=-2, sc=out_back(seg(lt, 0.0, 0.4)))
        cola(img, pilula("Comenta aqui!", 70, ROSA), W / 2, 1130, rot=3, sc=out_back(seg(lt, 0.4, 0.75)))
        return img
    lt -= COMENTA
    cola(img, logo_card(420), W / 2, 420, sc=out_back(seg(lt, 0.0, 0.4)))
    v = ease(seg(lt, 0.4, 0.8))
    for j, (txt, f, s, cor) in enumerate([("QUASE TODOS ESSES\nESTÃO NO NOSSO ACERVO", "lilita", 74, AMARELO),
                                          ("aluguel de 5 dias · retire em Mauá\nou receba em casa", "figtree", 46, WHITE),
                                          ("LINK NA BIO · @SUAVEZ_BG", "lilita", 62, WHITE)]):
        cola(img, texto(txt, f, s, cor, INK, 6 if f == "lilita" else 0, 5 if f == "lilita" else 3, INK, entre=1.15),
             W / 2, 860 + j * 230, alpha=v)
    return img


# ---------------------------------------------------------------- render
def ler(clipe):
    k, d = CLIPES[clipe]
    n = round(d * FPS)
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-i", os.path.join(BR, f"20261101_{k}.mp4"), "-frames:v", str(n),
                          "-vf", f"fps={FPS},scale={W}:{H},{GRADE}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    ultimo = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        ultimo = Image.frombytes("RGB", (W, H), buf)
        yield ultimo
    p.wait()


def quadros():
    ultimo = None
    for c in range(2):
        alvo = round(INICIO[c] * FPS) if c else 0
        k = 0
        for fr in ler(c):
            ultimo = fr
            yield fr
            k += 1
        # completa até o próximo início exato (arredondamento)
        prox = round(INICIO[1] * FPS) if c == 0 else round(FIM_GRAV * FPS)
        while alvo + k < prox:
            yield ultimo
            k += 1
    n = round(DUR * FPS) - round(FIM_GRAV * FPS) + 2
    for _ in range(n):
        yield ultimo


def frame_final(n, fr):
    t = n / FPS
    if t >= FIM_GRAV:
        return tela_fim(fr, t).convert("RGB")
    im = fr.convert("RGBA")
    im.alpha_composite(overlay(t))
    return im.convert("RGB")


def audio(path):
    sr = 44100
    voz = np.zeros(int(DUR * sr) + sr)
    for c, (k, d) in enumerate(CLIPES):
        r = subprocess.run([ffmpeg(), "-loglevel", "error", "-i", os.path.join(BR, f"20261101_{k}.mp4"), "-vn", "-ac", "1",
                            "-ar", "44100", "-af", VOZ, "-f", "s16le", "-"], capture_output=True)
        x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
        x = x[:int(d * sr)]
        f = int(0.02 * sr)
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
        i = int(INICIO[c] * sr)
        voz[i:i + len(x)] += x
    voz *= 10 ** (-20 / 20) / (np.sqrt((voz[np.abs(voz) > 0.02] ** 2).mean()) + 1e-9)
    vp = os.path.join(OUT, "top10_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(voz, -1, 1) * 32767).astype(np.int16).tobytes())
    cues = [(0.1, "whoosh", 0.3), (2.6, "whoosh", 0.35)]
    for ev in EVENTOS:
        cues += [(ev["nome"], "pop", 0.35), (ev["pos_t"], "whoosh", 0.3), (ev["pos_t"] + VOO, "ding", 0.45)]
    cues += [(FIM_GRAV, "reveal", 0.4)] + [(FIM_GRAV + 0.25 + 0.12 * k, "pop", 0.3) for k in range(10)]
    cues += [(FIM_GRAV + RECAP, "whoosh", 0.4), (FIM_GRAV + RECAP + COMENTA, "chime", 0.5)]
    som.build(path, DUR, cues, musica="gameshow", voz=[(vp, 0.0)], fx_ganho=0.35, duck=0.55, musica_ganho=0.2,
              satura=False)
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", path, "-af", "loudnorm=I=-15.5:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    tmp = path.replace(".wav", "_n.wav")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", path, "-af",
                    f"loudnorm=I=-15.5:TP=-2:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}",
                    "-ar", "44100", tmp], check=True)
    os.replace(tmp, path)


def render(saida, wav):
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-b:v", "5200k", "-maxrate",
                          "6500k", "-bufsize", "9000k", "-preset", "medium", "-tune", "film", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", saida],
                         stdin=subprocess.PIPE)
    for n, fr in enumerate(quadros()):
        if n / FPS >= DUR:
            break
        p.stdin.write(frame_final(n, fr).tobytes())
    p.stdin.close()
    p.wait()
    print("ok", saida, os.path.getsize(saida) // 1024 ** 2, "MB", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s")
    if a.frame:
        alvo = sorted(round(x * FPS) for x in a.frame)
        ims = []
        for n, fr in enumerate(quadros()):
            if n in alvo:
                ims.append(frame_final(n, fr))
            if n > alvo[-1]:
                break
        folha(ims, os.path.join(OUT, "frames_top10.jpg"))
        return
    wav = os.path.join(OUT, "top10.wav")
    audio(wav)
    render(os.path.join(OUT, "top10.mp4"), wav)


if __name__ == "__main__":
    main()
