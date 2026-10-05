#!/usr/bin/env python3
"""Monta a linha do tempo do vídeo a partir das falas gravadas.

Lê narracao/frase_NN.wav (já tratadas) e narracao/palavras.json (tempos das
palavras), decide quanto dura cada cena para caber a fala e grava
narracao/timeline.json, que o reels.py usa para esticar/encurtar as cenas,
posicionar a voz, os efeitos e as legendas.
"""
import json
import os
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(ROOT, "narracao")

# cenas originais (início, fim) na mesma ordem do reels.SCENES
ORIG = [(0.0, 5.0), (5.0, 11.0), (11.0, 22.0), (22.0, 30.0), (30.0, 37.5),
        (37.5, 45.0), (45.0, 52.0), (52.0, 58.0), (58.0, 68.0)]
# quais frases são faladas em cada cena
FALAS_POR_CENA = [[1], [2], [3, 4], [5], [6], [7], [8], [9], [10]]
LEAD, GAP, TAIL = 0.3, 0.45, 0.6
CTA_HOLD = 4.2  # tempo para ler o "comenta aí" depois da última fala

TEXTO = {
    1: "E se você pudesse amaldiçoar seus amigos e ainda ganhar pontos com isso?",
    2: "Esse é o Vudú, o joguinho em que você vira um bruxão... e a sua galera vira vítima.",
    3: "E é super simples: na sua vez, você rola 5 dados de ingredientes.",
    4: "Não gostou do que rolou? Não tem problema! Você guarda o que quer usar e rola de novo. "
       "Mas cuidado, porque cada nova rolagem custa um dado.",
    5: "Quando você juntar todos os ingredientes da carta, é hora de lançar sua maldição "
       "em alguém da mesa e assim marcar seus pontos.",
    6: "E aí que começa todo o caos! Por exemplo: na Kapoera, a vítima não pode encostar os pés no chão.",
    7: "Na Tutakobraço, tem que ficar com os braços esticados... e tem maldição muito pior.",
    8: "E preste bastante atenção, porque se você esquecer de fazer uma maldição, "
       "quem lançou ela ganha ainda mais pontos.",
    9: "E vence quem chegar aos 11 pontos primeiro. Um jogo super rápido e caótico, para até 8 pessoas.",
    10: "E aí, quer amaldiçoar a sua galera no final de semana? Aluga o Vudú na Sua Vez: o link está na bio!",
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
