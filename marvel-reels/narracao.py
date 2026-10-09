#!/usr/bin/env python3
"""Monta a linha do tempo do Reels do Marvel United a partir das falas gravadas.

Lê narracao/frase_NN.wav (já tratadas) e narracao/palavras.json (tempos das
palavras), decide quanto dura cada cena para caber a fala e grava
narracao/timeline.json, que o portais.py usa para esticar/encurtar as cenas,
posicionar a voz, os efeitos e as legendas.
"""
import json
import os
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(ROOT, "narracao")

# cenas originais (início, fim) na mesma ordem do portais.SCENES
ORIG = [(0.0, 6.0), (6.0, 13.0), (13.0, 20.0), (20.0, 27.0), (27.0, 33.5), (33.5, 41.0), (41.0, 48.5), (48.5, 56.5), (56.5, 65.5)]
FALAS_POR_CENA = [[1], [2], [3], [4], [5], [6], [7], [8], [9]]
LEAD, GAP, TAIL = 0.3, 0.45, 0.6
MIN_FRAC = 0.7  # cena nunca encolhe abaixo de 70% do original (animações respiram)
CTA_HOLD = 3.6  # tempo do logo na tela depois da última fala (garante mais de 1 minuto)

TEXTO = {  # o que ele FALOU na gravação (out/2026), com a grafia certa
    1: "Você já imaginou reunir os maiores heróis da Marvel na mesa da sua casa?",
    2: "Esse é o Marvel United: o jogo cooperativo em que vocês são os heróis contra o vilão que o próprio jogo controla.",
    3: "Na sua vez, você joga uma carta e soma com os símbolos da carta anterior. É tipo um combo: um herói ajudando o outro.",
    4: "A cada três cartas dos heróis, o vilão age. E é cumprindo as missões que vocês vão deixar ele vulnerável… e aí é só partir pra cima!",
    5: "E aqui na Sua Vez, a gente tem três jogos base: o Marvel United, o X-Men e o Spider-Geddon.",
    6: "Fora os jogos base, a gente tem seis expansões: Civil War, Blue Team, Gold Team, Deadpool, Pantera Negra e Spider-Verse. E dá pra misturar tudo!",
    7: "E a dica de ouro é pegar um jogo base e duas expansões: são três caixas e sete dias jogando, pelo mesmo preço!",
    8: "E a surpresa é que vem mais um jogo base, o Multiverse, com heróis de outras dimensões! E aí, qual dupla de heróis você montaria? Comenta aqui embaixo!",
    9: "Aluga aqui na Sua Vez, o link tá na bio!",
}


def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def chunks(text, maxc=40):
    """Quebra a frase em pedaços curtos de legenda, preferindo pontuação."""
    words, out, cur = text.split(), [], []
    for w in words:
        cur.append(w)
        line = " ".join(cur)
        if len(line) >= maxc or (w[-1] in ".?!:" and len(line) > 14):
            out.append(cur)
            cur = []
    if cur:
        if out and len(" ".join(cur)) < 12:
            out[-1] += cur
        else:
            out.append(cur)
    return out


def main():
    palavras = json.load(open(os.path.join(NAR, "palavras.json"), encoding="utf-8"))
    scenes, voice, subs = [], [], []
    t = 0.0
    for (o0, o1), falas in zip(ORIG, FALAS_POR_CENA):
        start = t
        cur = t + LEAD
        for k in falas:
            path = os.path.join(NAR, f"frase_{k:02d}.wav")
            d = dur(path)
            voice.append({"frase": k, "arquivo": os.path.relpath(path, ROOT), "inicio": round(cur, 3)})
            # legendas: distribui os pedaços pelos tempos reais das palavras
            ws = palavras[f"{k:02d}"]
            parts = chunks(TEXTO[k])
            total = sum(len(p) for p in parts)
            idx = 0
            for p in parts:
                a = ws[min(len(ws) - 1, round(idx * len(ws) / total))][0]
                idx += len(p)
                b = ws[min(len(ws) - 1, round(idx * len(ws) / total) - 1)][1]
                subs.append([round(cur + a, 2), round(cur + b + 0.15, 2), " ".join(p)])
            cur += d + GAP
        end = cur - GAP + (CTA_HOLD if o1 == ORIG[-1][1] else TAIL)
        end = max(end, start + MIN_FRAC * (o1 - o0))
        if not falas:  # cena sem fala (corridinha): mantém a duração original
            end = start + (o1 - o0)
        scenes.append([o0, o1, round(start, 3), round(end, 3)])
        t = end
    # legendas não se sobrepõem
    for i in range(len(subs) - 1):
        subs[i][1] = min(subs[i][1], subs[i + 1][0])
    out = {"duracao": round(t, 3), "cenas": scenes, "voz": voice, "legendas": subs}
    json.dump(out, open(os.path.join(NAR, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"duração total: {t:.1f} s")
    for s in scenes:
        print(f"  cena {s[0]:>5.1f}-{s[1]:<5.1f} -> {s[2]:>5.1f}-{s[3]:<5.1f}")


if __name__ == "__main__":
    main()
