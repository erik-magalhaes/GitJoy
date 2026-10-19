#!/usr/bin/env python3
"""Reels "VEM SEPARAR 2 PEDIDOS COMIGO" (Jéssica, 19/out/2026). Brutos fora do git em brutos/out19/: 102837 = ela na
estante ("Bom dia! Vem separar dois pedidos comigo!") e 103147 = a câmera dela pegando os jogos na estante e pondo nas
duas cadeiras (sem fala). Pedido 1 (cadeira da esquerda): Canvas, La Granja, Convidados Indesejados. Pedido 2 (direita):
Throw Throw Burrito, Echoes of Time, Azul Duel. Cada pedido tem 3 jogos = 7 dias (prazo progressivo).
Edição: rampas de velocidade (procura na estante bem rápida, pegar/mostrar só um pouco mais rápido, pôr na cadeira
médio), cartão com nome + jogadores/tempo do site ao mostrar, lista do pedido no canto que ganha ✓ quando o jogo vai
para a cadeira, selo "3 JOGOS = 7 DIAS!", "Qual pedido você levaria?" e tela final com as 6 fotos do site.
Identidade da Jéssica (Lilita One + Figtree, contorno marrom, sombra sólida, selos em pílula).

    python3 pedidos.py --info
    python3 pedidos.py --frame 1 5 12 30    # out/frames_pedidos.jpg
    python3 pedidos.py                      # out/pedidos.mp4
"""
import argparse
import json
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
from motor import W, H, FPS, ease, seg, out_back, logo_card, cola, folha, ffmpeg  # noqa: E402
import som  # noqa: E402
from base import texto, foto  # noqa: E402

BR = os.path.join(ROOT, "brutos", "out19")
OUT = os.path.join(ROOT, "out")
MARROM, PETROLEO, LARANJA, AMARELO, BRANCO = (63, 36, 18), (28, 124, 150), (244, 136, 37), (255, 199, 31), (250, 250, 250)
VERDE, ROSA = (46, 160, 90), (219, 39, 119)
GRADE = "hqdn3d=1.5:1.5:3:3,unsharp=5:5:0.35:5:5:0.0,eq=contrast=1.02:saturation=1.03"
VOZ = "highpass=f=80,afftdn=nr=8:nf=-48,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=1.5"
INTRO = ("102837", 0.85, 3.80)  # "Bom dia! Vem separar dois pedidos comigo!"
CAM = "103147"
# jogos: (pedido, nome no site, foto do site, procura a→b, pegar+mostrar b→c, pôr na cadeira c→d)  — tempos no bruto
JOGOS = [
    (1, "Canvas", "canvas", 0.0, 2.5, 6.0, 7.5),
    (1, "La Granja", "la_granja", 7.5, 10.0, 15.0, 16.0),
    (1, "Convidados Indesejados", "convidados_indesejados", 16.0, 17.0, 21.0, 22.5),
    (2, "Throw Throw Burrito", "throw_throw_burrito", 22.5, 26.0, 29.5, 31.0),
    (2, "Echoes of Time", "echoes_of_time", 31.0, 33.0, 37.5, 39.5),
    (2, "Azul Duel", "azul_duel", 39.5, 43.0, 47.5, 49.5),
]
FIM_CAM = 53.2  # as duas cadeiras prontas + o joinha (velocidade normal)
MOSTRA = 0.6  # o nome entra quando a caixa já saiu da estante
VEL = {"procura": 3.0, "mostra": 1.25, "poe": 1.5, "fim": 1.0}
COMENTA, FINAL = 3.2, 3.8


@lru_cache(None)
def site():
    return json.load(open(os.path.join(REPO, "comum", "dados", "acervo_site.json"), encoding="utf-8"))


EXTRA = {"Convidados Indesejados": {"jogadores": "1–8", "tempo": "75min"}}  # entrou no site depois de 12/out (17/out)


def ficha(nome):
    g = site().get(nome) or EXTRA[nome]
    a, b = g["jogadores"].replace("–", "-").split("-")
    jog = f"{a} jogadores" if a == b else f"{a} a {b} jogadores"
    return f"{jog} · {g['tempo'].replace('min', ' min')}"


def nq(t0, d):
    return round((t0 + d) * FPS) - round(t0 * FPS)


def linha():
    """Planos (fonte, início no bruto, velocidade, quadros) e marcas no tempo do vídeo."""
    tl, t, mk = [], 0.0, {"jogos": []}
    n = nq(t, INTRO[2] - INTRO[1])
    tl.append(dict(src=INTRO[0], a=INTRO[1], vel=1.0, n=n, t0=t))
    t += n / FPS
    mk["cam"] = t
    for ped, nome, arq, a, b, c, d in JOGOS:
        j = {"ped": ped, "nome": nome, "arq": arq}
        for tipo, x, y in (("procura", a, b), ("mostra", b, c), ("poe", c, d)):
            n = nq(t, (y - x) / VEL[tipo])
            tl.append(dict(src=CAM, a=x, vel=VEL[tipo], n=n, t0=t, tipo=tipo))
            j[tipo] = t
            t += n / FPS
        j["pronto"] = t  # o jogo assentou na cadeira
        mk["jogos"].append(j)
    mk["fim_cam"] = t
    n = nq(t, (FIM_CAM - JOGOS[-1][6]) / VEL["fim"])
    tl.append(dict(src=CAM, a=JOGOS[-1][6], vel=VEL["fim"], n=n, t0=t, tipo="fim"))
    t += n / FPS
    mk["comenta"] = t
    mk["final"] = t + COMENTA
    return tl, mk, t + COMENTA + FINAL


TL, M, DUR = linha()
TROCA = M["jogos"][2]["pronto"] + 1.1  # "PEDIDO 2!" entra depois do selo "3 JOGOS = 7 DIAS!" do pedido 1


# ---------------------------------------------------------------- peças gráficas
def titulo(txt, s, cor=BRANCO, entre=1.05):
    return texto(txt, "lilita", s, cor, MARROM, max(6, s // 11), max(5, s // 13), MARROM, entre=entre)


@lru_cache(None)
def pilula(txt, s, cor, fg=BRANCO):
    tx = texto(txt, "lilita", s, fg)
    im = Image.new("RGBA", (tx.width + 44, tx.height + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((7, 7, im.width - 1, im.height - 1), radius=im.height // 2, fill=MARROM)  # sombra sólida
    d.rounded_rectangle((0, 0, im.width - 8, im.height - 8), radius=im.height // 2, fill=cor, outline=MARROM, width=6)
    im.alpha_composite(tx, (18, 0))
    return im


@lru_cache(None)
def cartao_jogo(nome):
    """Cartão branco com contorno marrom: nome do jogo + ficha do site."""
    t1 = texto(nome.upper(), "lilita", 74, MARROM)
    t2 = texto(ficha(nome), "figtree", 44, PETROLEO)
    w = max(t1.width, t2.width) + 70
    h = t1.height + t2.height + 10
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, w + 11, h + 11), radius=34, fill=MARROM)
    d.rounded_rectangle((0, 0, w, h), radius=34, fill=BRANCO, outline=MARROM, width=7)
    im.alpha_composite(t1, ((w - t1.width) // 2, 4))
    im.alpha_composite(t2, ((w - t2.width) // 2, t1.height - 14))
    return im


def check(d, x, y, s, cor):
    d.line([(x, y + s * 0.5), (x + s * 0.38, y + s * 0.88), (x + s, y + s * 0.05)], fill=cor, width=max(4, int(s / 5)),
           joint="curve")


def lista(img, t):
    """Lista do pedido no canto superior esquerdo: os 3 nomes; ✓ quando o jogo assenta na cadeira."""
    if t < M["cam"] or t >= M["fim_cam"] + 0.6:
        return
    ped = 1 if t < TROCA else 2
    js = [j for j in M["jogos"] if j["ped"] == ped]
    w, h, top = 540, 300, 40  # o selo do pedido fica metade acima do cartão (com espaço no topo da imagem)
    im = Image.new("RGBA", (w + 12, h + top + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, top + 12, w + 11, top + h + 11), radius=30, fill=MARROM)
    d.rounded_rectangle((0, top, w, top + h), radius=30, fill=BRANCO, outline=MARROM, width=6)
    cola(im, pilula(f"PEDIDO {ped}", 48, LARANJA if ped == 1 else PETROLEO), w / 2, top + 4)
    for k, j in enumerate(js):
        y = top + 66 + k * 74
        feito = t >= j["pronto"]
        visto = t >= j["mostra"] + MOSTRA
        d.rounded_rectangle((22, y, 70, y + 48), radius=10, fill=VERDE if feito else BRANCO, outline=MARROM, width=5)
        if feito:
            u = ease(seg(t, j["pronto"], j["pronto"] + 0.25))
            if u > 0.05:
                check(d, 30, y + 6, 34 * u + 0.1, BRANCO)
        nome = j["nome"] if visto else "?"
        cor = MARROM if visto else (170, 150, 135)
        tx = texto(nome, "figtree", 42 if len(nome) < 18 else 35, cor)
        im.alpha_composite(tx, (84, int(y + 24 - tx.height / 2)))
    ent = out_back(seg(t, M["cam"], M["cam"] + 0.35))
    if ped == 2:
        ent = out_back(seg(t, TROCA, TROCA + 0.35))
    sai = ease(seg(t, M["fim_cam"] + 0.2, M["fim_cam"] + 0.6))
    cola(img, im, 34 + im.width / 2, 70 + im.height / 2 - 500 * sai, rot=-2 if ped == 1 else 2, sc=ent)


def overlay(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= M["final"]:
        tela_final(img, t - M["final"])
        return img
    img.alpha_composite(logo_card(150), (W - 186, 46))
    if t < M["cam"]:  # gancho: o rosto dela fica livre no alto
        cola(img, titulo("BOM DIA!", 92, AMARELO), W / 2, 1180, rot=-3, sc=out_back(seg(t, 0.1, 0.45)))
        cola(img, titulo("VEM SEPARAR\n2 PEDIDOS COMIGO!", 96), W / 2, 1380, rot=2, sc=out_back(seg(t, 0.9, 1.3)))
        return img
    lista(img, t)
    for k, j in enumerate(M["jogos"]):
        if j["mostra"] + MOSTRA <= t < j["pronto"] + 0.2:  # nome do jogo enquanto ela mostra a caixa
            u = out_back(seg(t, j["mostra"] + MOSTRA, j["mostra"] + MOSTRA + 0.3)) * (1 - ease(seg(t, j["pronto"] - 0.1, j["pronto"] + 0.2)))
            cola(img, cartao_jogo(j["nome"]), W / 2, 1480, rot=-2 if k % 2 else 2, sc=u)
        if k in (2, 5) and j["pronto"] <= t < j["pronto"] + 1.1:  # pedido fechado: 3 jogos = 7 dias
            lt = t - j["pronto"]
            u = out_back(seg(lt, 0.05, 0.35)) * (1 - ease(seg(lt, 0.85, 1.1)))
            cola(img, pilula("3 JOGOS = 7 DIAS!", 76, VERDE), W / 2, 1000, rot=-4, sc=u)
        if k == 3 and TROCA <= t < TROCA + 1.0:  # carimbo de troca de pedido
            lt = t - TROCA
            u = out_back(seg(lt, 0.0, 0.3)) * (1 - ease(seg(lt, 0.75, 1.0)))
            cola(img, titulo("PEDIDO 2!", 130, AMARELO), W / 2, 900, rot=-5, sc=u)
    if M["fim_cam"] <= t < M["comenta"]:
        lt = t - M["fim_cam"]
        cola(img, titulo("PEDIDOS\nPRONTOS!", 120, AMARELO), W / 2, 1380, rot=-3, sc=out_back(seg(lt, 1.1, 1.5)))
        cola(img, pilula("1", 80, LARANJA), 300, 640, sc=out_back(seg(lt, 1.5, 1.8)))
        cola(img, pilula("2", 80, PETROLEO), 760, 640, sc=out_back(seg(lt, 1.7, 2.0)))
    if t >= M["comenta"]:
        lt = t - M["comenta"]
        cola(img, titulo("QUAL PEDIDO\nVOCÊ LEVARIA?", 104), W / 2, 820, rot=-2, sc=out_back(seg(lt, 0.0, 0.4)))
        cola(img, pilula("Comenta 1 ou 2!", 72, ROSA), W / 2, 1100, rot=3, sc=out_back(seg(lt, 0.35, 0.7)))
    return img


def tela_final(img, lt):
    cola(img, logo_card(380), W / 2, 250, sc=out_back(seg(lt, 0.0, 0.4)))
    for k, j in enumerate(M["jogos"]):
        x, y = 210 + (k % 3) * 330, 640 + (k // 3) * 340
        cola(img, foto(j["arq"], 300, borda=8, raio=22, sombra_a=0.45), x, y, rot=(-3, 2, -2, 3, -2, 2)[k],
             sc=out_back(seg(lt, 0.12 + 0.06 * k, 0.45 + 0.06 * k)))
    v = ease(seg(lt, 0.6, 1.0))
    linhas = [("3 JOGOS = 7 DIAS DE JOGO", "lilita", 70, AMARELO), ("RESERVE ONLINE · RETIRE EM MAUÁ\nOU RECEBA EM CASA", "figtree", 44, BRANCO),
              ("LINK NA BIO · @SUAVEZ_BG", "lilita", 60, BRANCO)]
    for j, (txt, f, s, cor) in enumerate(linhas):
        cola(img, texto(txt, f, s, cor, MARROM, 6 if f == "lilita" else 3, 5 if f == "lilita" else 3, MARROM, entre=1.2),
             W / 2, 1360 + j * 150, alpha=v)


# ---------------------------------------------------------------- vídeo
def ler(src, a, n, vel):
    p = subprocess.Popen([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-i", os.path.join(BR, src + ".mp4"),
                          "-frames:v", str(n), "-vf", f"setpts=PTS/{vel},fps={FPS},scale={W}:{H},{GRADE}", "-an", "-f",
                          "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    k, ultimo = 0, None
    while k < n:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        ultimo = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        yield ultimo
        k += 1
    while k < n:
        yield ultimo
        k += 1
    p.wait()


def quadros():
    ultimo = None
    for p in TL:
        for fr in ler(p["src"], p["a"], p["n"], p["vel"]):
            ultimo = fr
            yield fr
    base = Image.fromarray(ultimo).filter(ImageFilter.GaussianBlur(20))
    for k in range(round(COMENTA * FPS)):
        yield np.asarray(Image.blend(base, Image.new("RGB", (W, H), (28, 124, 150)), 0.45))
    fundo = np.asarray(Image.blend(base, Image.new("RGB", (W, H), (28, 124, 150)), 0.78))
    for _ in range(round(FINAL * FPS) + 2):
        yield fundo


# ---------------------------------------------------------------- áudio
def cues():
    c = [(0.1, "pop", 0.5), (0.9, "pop", 0.5), (M["cam"], "whoosh", 0.45)]
    for k, j in enumerate(M["jogos"]):
        c += [(j["procura"], "whoosh", 0.35), (j["mostra"] + MOSTRA, "pop", 0.5), (j["pronto"], "ding", 0.55)]
        if k in (2, 5):
            c.append((j["pronto"] + 0.15, "chime", 0.5))
    c += [(TROCA, "carimbo", 0.45), (M["fim_cam"] + 1.1, "reveal", 0.6), (M["fim_cam"] + 1.5, "pop", 0.5),
          (M["fim_cam"] + 1.7, "pop", 0.5), (M["comenta"], "whoosh", 0.4), (M["comenta"] + 0.35, "pop", 0.5),
          (M["final"], "whoosh", 0.4), (M["final"] + 0.5, "chime", 0.5)]
    return c


def audio(path):
    sr = 44100
    src, a, b = INTRO
    r = subprocess.run([ffmpeg(), "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", os.path.join(BR, src + ".mp4"),
                        "-vn", "-ac", "1", "-ar", "44100", "-af", VOZ, "-f", "s16le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, np.int16).astype(np.float64) / 32768
    q = int(0.03 * sr)
    e = np.sqrt(np.convolve(x ** 2, np.ones(q) / q, "same"))
    x = x * 10 ** (-20 / 20) / (np.sqrt((x[e > e.max() * 0.12] ** 2).mean()) + 1e-9)
    f = int(0.02 * sr)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    vp = os.path.join(OUT, "pedidos_voz.wav")
    with wave.open(vp, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    som.build(path, DUR, cues(), musica="travessa", voz=[(vp, 0.0)], fx_ganho=0.4, duck=0.6, musica_ganho=0.3,
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
                          "-framerate", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "19", "-preset", "medium",
                          "-tune", "film", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags",
                          "+faststart", saida], stdin=subprocess.PIPE)
    for n, fr in enumerate(quadros()):
        t = n / FPS
        if t >= DUR:
            break
        im = Image.fromarray(fr).convert("RGBA")
        im.alpha_composite(overlay(t))
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print("ok", saida, os.path.getsize(saida) // 1024 ** 2, "MB", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=float, nargs="*")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    print(f"duração {DUR:.1f} s", {k: round(v, 1) for k, v in M.items() if k != "jogos"})
    if a.info:
        for j in M["jogos"]:
            print(j["nome"], {k: round(v, 2) for k, v in j.items() if isinstance(v, float)})
        return
    if a.frame:
        alvo = {round(x * FPS): x for x in a.frame}
        ims = {}
        for n, fr in enumerate(quadros()):
            if n in alvo:
                im = Image.fromarray(fr).convert("RGBA")
                im.alpha_composite(overlay(n / FPS))
                ims[n] = im.convert("RGB")
            if len(ims) == len(alvo):
                break
        folha([ims[k] for k in sorted(ims)], os.path.join(OUT, "frames_pedidos.jpg"))
        return
    wav = os.path.join(OUT, "pedidos.wav")
    audio(wav)
    render(os.path.join(OUT, "pedidos.mp4"), wav)


if __name__ == "__main__":
    main()
