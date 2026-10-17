"""Peças comuns dos vídeos de lista sem narração (17/out/2026): signos, tempo, pessoas, flags e novidades.

- foto(nome, w): a FOTO DO SITE da Sua Vez (render da caixa em fundo laranja), inteira, em cartão com cantos
  arredondados, borda e sombra. Nunca cortada (pedido deles: a caixa que aparece é a que eles têm).
- texto(...): texto com contorno e sombra sólida, em qualquer fonte do repositório.
- entrega(nome, dur, frame, cues, musica): grava _com_trilha e _para_musica e normaliza para −15,5 LUFS (*_final.mp4).
"""
import json
import os
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "comum"))
from motor import W, H, FPS, ffmpeg, encode, folha, sombra  # noqa: E402,F401
import som  # noqa: E402

OUT = os.path.join(ROOT, "out")
FOTOS = os.path.join(REPO, "hobby-reels", "assets", "acervo_foto")
FONTES = {"lilita": "assinatura-reels/assets/fonts/LilitaOne.ttf", "figtree": "assinatura-reels/assets/fonts/Figtree.ttf",
          "cinzel": "halloween-reels/assets/fonts/Cinzel.ttf", "bungee": "hobby-reels/assets/fonts/Bungee-Regular.ttf",
          "poppins": "hobby-reels/assets/fonts/Poppins-Black.ttf", "poppins_eb": "hobby-reels/assets/fonts/Poppins-ExtraBold.ttf",
          "poppins_sb": "hobby-reels/assets/fonts/Poppins-SemiBold.ttf", "luckiest": "hobby-reels/assets/fonts/LuckiestGuy-Regular.ttf",
          "alfa": "hobby-reels/assets/fonts/AlfaSlabOne-Regular.ttf"}


@lru_cache(None)
def fonte(nome, s):
    f = ImageFont.truetype(os.path.join(REPO, FONTES[nome]), int(s))
    if nome == "figtree":
        try:
            f.set_variation_by_name("Bold")
        except Exception:  # noqa: BLE001
            pass
    return f


@lru_cache(None)
def texto(txt, nome, s, cor=(255, 255, 255), contorno=None, sw=0, sombra_px=0, cor_sombra=(0, 0, 0), entre=1.12,
          alinha="mm"):
    """Várias linhas centralizadas, com contorno e sombra sólida deslocada (degraus)."""
    f = fonte(nome, s)
    linhas = txt.split("\n")
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lw = max(tmp.textlength(l, font=f) for l in linhas)
    lh = s * entre
    m = sw + sombra_px + 14
    im = Image.new("RGBA", (int(lw + 2 * m), int(lh * len(linhas) + 2 * m)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, l in enumerate(linhas):
        x = im.width / 2 if alinha == "mm" else m
        y = m + k * lh + lh / 2
        anc = "mm" if alinha == "mm" else "lm"
        for p in range(sombra_px, 0, -1):
            d.text((x + p, y + p), l, font=f, fill=cor_sombra, anchor=anc, stroke_width=sw, stroke_fill=cor_sombra)
        d.text((x, y), l, font=f, fill=cor, anchor=anc, stroke_width=sw, stroke_fill=contorno or cor)
    return im


@lru_cache(None)
def foto(nome, w, borda=10, cor_borda=(255, 255, 255), raio=34, sombra_a=0.5):
    """Foto do site inteira num cartão (quadrada), com borda e sombra."""
    im = Image.open(os.path.join(FOTOS, nome + ".jpg")).convert("RGB")
    im = im.resize((w - 2 * borda, w - 2 * borda), Image.LANCZOS)
    card = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, w - 1, w - 1), radius=raio, fill=cor_borda + (255,))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=max(4, raio - borda), fill=255)
    card.paste(im, (borda, borda), m)
    return sombra(card, 18, (0, 16), sombra_a) if sombra_a else card


def final_loudness(src, dst, alvo=-15.5, tp=-2.0):
    """loudnorm LINEAR em 2 passadas só no áudio; o vídeo é copiado."""
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", src, "-af", f"loudnorm=I={alvo}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I={alvo}:TP={tp}:LRA=11:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", src, "-c:v", "copy", "-af", af, "-ar", "44100",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst], check=True)
    print("ok:", dst, os.path.getsize(dst) // 1024 ** 2, "MB", flush=True)


def entrega(nome, dur, render_frame, cues, musica, musica_ganho=0.3):
    os.makedirs(OUT, exist_ok=True)
    n = int(round(dur * FPS))
    base = None
    for versao, mus in (("com_trilha", musica), ("para_musica", None)):
        wav = os.path.join(OUT, f"{nome}_{versao}.wav")
        som.build(wav, dur, cues, musica=mus, fx_ganho=0.55 if mus else 0.5, musica_ganho=musica_ganho)
        mp4 = os.path.join(OUT, f"{nome}_{versao}.mp4")
        if base is None:
            encode(mp4, render_frame, list(range(n)), wav)
            base = mp4
        else:  # mesma imagem, só troca o áudio
            subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", base, "-i", wav, "-map", "0:v", "-map", "1:a",
                            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", mp4], check=True)
        final_loudness(mp4, mp4.replace(".mp4", "_final.mp4"))
