#!/usr/bin/env python3
"""Monta a linha do tempo do Reels do Nekojima a partir das falas gravadas.

Lê narracao/frase_NN.wav (já tratadas) e narracao/palavras.json (tempos das
palavras), decide quanto dura cada cena para caber a fala e grava
narracao/timeline.json, que o neko.py usa para esticar/encurtar as cenas,
posicionar a voz, os efeitos e as legendas.
"""
import json
import os
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(ROOT, "narracao")

# cenas originais (início, fim) na mesma ordem do neko.SCENES
ORIG = [(0.0, 5.6), (5.6, 12.2), (12.2, 19.2), (19.2, 26.2), (26.2, 34.0), (34.0, 41.2),
        (41.2, 48.2), (48.2, 57.2), (57.2, 66.0)]
FALAS_POR_CENA = [[1], [2], [3], [4], [5], [6], [7], [8], [9]]
LEAD, GAP, TAIL = 0.3, 0.45, 0.6
MIN_FRAC = 0.7  # cena nunca encolhe abaixo de 70% do original (animações respiram)
CTA_HOLD = 3.6  # tempo do logo na tela depois da última fala (garante mais de 1 minuto)

TEXTO = {
    1: 'Essa torre vai cair... e a culpa vai ser sua!',
    2: 'Esse é o Nekojima: uma ilha de gatos no Japão onde vocês precisam montar a rede elétrica.',
    3: 'Na sua vez, você rola os dois dados: eles dizem em quais bairros da ilha vão os seus postes.',
    4: 'Depois tira um cubo do saquinho: a cor diz qual poste você pega, e cada cor tem um fio de tamanho diferente.',
    5: 'Aí coloca um poste em cada bairro, pode até empilhar em cima dos outros... mas não pode encostar a mão nos fios!',
    6: 'E tem mais: os fios não podem tocar no tabuleiro, em outro fio nem em outro poste.',
    7: 'Saiu cubo preto? Tem gatinho pra pendurar no fio... e cada gato deixa tudo mais bambo.',
    8: 'No competitivo, quem derrubar a torre perde. No cooperativo, vocês tentam chegar o mais alto juntos. E aí, você é mão firme ou derruba tudo? Comenta aqui!',
    9: 'De 1 a 5 jogadores, em partidas rápidas: aluga o Nekojima na Sua Vez, o link tá na bio!',
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
