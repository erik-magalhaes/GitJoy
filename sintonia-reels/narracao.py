#!/usr/bin/env python3
"""Monta a linha do tempo do Reels do Sintonia a partir das falas gravadas.

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

# cenas originais (início, fim) na mesma ordem do sintonia.SCENES
ORIG = [(0.0, 6.0), (6.0, 12.0), (12.0, 20.0), (20.0, 25.0), (25.0, 32.0), (32.0, 38.0),
        (38.0, 47.0), (47.0, 57.0), (57.0, 66.0)]
FALAS_POR_CENA = [[1], [2], [3], [4], [5], [6], [7], [8], [9]]
LEAD, GAP, TAIL = 0.3, 0.45, 0.6
CTA_HOLD = 3.6  # tempo do logo na tela depois da última fala (garante mais de 1 minuto)

TEXTO = {
    1: "Pizza é um tipo de sanduíche? Pensa rápido... e responde girando o ponteiro.",
    2: "Esse é o Sintonia, o jogo de ler a mente dos amigos, eleito o melhor party game de 2019.",
    3: "Cada rodada tem uma carta com dois extremos, mas só o psíquico vê onde está o alvo... e o esconde.",
    4: "E aí ele tem que dar uma dica. Tipo: minhas chaves!",
    5: "O time discute, briga, tá mais pra defender a sua opinião... e gira o ponteiro onde acha que a dica se encaixa.",
    6: "Então o psíquico revela: quanto mais perto do centro, mais pontos o time faz.",
    7: "E cada rodada vira uma discussão absurda, tipo: água tem cor? Claro que não! Claro que sim! "
       "Claro que não! Claro que sim! Claro que não! Enfim, é um jogo pra galera, e quanto mais gente, melhor.",
    8: "E agora é com você! Lugar silencioso ou barulhento? Que dica você daria pra esse alvo? Comenta aqui!",
    9: "Teste a conexão com a sua galera: aluga o Sintonia na Sua Vez, o link está na bio!",
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
    # instantes de cada "Claro que..." da frase 7 (balões na cena das discussões)
    v7 = next(v for v in voice if v["frase"] == 7)
    claro = [round(v7["inicio"] + w[0], 3) for w in palavras["07"] if w[2].lower().startswith("claro")]
    out = {"duracao": round(t, 3), "cenas": scenes, "voz": voice, "legendas": subs, "claro": claro}
    json.dump(out, open(os.path.join(NAR, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"duração total: {t:.1f} s")
    for s in scenes:
        print(f"  cena {s[0]:>5.1f}-{s[1]:<5.1f} -> {s[2]:>5.1f}-{s[3]:<5.1f}")


if __name__ == "__main__":
    main()
