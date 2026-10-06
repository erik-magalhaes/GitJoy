#!/usr/bin/env python3
"""Monta a linha do tempo do Reels do 7 Wonders Arquitetos a partir das falas gravadas.

Lê narracao/frase_NN.wav (já tratadas) e narracao/palavras.json (tempos das
palavras), decide quanto dura cada cena para caber a fala e grava
narracao/timeline.json, que o arq.py usa para esticar/encurtar as cenas,
posicionar a voz, os efeitos e as legendas.
"""
import json
import os
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(ROOT, "narracao")

# cenas originais (início, fim) na mesma ordem do arq.SCENES
ORIG = [(0.0, 6.0), (6.0, 12.5), (12.5, 20.0), (20.0, 27.0), (27.0, 35.0), (35.0, 43.0),
        (43.0, 51.0), (51.0, 58.5), (58.5, 66.0)]
FALAS_POR_CENA = [[1], [2], [3], [4], [5], [6], [7], [8], [9]]
LEAD, GAP, TAIL = 0.3, 0.45, 0.6
MIN_FRAC = 0.7  # cena nunca encolhe abaixo de 70% do original (animações respiram)
CTA_HOLD = 3.6  # tempo do logo na tela depois da última fala (garante mais de 1 minuto)

TEXTO = {
    1: 'Já pensou construir uma das sete maravilhas do mundo... em só vinte e cinco minutos?',
    2: 'Esse é o 7 Wonders Arquitetos! Cada jogador é o arquiteto de uma maravilha, e no final vence quem tiver mais pontos.',
    3: 'Na sua vez, você pega só uma carta: do monte da esquerda, do monte da direita... ou arrisca no monte do meio, sem ver.',
    4: 'As cartas cinzas são materiais: pedra, madeira, tijolo, papiro e vidro. E o ouro vale como qualquer um deles.',
    5: 'Juntou os materiais que a maravilha pede? Constrói uma etapa! Cada etapa dá pontos, e algumas ainda dão um poder especial.',
    6: 'As vermelhas são escudos. Quando aparece a corneta, uma ficha vira... e quando todas viram, é guerra! Quem tem mais escudos que o vizinho ganha pontos.',
    7: 'As verdes são ciência e dão fichas de progresso. As azuis dão pontos direto, e algumas trazem o gato, que espia o monte do meio.',
    8: 'Quando alguém termina a maravilha, o jogo acaba e vence quem tiver mais pontos. E aí, qual maravilha você construiria? Comenta aqui!',
    9: 'Junta a galera, de 2 a 7 jogadores, e aluga o 7 Wonders Arquitetos na Sua Vez. O link tá na bio!',
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
