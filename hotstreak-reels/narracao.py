#!/usr/bin/env python3
"""Monta a linha do tempo do Reels do Hot Streak a partir das falas gravadas.

Lê narracao/frase_NN.wav (já tratadas) e narracao/palavras.json (tempos das
palavras), decide quanto dura cada cena para caber a fala e grava
narracao/timeline.json, que o hs.py usa para esticar/encurtar as cenas,
posicionar a voz, os efeitos e as legendas.
"""
import json
import os
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(ROOT, "narracao")

# cenas originais (início, fim) na mesma ordem do hs.SCENES
ORIG = [(0.0, 5.6), (5.6, 12.6), (12.6, 19.6), (19.6, 26.6), (26.6, 34.0), (34.0, 42.0), (42.0, 49.0),
        (49.0, 57.4), (57.4, 63.0), (63.0, 69.6)]
FALAS_POR_CENA = [[1], [2], [3], [4], [5], [6], [7], [8], [], [9]]  # a corridinha final não tem fala
LEAD, GAP, TAIL = 0.2, 0.4, 0.25  # fala longa: respiros mais curtos para não passar de 1:10
MIN_FRAC = 0.7  # cena nunca encolhe abaixo de 70% do original (animações respiram)
CTA_HOLD = 2.3  # tempo do logo na tela depois da última fala (garante mais de 1 minuto)

TEXTO = {  # o que ele FALOU na gravação (out/2026), com a grafia certa
    1: "Você já pensou em apostar seu dinheiro num cachorro-quente? Se não, prepara a carteira!",
    2: "Esse é o Hot Streak, onde quatro mascotes atrapalhados correm e você precisa apostar em quem vai ganhar.",
    3: "E antes de cada corrida, cada jogador pega dois bilhetes de aposta: pode ser no mascote, ou em coisas bizarras, tipo: alguém vai sair da pista?",
    4: "E é você que escolhe: ou vai na aposta segura, ou na arriscada, que te paga mais, mas pode te fazer perder dinheiro.",
    5: "E é aí que vem a malandragem: cada jogador coloca uma carta secreta no baralho da corrida pra puxar a sardinha pro seu lado.",
    6: "E então começa a corrida: um dos jogadores vira as cartas uma a uma, o mascote corre, tropeça, dá meia-volta, invade a raia do outro e derruba geral!",
    7: "E aqui tudo pode desclassificar o mascote: saiu da pista, desclassificado! Foi atropelado, desclassificado! Tropeçou já no chão, desclassificado de novo!",
    8: "E depois de três corridas sofridas, ganha quem tiver mais dinheiro. Agora para tudo: em quem você aposta? Comenta aqui!",
    9: "Aluga o Hot Streak aqui na Sua Vez e chama a galera pra apostar! O link tá na bio.",
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
        if not falas:  # cena sem fala (corridinha): um pouco mais rápida, para o vídeo caber em 1:10
            end = start + 0.62 * (o1 - o0)
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
