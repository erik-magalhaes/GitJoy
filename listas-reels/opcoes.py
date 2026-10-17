#!/usr/bin/env python3
"""Listas para ele aprovar ANTES de montar (17/out/2026): signos, quanto tempo, quantas pessoas e novidades do acervo.
Fotos = as do site (hobby-reels/assets/acervo_foto/), para ele conferir que é a caixa que eles têm.

    python3 opcoes.py      # out/opcoes_{signos,tempo,pessoas,novidades}.jpg
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
FOTOS = os.path.join(REPO, "hobby-reels", "assets", "acervo_foto")
FONTE = os.path.join(REPO, "assinatura-reels", "assets", "fonts", "Figtree.ttf")
OUT = os.path.join(ROOT, "out")

SIGNOS = [("ÁRIES", "1, 2, 3, Lucha!", "1_2_3_lucha"), ("TOURO", "Bohnanza", "bohnanza"),
          ("GÊMEOS", "Mascarade", "mascarade_second_edition"), ("CÂNCER", "Quem do casal?", "quem_do_casal"),
          ("LEÃO", "Gravity Superstar", "gravity_superstar"), ("VIRGEM", "Architectura", "architectura"),
          ("LIBRA", "Splito", "splito"), ("ESCORPIÃO", "Coup", "coup_inquisition"),
          ("SAGITÁRIO", "Treasure Island", "treasure_island"), ("CAPRICÓRNIO", "High Society", "high_society"),
          ("AQUÁRIO", "Alieninjas", "alieninjas"), ("PEIXES", "Happy Salmon", "happy_salmon")]
TEMPO = [("15 MIN", "Tesouro do Dragão", "tesouro_do_drag_o"), ("15 MIN", "Bad Signs", "bad_signs"),
         ("15 MIN", "Trio", "trio"), ("30 MIN", "Beaver Creek", "beaver_creek"), ("30 MIN", "Metro", "metro"),
         ("30 MIN", "4 Gods", "4_gods"), ("1 HORA", "Cóatl", "c_atl"), ("1 HORA", "Dwar7s Fall", "dwar7s_fall"),
         ("1 HORA", "Echoes of Time", "echoes_of_time"), ("A NOITE TODA", "Tikal (90 min)", "tikal"),
         ("A NOITE TODA", "Emberleaf (2 h)", "emberleaf"), ("A NOITE TODA", "Vast (90 min)", "vast_the_fearsome_foes")]
PESSOAS = [("SOZINHO", "World Wonders (1–5)", "world_wonders"), ("SOZINHO", "Fliptown (1–4)", "fliptown"),
           ("SOZINHO", "Dice Colony (1–4)", "dice_colony"), ("A DOIS", "7 Wonders Duel", "7_wonders_duel"),
           ("A DOIS", "Fugitive", "fugitive_second_edition"), ("A DOIS", "Allumbra: O Duelo", "allumbra_o_duelo"),
           ("3 OU 4", "Samoa (2–4)", "samoa"), ("3 OU 4", "Savernake Forest (2–4)", "savernake_forest"),
           ("3 OU 4", "Rebirth (2–4)", "rebirth"), ("5 OU MAIS", "Blablabel (3–9)", "blablabel"),
           ("5 OU MAIS", "Conectados (4–8)", "conectados"), ("5 OU MAIS", "Encantados (2–6)", "encantados"),
           ("FESTA 10+", "Ref! (2–10)", "ref_o_jogo_da_refer_ncia"), ("FESTA 10+", "É Top!? Geek & Pop (2–10)", "top_geek_pop"),
           ("FESTA 10+", "UNO Stacko (2–10)", "uno_stacko")]
NOVIDADES = [("CHEGOU", "Marvel United: Multiverse", "marvel_united_multiverse"), ("CHEGOU", "Trial by Trolley", "trial_by_trolley"),
             ("CHEGOU", "Trio", "trio"), ("CHEGOU", "Convidados Indesejados", "convidados_indesejados")]


def folha(itens, nome, col=4, w=380, h=470):
    img = Image.new("RGB", (col * w, ((len(itens) + col - 1) // col) * h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONTE, 25)
    for k, (titulo, jogo, arq) in enumerate(itens):
        x, y = (k % col) * w, (k // col) * h
        im = Image.open(os.path.join(FOTOS, arq + ".jpg")).convert("RGB")
        im.thumbnail((330, 330))
        img.paste(im, (x + (w - im.width) // 2, y + 70))
        d.text((x + w / 2, y + 28), f"{k + 1}. {titulo}", fill=(200, 60, 20), font=f, anchor="mm")
        d.text((x + w / 2, y + 430), jogo, fill=(20, 20, 30), font=f, anchor="mm")
    img.save(os.path.join(OUT, f"opcoes_{nome}.jpg"), quality=88)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    folha(SIGNOS, "signos")
    folha(TEMPO, "tempo", col=3)
    folha(PESSOAS, "pessoas", col=3)
    folha(NOVIDADES, "novidades")
    print("ok")
