#!/usr/bin/env python3
"""DOMINGO DE JOGOS NO BECA’S (22/nov/2026): o evento MENSAL (o café não abre aos domingos, a dona propôs um domingo
por mês). Regras do Erik: no máximo 30 VAGAS, pagamento SÓ antecipado (Pix pelo WhatsApp). O mínimo de 15 pessoas é
INTERNO: não aparece em nenhuma peça. A comunicação foca nas vagas CONTADAS.

Peça-chave nova: o QUADRO DE VAGAS, com 30 ingressinhos numerados (01–30). Nos stories de "restam N", os vendidos levam o
carimbo RESERVADA (só com o número REAL, que eles informam).

- Reels/Stories (~24 s): abre com os vídeos DELES da 1ª tarde de jogos (053620 = antes de abrir as portas; 180822 =
  mesas cheias) → "AGORA É TODO MÊS!" → DOMINGO DE JOGOS → quadro com as 30 vagas → convite.
- Post 1080x1350 + story.
- Stories de vagas: abertas (30), restam N, últimas, última, ESGOTADO (lista de espera).
- Confirmação para o WhatsApp de quem pagou: "SUA VAGA Nº NN TÁ GARANTIDA".

Data/horário/preço em constantes (DATA, HORA, PRECO): mudar aqui e rodar de novo.

    /usr/bin/python3 domingo.py --frame 1 4 8 11 15 20      # out/frames_domingo.jpg
    /usr/bin/python3 domingo.py --fotos                     # out/domingo/ (post, story, vagas, confirmações)
    /usr/bin/python3 domingo.py --vagas 12                  # só o story "restam 12"
    /usr/bin/python3 domingo.py                             # Reels + Stories em vídeo
"""
import math
import os
import random
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import kit as K
import sons as S
import tarde as T
from tarde import E, TB, W, H, MAR, PET, LAR, AMA, BR, ROSA

from motor import FPS, out_back  # noqa: E402

OUT = T.OUT
PASTA = os.path.join(OUT, "domingo")
BRUTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brutos", "nov20")
K.CLIPES["dia"] = (os.path.join(BRUTO, "180822.mp4"), "")
K.CLIPES["intro"] = (os.path.join(BRUTO, "053620.mp4"), "")

# ---- dados do evento (A CONFIRMAR com o café) ----
DATA = "DOMINGO, 13/12"
HORA = "DAS 14H ÀS 19H"
PRECO = "R$ 40"
CONSUMO = "R$ 25 VIRAM CONSUMAÇÃO NO CAFÉ"
ENDERECO = TB.ENDERECO
VAGAS = 30

VERM = (206, 38, 44)
VERDE = (64, 168, 82)
CREME = (255, 249, 236)
CINZA = (196, 190, 182)

# ---------------------------------------------------------------- linha do tempo do vídeo
BEAT = 60 / 118
D_INTRO = 2.6                      # 053620 a 1,3x com o gancho
VEL_INTRO = 1.3
CORTE = 2 * BEAT                   # ~1,02 s por corte
MONT = [(3.0, "MESAS CHEIAS"), (13.5, "GENTE NOVA EM CADA MESA"), (27.6, "MUITA RISADA"), (39.6, "35 JOGOS NA MESA")]
T_MONT = D_INTRO
T_VIRA = T_MONT + len(MONT) * CORTE      # quadro parado: "E AGORA..."
T_TIT = T_VIRA + 2.0                      # guarda-chuvinhas: DOMINGO DE JOGOS
T_QUADRO = T_TIT + 3.6                    # quadro das 30 vagas
T_CTA = T_QUADRO + 4.4                    # convite
DUR = T_CTA + 6.6
TRECHOS = [("intro", 0.0, D_INTRO, VEL_INTRO)] + [("dia", s, CORTE, 1.0) for s, _ in MONT]


# ---------------------------------------------------------------- peças
def cabe(txt, larg, s, fonte=E.lilita):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    while s > 16 and d.textlength(txt, font=fonte(s)) > larg:
        s -= 2
    return fonte(s)


@lru_cache(None)
def ingressinho(n, vendida=False, w=132, h=94):
    """Ingresso pequeno numerado com meias-luas nas laterais e borda tracejada."""
    m = 10
    im = Image.new("RGBA", (w + m, h + m), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cor = CINZA if vendida else CREME
    for (dx, dy, c) in ((m, m, MAR), (0, 0, cor)):
        d.rounded_rectangle((dx, dy, dx + w - 1, dy + h - 1), 12, fill=c, outline=MAR, width=4)
    # meias-luas (furos) dos dois lados
    for x in (0, w):
        d.ellipse((x - 12, h / 2 - 12, x + 12, h / 2 + 12), fill=(0, 0, 0, 0))
    mask = Image.new("L", im.size, 255)
    md = ImageDraw.Draw(mask)
    for x in (0, w):
        md.ellipse((x - 12, h / 2 - 12, x + 12, h / 2 + 12), fill=0)
    a = Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), mask)
    im.putalpha(a)
    d = ImageDraw.Draw(im)
    for x in (0, w):
        d.arc((x - 12, h / 2 - 12, x + 12, h / 2 + 12), 0, 360, fill=MAR, width=4)
    # tracejado interno
    for x in range(22, w - 22, 14):
        d.line((x, 12, x + 7, 12), fill=MAR if not vendida else (150, 140, 130), width=2)
        d.line((x, h - 13, x + 7, h - 13), fill=MAR if not vendida else (150, 140, 130), width=2)
    d.text((w / 2, h / 2 - 9), f"{n:02d}", font=E.lilita(46), fill=PET if not vendida else (140, 130, 120),
           anchor="mm")
    d.text((w / 2, h / 2 + 25), "VAGA", font=E.fig(17, 900), fill=MAR if not vendida else (140, 130, 120),
           anchor="mm")
    if vendida:
        st = Image.new("RGBA", (w + 40, 46), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((2, 2, w + 37, 43), 8, outline=VERM, width=4)
        sd.text(((w + 40) / 2, 23), "RESERVADA", font=E.lilita(24), fill=VERM, anchor="mm")
        st = st.rotate(18, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(st, (int((w + m) / 2 - st.width / 2), int((h + m) / 2 - st.height / 2)))
    return im


COLS, LINS = 6, 5


def pos_ing(k, x0, y0, passo_x=146, passo_y=108):
    c, l = k % COLS, k // COLS
    return x0 + c * passo_x, y0 + l * passo_y


@lru_cache(None)
def painel(vendidas=0, titulo="QUADRO DE VAGAS"):
    """Painel de madeira clara com os 30 ingressinhos (os `vendidas` primeiros com carimbo)."""
    pw, ph = 960, 720
    p = E.bloco(pw, ph, (233, 196, 140), raio=34, ow=8, sombra=14).copy()
    d = ImageDraw.Draw(p)
    rnd = random.Random(4)
    for y in range(30, ph - 30, 9):  # veios da madeira
        d.line((30, y + rnd.uniform(-2, 2), pw - 40, y + rnd.uniform(-2, 2)), fill=(222, 182, 126), width=2)
    d.rounded_rectangle((pw / 2 - 300, 26, pw / 2 + 300, 104), 26, fill=PET, outline=MAR, width=5)
    d.text((pw / 2, 66), titulo, font=E.lilita(48), fill=BR, anchor="mm")
    x0, y0 = (pw - (COLS - 1) * 146 - 142) / 2, 132
    for k in range(VAGAS):
        x, y = pos_ing(k, x0, y0)
        p.alpha_composite(ingressinho(k + 1, k < vendidas), (int(x), int(y)))
    return p


def painel_anim(t, t0):
    """Painel com os ingressinhos entrando um a um (vídeo: todas livres)."""
    pw, ph = 960, 720
    p = E.bloco(pw, ph, (233, 196, 140), raio=34, ow=8, sombra=14).copy()
    d = ImageDraw.Draw(p)
    rnd = random.Random(4)
    for y in range(30, ph - 30, 9):
        d.line((30, y + rnd.uniform(-2, 2), pw - 40, y + rnd.uniform(-2, 2)), fill=(222, 182, 126), width=2)
    d.rounded_rectangle((pw / 2 - 300, 26, pw / 2 + 300, 104), 26, fill=PET, outline=MAR, width=5)
    d.text((pw / 2, 66), "QUADRO DE VAGAS", font=E.lilita(48), fill=BR, anchor="mm")
    x0, y0 = (pw - (COLS - 1) * 146 - 142) / 2, 132
    for k in range(VAGAS):
        tk = t0 + 0.25 + k * 0.045
        if t < tk:
            continue
        u = min(1.0, (t - tk) / 0.22)
        s = out_back(u)
        ing = ingressinho(k + 1)
        if s < 0.999:
            ing = ing.resize((max(1, int(ing.width * s)), max(1, int(ing.height * s))), Image.BICUBIC)
        x, y = pos_ing(k, x0, y0)
        p.alpha_composite(ing, (int(x + 71 - ing.width / 2), int(y + 52 - ing.height / 2)))
    # brilho que passa depois que todos entraram
    tb = t - (t0 + 0.25 + VAGAS * 0.045 + 0.3)
    if 0 < tb < 0.7:
        pw, ph = p.size
        g = Image.new("L", (pw, ph), 0)
        gx = -200 + (pw + 400) * tb / 0.7
        ImageDraw.Draw(g).polygon([(gx, 0), (gx + 90, 0), (gx - 110, ph), (gx - 200, ph)], fill=110)
        g = g.filter(ImageFilter.GaussianBlur(20))
        g = Image.composite(g, Image.new("L", (pw, ph), 0), p.getchannel("A"))
        br = Image.new("RGBA", (pw, ph), (255, 255, 240, 255))
        br.putalpha(g)
        p.alpha_composite(br)
    return p


@lru_cache(None)
def card(w=920, link=False):
    """Convite: data, horário, lugar, preço e como garantir."""
    h = 560
    c = E.bloco(w, h, CREME, raio=40, ow=8, sombra=14).copy()
    d = ImageDraw.Draw(c)
    d.text((w / 2, 70), "SUA VEZ  ×  BECA’S CAFÉ", font=E.lilita(40), fill=PET, anchor="mm")
    sel = E.pilula(f"{DATA} · {HORA}", 44, AMA, MAR, fonte_titulo=True)
    c.alpha_composite(sel, (int(w / 2 - sel.width / 2), 112))
    d.text((w / 2, 232), ENDERECO, font=cabe(ENDERECO, w - 80, 36), fill=MAR, anchor="mm")
    d.text((w / 2, 305), PRECO, font=E.lilita(84), fill=LAR, anchor="mm", stroke_width=5, stroke_fill=MAR)
    d.text((w / 2, 372), "R$ 25 viram consumação no café", font=E.fig(34, 800), fill=MAR, anchor="mm")
    d.text((w / 2, 418), "+ jogos e monitoria a tarde toda", font=E.fig(32, 700), fill=MAR, anchor="mm")
    d.rounded_rectangle((50, 458, w - 50, 530), 30, fill=PET)
    d.text((w / 2, 494), "VAGA SÓ COM PAGAMENTO ANTECIPADO", font=E.lilita(36), fill=BR, anchor="mm")
    return c


def seta():
    s = Image.new("RGBA", (120, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.polygon([(42, 0), (78, 0), (78, 70), (112, 70), (60, 136), (8, 70), (42, 70)], fill=AMA, outline=MAR)
    d.line([(42, 0), (78, 0), (78, 70), (112, 70), (60, 136), (8, 70), (42, 70), (42, 0)], fill=MAR, width=6)
    return s


def fundo(t=3.0):
    img = T.fundo().copy()
    T.guarda_chuvas(img, t)
    return img


# ---------------------------------------------------------------- vídeo
def intro(img, t):
    img.alpha_composite(K.quadro_clip("intro", 0.0, D_INTRO, VEL_INTRO, t))
    K.escurece(img, 230, 760, 165)
    K.poe(img, K.titulo("LEMBRA DA NOSSA\nTARDE DE JOGOS?", 100, BR), W / 2, 470, t, 0.05, -2)


def montagem(img, t):
    k = min(len(MONT) - 1, int((t - T_MONT) / CORTE))
    u = t - T_MONT - k * CORTE
    s, rot = MONT[k]
    img.alpha_composite(K.quadro_clip("dia", s, CORTE, 1.0, u))
    K.escurece(img, 1200, 1560, 150)
    K.poe(img, K.etiqueta(rot, 64, AMA, MAR), W / 2, 1380, t, T_MONT + k * CORTE, -2 if k % 2 else 2)
    E.cola(img, E.pilula("20/11 · FOI ASSIM!", 34, PET, BR, fonte_titulo=True), 230, 150, -3, 1, 1)


def vira(img, t):
    """Último quadro da montagem parado e escurecendo: 'E AGORA... VAI SER TODO MÊS!'."""
    s, _ = MONT[-1]
    base = K.quadro_clip("dia", s, CORTE, 1.0, CORTE - 0.05)
    u = min(1.0, (t - T_VIRA) / 0.5)
    base = Image.blend(base, K.desfoca(base, 14), u)
    img.alpha_composite(base)
    img.alpha_composite(Image.new("RGBA", (W, H), (20, 12, 6, int(130 * u))))
    K.poe(img, K.titulo("E AGORA...", 110, BR), W / 2, 760, t, T_VIRA + 0.1, -2)
    K.poe(img, K.titulo("VAI SER\nTODO MÊS!", 170, AMA), W / 2, 1040, t, T_VIRA + 0.75, 2)


def titulo(img, t):
    img.alpha_composite(fundo(t - T_TIT))
    K.poe(img, TB.parceria(110), W / 2, 560, t, T_TIT + 0.1)
    K.poe(img, K.titulo("DOMINGO\nDE JOGOS", 190, LAR), W / 2, 860, t, T_TIT + 0.35, -2)
    K.poe(img, K.etiqueta("NO BECA’S CAFÉ", 60, PET, BR), W / 2, 1100, t, T_TIT + 0.7, 2)
    K.poe(img, K.etiqueta("UM DOMINGO POR MÊS, A TARDE TODA", 40, BR, MAR), W / 2, 1210, t, T_TIT + 1.0, -1)
    K.poe(img, E.pilula(f"PRIMEIRO: {DATA}", 50, AMA, MAR, fonte_titulo=True), W / 2, 1330, t, T_TIT + 1.4, 1)


def quadro_vagas(img, t):
    img.alpha_composite(fundo(t - T_TIT))
    K.poe(img, K.titulo("SÓ 30 VAGAS!", 150, VERM), W / 2, 560, t, T_QUADRO + 0.05, -2)
    E.cola(img, painel_anim(t, T_QUADRO), W / 2, 1050, 0, 1, 1)
    K.poe(img, K.etiqueta("PAGOU, GARANTIU. ACABOU, ACABOU!", 44, AMA, MAR), W / 2, 1500, t, T_QUADRO + 2.4, 1)


def cta(img, t, modo):
    img.alpha_composite(fundo(t - T_TIT))
    st = modo == "stories"
    K.poe(img, K.titulo("GARANTA A SUA\nVAGA!", 112, LAR), W / 2, 545, t, T_CTA + 0.05, -2)
    c = card()
    K.poe(img, c, W / 2, 1000 if not st else 980, t, T_CTA + 0.35, 1 if not st else 0)
    if st:
        K.poe(img, E.pilula("garanta sua vaga aqui:", 40, BR, MAR), W / 2, 1310, t, T_CTA + 0.8)
        if t > T_CTA + 1.0:
            E.cola(img, seta(), W / 2, 1420 + 10 * math.sin((t - T_CTA) * 6), 0, 0.7, 1)
        K.poe(img, E.pilula(f"OU NO WHATSAPP {TB.WHATS}", 38, PET, BR, fonte_titulo=True), W / 2, 1680, t, T_CTA + 1.1)
    else:
        K.poe(img, E.pilula(f"RESERVE NO WHATSAPP {TB.WHATS}", 42, PET, BR, fonte_titulo=True), W / 2, 1370, t,
              T_CTA + 0.8, -1)
        K.poe(img, E.pilula("Comenta: com quem você vem?", 40, BR, MAR), W / 2, 1480, t, T_CTA + 1.1, 1)
        K.poe(img, E.pilula("@suavez_bg", 34, AMA, MAR, fonte_titulo=True), W / 2, 1650, t, T_CTA + 1.3)


def quadro(t, modo="reels"):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    if t < T_MONT:
        intro(img, t)
    elif t < T_VIRA:
        montagem(img, t)
    elif t < T_TIT:
        vira(img, t)
    elif t < T_QUADRO:
        titulo(img, t)
    elif t < T_CTA:
        quadro_vagas(img, t)
    else:
        cta(img, t, modo)
    for tb in (T_MONT, T_TIT, T_QUADRO, T_CTA):
        dd = t - tb
        if 0 <= dd < 0.12:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - dd / 0.12)))))
    if t < T_TIT:
        K.marca(img)
    return img.convert("RGB")


def render_reels(fi):
    return quadro(fi / FPS, "reels").tobytes()


def render_stories(fi):
    return quadro(fi / FPS, "stories").tobytes()


def audio(nome):
    ev = [(0.05, S.sopro(0.4), 0.3)]
    ev += [(T_MONT + k * CORTE, S.sopro(0.25), 0.3) for k in range(len(MONT))]
    ev += [(T_VIRA + 0.1, S.tic(), 0.4), (T_VIRA + 0.75, S.estouro(), 0.6), (T_VIRA + 0.78, S.plim(), 0.5),
           (T_TIT, S.sino(), 0.45), (T_TIT + 0.35, S.estouro(), 0.4), (T_QUADRO + 0.05, S.estouro(), 0.5)]
    ev += [(T_QUADRO + 0.25 + k * 0.045, S.tic(k % 2 == 0), 0.18) for k in range(VAGAS)]
    ev += [(T_QUADRO + 2.4, S.plim(), 0.45), (T_CTA, S.sopro(0.5, False), 0.4), (T_CTA + 0.35, S.carta_vira(), 0.5)]
    mus = S.musica_pop(DUR + 0.5, 0.0)
    com = os.path.join(OUT, f"{nome}_com.wav")
    sem = os.path.join(OUT, f"{nome}_sem.wav")
    S.grava(com, DUR, ev, mus, musica_ganho=0.42, fx_ganho=0.75)
    S.grava(sem, DUR, ev, None, fx_ganho=0.75)
    return com, sem


# ---------------------------------------------------------------- imagens
def frame_foto(seg, w, h):
    """Quadro do 180822 (a tarde de 20/11) recortado em w x h."""
    import subprocess
    from motor import ffmpeg
    arq = os.path.join(OUT, "_fotos", f"dom_{seg:.1f}.jpg")
    os.makedirs(os.path.dirname(arq), exist_ok=True)
    if not os.path.exists(arq):
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", str(seg), "-i", K.CLIPES["dia"][0], "-frames:v", "1",
                        "-vf", "hqdn3d=3:3:4:4,eq=contrast=1.03:saturation=1.05", "-q:v", "2", arq], check=True)
    im = Image.open(arq).convert("RGB")
    return ImageOps.fit(im, (w, h), Image.LANCZOS)


def polaroide(seg, w, h, legenda):
    f = frame_foto(seg, w, h).convert("RGBA")
    m = 22
    p = Image.new("RGBA", (w + 2 * m, h + m + 84), CREME + (255,))
    p.alpha_composite(f, (m, m))
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, p.width - 1, p.height - 1), outline=MAR, width=5)
    d.text((p.width / 2, h + m + 42), legenda, font=E.lilita(40), fill=MAR, anchor="mm")
    sh = Image.new("RGBA", (p.width + 16, p.height + 16), (0, 0, 0, 0))
    sh.paste(MAR + (255,), (14, 14, p.width + 14, p.height + 14))
    sh.alpha_composite(p, (0, 0))
    return sh


def post():
    img = T.fundo().copy().crop((0, 0, 1080, 1350))
    T.guarda_chuvas(img, 3.0)
    E.cola(img, E.titulo("DOMINGO\nDE JOGOS", 135, LAR), 540, 405, -2, 1, 1)
    E.cola(img, E.pilula("NO BECA’S CAFÉ · UM DOMINGO POR MÊS", 36, PET, BR, fonte_titulo=True), 540, 575, 1, 1, 1)
    E.cola(img, polaroide(14.0, 380, 285, "20/11: foi assim!"), 285, 815, -5, 1, 1)
    E.cola(img, painel(0), 790, 800, 3, 0.47, 1)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 96, VERM), 540, 1065, -2, 1, 1)
    E.cola(img, E.pilula(f"{DATA} · {HORA}", 42, AMA, MAR, fonte_titulo=True), 540, 1170, 1, 1, 1)
    E.cola(img, E.pilula(f"{PRECO} · R$ 25 viram consumação no café", 30, BR, MAR), 540, 1240, -1, 1, 1)
    E.cola(img, E.pilula(f"RESERVE: WHATSAPP {TB.WHATS}", 34, PET, BR, fonte_titulo=True), 540, 1305, 0, 1, 1)
    return img.convert("RGB")


def story():
    img = fundo(3.0)
    E.cola(img, TB.parceria(90), W / 2, 470, 0, 1, 1)
    E.cola(img, E.titulo("DOMINGO\nDE JOGOS", 170, LAR), W / 2, 700, -2, 1, 1)
    E.cola(img, E.titulo("SÓ 30 VAGAS!", 110, VERM), W / 2, 920, 2, 1, 1)
    E.cola(img, card(), W / 2, 1290, 0, 0.92, 1)
    E.cola(img, E.pilula("garanta sua vaga aqui:", 40, BR, MAR), W / 2, 1600, 0, 1, 1)
    E.cola(img, seta(), W / 2, 1700, 0, 0.55, 1)
    return img.convert("RGB")


def story_vagas(restam):
    """Story de contagem: 'RESTAM N VAGAS' (N real!), com os vendidos carimbados. Espaço do link y≈1560–1720."""
    img = fundo(3.0)
    vend = VAGAS - restam
    if restam >= VAGAS:
        t1, t2, cor = "VAGAS", "ABERTAS!", LAR
    elif restam == 0:
        t1, t2, cor = "ESGOTADO!", "", VERM
    elif restam == 1:
        t1, t2, cor = "ÚLTIMA", "VAGA!", VERM
    elif restam <= 5:
        t1, t2, cor = f"ÚLTIMAS {restam}", "VAGAS!", VERM
    else:
        t1, t2, cor = f"RESTAM {restam}", "VAGAS!", LAR
    E.cola(img, E.titulo(t1 + ("\n" + t2 if t2 else ""), 150, cor), W / 2, 560, -2, 1, 1)
    E.cola(img, E.pilula(f"DOMINGO DE JOGOS NO BECA’S · {DATA.split(', ')[-1]}", 38, PET, BR, fonte_titulo=True),
           W / 2, 790, 1, 1, 1)
    E.cola(img, painel(vend), W / 2, 1150, 0, 0.92, 1)
    if restam == 0:
        st = Image.new("RGBA", (760, 230), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((6, 6, 754, 224), 26, outline=VERM, width=14)
        sd.text((380, 118), "ESGOTADO", font=E.lilita(150), fill=VERM, anchor="mm")
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
        E.cola(img, st, W / 2, 1150, 0, 1, 0.92)
        E.cola(img, E.pilula("Ficou de fora? Entra na LISTA DE ESPERA:", 38, BR, MAR), W / 2, 1560, 0, 1, 1)
        E.cola(img, E.pilula(f"WHATSAPP {TB.WHATS}", 44, PET, BR, fonte_titulo=True), W / 2, 1650, 0, 1, 1)
        E.cola(img, E.pilula("e já fica de olho no próximo mês!", 34, AMA, MAR), W / 2, 1745, 0, 1, 1)
    else:
        txt = "garanta a sua aqui:" if restam > 1 else "é a última! garanta aqui:"
        E.cola(img, E.pilula(txt, 40, BR, MAR), W / 2, 1530, 0, 1, 1)
        E.cola(img, seta(), W / 2, 1625, 0, 0.5, 1)
        E.cola(img, E.pilula(f"OU NO WHATSAPP {TB.WHATS}", 34, PET, BR, fonte_titulo=True), W / 2, 1830, 0, 1, 1)
    return img.convert("RGB")


def confirmacao(n):
    """Imagem pro WhatsApp de quem PAGOU: o ingressinho dela em destaque."""
    img = fundo(3.0).crop((0, 0, W, 1500))
    E.cola(img, E.titulo("SUA VAGA TÁ\nGARANTIDA!", 120, LAR), W / 2, 500, -2, 1, 1)
    ing = ingressinho(n)
    E.cola(img, ing, W / 2, 820, -4, 3.0, 1)
    E.cola(img, E.pilula(f"{DATA} · {HORA}", 44, AMA, MAR, fonte_titulo=True), W / 2, 1080, 1, 1, 1)
    E.cola(img, E.pilula(ENDERECO, 32, BR, PET, fonte_titulo=True), W / 2, 1170, -1, 1, 1)
    E.cola(img, E.pilula("Seus R$ 25 de consumação te esperam no café", 32, BR, MAR), W / 2, 1255, 0, 1, 1)
    E.cola(img, E.titulo("TE ESPERAMOS!", 84, AMA), W / 2, 1390, 2, 1, 1)
    return img.convert("RGB")


def fotos(so=None):
    os.makedirs(os.path.join(PASTA, "vagas"), exist_ok=True)
    os.makedirs(os.path.join(PASTA, "confirmacao"), exist_ok=True)
    if so is not None:
        arq = os.path.join(PASTA, "vagas", f"restam_{so:02d}.png")
        story_vagas(so).save(arq)
        print("ok", arq)
        return
    post().save(os.path.join(PASTA, "post.png"))
    story().save(os.path.join(PASTA, "story.png"))
    for n in (30, 25, 20, 15, 10, 5, 3, 2, 1, 0):
        story_vagas(n).save(os.path.join(PASTA, "vagas", f"restam_{n:02d}.png"))
    for n in range(1, VAGAS + 1):
        confirmacao(n).save(os.path.join(PASTA, "confirmacao", f"vaga_{n:02d}.png"))
    print("ok", PASTA)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--fotos" in sys.argv:
        fotos()
        return
    if "--vagas" in sys.argv:
        fotos(int(sys.argv[sys.argv.index("--vagas") + 1]))
        return
    K.prepara(TRECHOS)
    if "--frame" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:] if not x.startswith("--")]
        md = "stories" if "--stories" in sys.argv else "reels"
        K.folha([quadro(x, md) for x in ts], os.path.join(OUT, "frames_domingo.jpg"))
        print("ok", DUR)
        return
    for nome, rnd in (("domingo_reels", render_reels), ("domingo_stories", render_stories)):
        com, sem = audio(nome)
        K.entrega(nome, DUR, rnd, com, sem)
    print("ok", DUR)


if __name__ == "__main__":
    main()
