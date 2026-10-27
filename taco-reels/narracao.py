#!/usr/bin/env python3
"""Linha do tempo do Taco Gato com a narração dele (8 falas, 27/out/2026).

Lê narracao/frase_NN.wav + palavras.json e grava narracao/timeline.json: cada cena estica/encolhe para caber a fala.
Cenas com MARCOS são cortadas em pedaços para a animação bater com a palavra (o gorila entra quando ele diz "gorila",
o "Comenta aqui" quando ele diz "comenta").
"""
import json
import os
import unicodedata
import wave

ROOT = os.path.dirname(os.path.abspath(__file__))
NAR = os.path.join(ROOT, "narracao")
DURS = [5.2, 6.4, 9.0, 8.0, 12.6, 7.0, 7.8, 6.0]  # igual ao taco.DURS
LEAD, GAP, TAIL, CTA_HOLD = 0.25, 0.4, 0.5, 3.0
MIN_FRAC = 0.7
ESPECIAIS_INTRO, ESPECIAIS_BLOCO = 2.4, 3.4  # taco.cena5
# cena -> [(tempo na cena original, palavra falada que puxa esse momento, adianto em s)]
MARCOS = {4: [(ESPECIAIS_INTRO + k * ESPECIAIS_BLOCO, p, 0.25) for k, p in enumerate(("gorila", "narval", "marmota"))],
          6: [(4.3, "comenta", 0.15)]}

TEXTO = {  # o que ELE falou (não o roteiro), com a grafia certa
    1: "Esse jogo tem só cinco palavras e mesmo assim todo mundo erra!",
    2: "Depois de embaralhar e dividir todas as cartas, cada um fica com um monte virado pra baixo na sua frente, e não vale espiar!",
    3: "Na sua vez, você vira uma carta no meio da mesa e fala a próxima palavra. Tipo: taco, gato, cabra, queijo... e quando chega na pizza, começa tudo de novo.",
    4: "Se a carta for igual à palavra que você falou, todo mundo bate a mão no monte! O último que bater leva a pilha inteira.",
    5: "E é claro que, pra ficar mais difícil, tem as cartas especiais. Tipo o gorila, que você tem que bater com as mãos no peito; o narval, que você tem que bater com as mãos em cima da cabeça; e a marmota, que você bate com as duas mãos na mesa. Tudo isso antes de bater no monte.",
    6: "Errou o gesto, bateu sem precisar ou hesitou? A pilha é toda sua!",
    7: "E ganha quem conseguir acabar com as cartas e for o primeiro a bater na próxima. Comenta aqui: você acha que você seria rápido o suficiente?",
    8: "Taco Gato Cabra Queijo Pizza é um party game de 2 a 8 jogadores. Aluga aqui na Sua Vez, o link tá na bio!",
}


def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if c.isalpha())


def chunks(text, maxc=46):
    """Pedaços de legenda: corta na pontuação; pedaço comprido demais vira 2 metades equilibradas."""
    words, frases, cur = text.split(), [], []
    for w in words:
        cur.append(w)
        if w[-1] in ".?!:;,":
            frases.append(cur)
            cur = []
    if cur:
        frases.append(cur)
    out = []
    for f in frases:  # junta vírgulas curtas com a próxima
        if out and len(" ".join(out[-1] + f)) <= maxc and len(" ".join(out[-1])) < 20:
            out[-1] = out[-1] + f
        else:
            out.append(f)
    res = []
    for f in out:
        while len(" ".join(f)) > maxc:
            n = len(" ".join(f))
            k = min(range(1, len(f)), key=lambda i: abs(len(" ".join(f[:i])) - n / 2))
            if len(" ".join(f[:k])) <= maxc:
                res.append(f[:k])
                f = f[k:]
            else:
                k = max(i for i in range(1, len(f)) if len(" ".join(f[:i])) <= maxc)
                res.append(f[:k])
                f = f[k:]
        res.append(f)
    return res


def main():
    palavras = json.load(open(os.path.join(NAR, "palavras.json"), encoding="utf-8"))
    cenas, voz, subs = [], [], []
    t, o = 0.0, 0.0
    for k, d0 in enumerate(DURS):
        n = k + 1
        path = os.path.join(NAR, f"frase_{n:02d}.wav")
        d = dur(path)
        v0 = t + LEAD
        voz.append({"frase": n, "arquivo": os.path.relpath(path, ROOT), "inicio": round(v0, 3)})
        ws = palavras[f"{n:02d}"]
        parts = chunks(TEXTO[n])
        total = sum(len(p) for p in parts)
        idx = 0
        for p in parts:
            a = ws[min(len(ws) - 1, round(idx * len(ws) / total))][0]
            idx += len(p)
            b = ws[min(len(ws) - 1, round(idx * len(ws) / total) - 1)][1]
            subs.append([round(v0 + a, 2), round(v0 + b + 0.15, 2), " ".join(p)])
        fim = v0 + d + (CTA_HOLD if k == len(DURS) - 1 else TAIL)
        fim = max(fim, t + MIN_FRAC * d0)
        # pedaços: (tempo original, tempo novo) — começo, marcos e fim da cena
        pts = [(0.0, t)]
        for ot, pal, adi in MARCOS.get(k, []):
            w = next(x for x in ws if norm(x[2]).startswith(norm(pal)))
            pts.append((ot, max(pts[-1][1] + 0.5, v0 + w[0] - adi)))
        pts.append((d0, max(fim, pts[-1][1] + 0.8)))
        for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
            cenas.append([round(o + a0, 3), round(o + a1, 3), round(b0, 3), round(b1, 3)])
        t, o = pts[-1][1], o + d0
    for i in range(len(subs) - 1):
        subs[i][1] = min(subs[i][1], subs[i + 1][0])
    json.dump({"duracao": round(t, 3), "cenas": cenas, "voz": voz, "legendas": subs},
              open(os.path.join(NAR, "timeline.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"duração total: {t:.1f} s")
    for c in cenas:
        print(f"  {c[0]:6.2f}-{c[1]:<6.2f} -> {c[2]:6.2f}-{c[3]:<6.2f} ({(c[3]-c[2])/(c[1]-c[0]):.2f}x)")


if __name__ == "__main__":
    main()
