"""Monta e renderiza um episódio de novelinha de WhatsApp.

python3 novela.py <serie> <ep> [--frame T1 T2 ...] [--dur]
  ex.: python3 novela.py sogra 1            -> out/sogra_ep1.mp4
       python3 novela.py sogra 1 --frame 3 20 -> out/frames.jpg
       python3 novela.py sogra 1 --dur        -> só mostra a duração
"""
import importlib
import math
import os
import subprocess
import sys
from dataclasses import dataclass, field
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import marca
import som
import vozes
import zap
from zap import C, W, H

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "out")
FPS = 30
SR = vozes.SR


def ease(p):
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 3


# ------------------------------------------------------------------ estruturas da linha do tempo
@dataclass
class Item:
    tipo: str                 # texto | audio | foto | apagada | chip | sistema
    t: float                  # quando aparece
    quem: str = ""
    texto: str = ""
    hora: str = ""
    saida: bool = False
    rabo: bool = True
    extra: dict = field(default_factory=dict)
    t_apaga: float = 1e9      # vira "mensagem apagada"
    t_lido: float = -1e9      # tracinhos azuis a partir daqui (saída)


@dataclass
class Chat:
    id: str
    titulo: str
    dono: str
    com: str = ""
    grupo: bool = False
    sub: str = ""
    itens: list = field(default_factory=list)
    subs: list = field(default_factory=list)        # (t0, t1, texto, verde)
    rascunhos: list = field(default_factory=list)   # (t0, t1, texto)
    digitando: list = field(default_factory=list)   # (t0, t1, quem)
    horas: list = field(default_factory=list)       # (t, "09:31")


class Ep:
    def __init__(self, serie, n):
        self.mod = importlib.import_module(f"{serie}.roteiro")
        # cada novela pode ter as próprias vozes (VOZES = {personagem: (voz, velocidade, tom)})
        vozes.ELENCO.update(getattr(self.mod, "VOZES", {}))
        self.serie, self.n = serie, n
        self.dados = self.mod.EPISODIOS[n - 1]
        self.p = self.mod.PERSONAGENS
        self.telas = []      # (t0, tipo, arg)
        self.narr = []       # (t0, t1, texto, palavras)
        self.notifs = []     # (t0, t1, titulo, texto)
        self.vozes = []      # (t, audio)
        self.sfx = []        # (t, nome, ganho)
        self.chats = {}
        self.zooms = []      # (t0, t1, imagem): o print ocupa a tela para dar para ler
        self.t = 0.0
        self._monta()

    # -------------------------------------------- helpers
    def cor(self, quem):
        return self.p[quem]["cor"]

    def nome(self, quem):
        return self.p[quem]["nome"]

    def chat(self):
        return self.chats[self.chat_atual]

    def voz(self, quem, texto, t0, filtro=None):
        a, pal = vozes.fala(quem, texto)
        if filtro:
            a = filtro(a)
        self.vozes.append((t0, a))
        return len(a) / SR, pal

    def tela(self, tipo, arg=None):
        self.telas.append((self.t, tipo, arg))

    # -------------------------------------------- roteiro -> linha do tempo
    def _monta(self):
        self.t_fim = None
        for ev in self.dados["eventos"]:
            args, op = list(ev[1:]), {}
            if args and isinstance(args[-1], dict):
                op = args.pop()
            getattr(self, "ev_" + ev[0])(*args, **op)
        self.dur = self.t
        if self.t_fim is None:
            self.t_fim = self.dur + 10

    def ev_gancho(self, titulo, texto, hora, narr):
        self.tela("bloqueio", hora)
        self.sfx.append((0.25, "impacto", 0.7))
        self.notifs.append((0.25, None, titulo, texto))
        self.sfx.append((0.25, "notif", 0.8))
        self.t = 0.9
        self.ev_narr(narr)
        self.notifs[-1] = self.notifs[-1][:1] + (self.t,) + self.notifs[-1][2:]
        self.t += 0.1

    def ev_titulo(self):
        self.tela("titulo")
        self.sfx.append((self.t, "tantan", 0.75))
        ep = self.dados
        txt = f"{self.mod.TITULO}. Parte {ep['parte']}: {ep['nome']}."
        d, _ = self.voz("narrador", txt, self.t + 0.6)
        self.t += max(2.6, 0.6 + d + 0.25)

    def ev_narr(self, texto, dim=True):
        # frases longas viram cartões separados
        partes = [p.strip() for p in texto.replace("... ", "…|").replace(". ", ".|").replace("? ", "?|").split("|") if p.strip()]
        for p in partes:
            d, pal = self.voz("narrador", p, self.t + 0.12)
            self.narr.append((self.t, self.t + 0.12 + d + 0.25, p, [(s + self.t + 0.12, e + self.t + 0.12, w) for s, e, w in pal]))
            self.t += 0.12 + d + 0.25

    def ev_chat(self, cid, hora, chip=None, historico=()):
        cfg = self.mod.CHATS[cid]
        novo = cid not in self.chats
        if novo:
            self.chats[cid] = Chat(cid, cfg["titulo"], cfg["dono"], cfg.get("com", ""), cfg.get("grupo", False),
                                   cfg.get("sub", "online"))
        self.chat_atual = cid
        ch = self.chats[cid]
        ch.horas.append((self.t, hora))
        if novo:
            for h in historico:
                if h[0] == "chip":
                    ch.itens.append(Item("chip", -1e9, texto=h[1]))
                elif h[0] == "foto":
                    _, quem, img, hh = h[:4]
                    if isinstance(img, str):
                        img = os.path.join(AQUI, "assets", "fotos", img)
                    self._add(Item("foto", -1e9, quem, "", hh, quem == ch.dono,
                                   extra=dict(img=img, h_max=h[4] if len(h) > 4 else 560, w=h[5] if len(h) > 5 else 600)))
                else:
                    quem, txt, hh = h
                    self._add(Item("texto", -1e9, quem, txt, hh, quem == ch.dono, t_lido=-1e9))
        if chip:
            ch.itens.append(Item("chip", self.t + 0.3, texto=chip))
        if self.telas:
            self.sfx.append((self.t, "whoosh", 0.35))
        self.tela("chat", cid)
        self.t += 0.6 if len(self.telas) > 1 else 0.4

    def _add(self, it):
        ch = self.chat()
        ant = next((i for i in reversed(ch.itens) if i.tipo not in ("chip",)), None)
        it.rabo = not (ant and ant.quem == it.quem and ant.tipo != "sistema")
        ch.itens.append(it)
        return it

    def _digitando(self, quem, dur):
        ch = self.chat()
        txt = f"{self.nome(quem)} está digitando…" if ch.grupo else "digitando…"
        ch.subs.append((self.t, self.t + dur, txt, True))
        ch.digitando.append((self.t, self.t + dur, quem))

    def ev_msg(self, quem, texto, **op):
        ch = self.chat()
        saida = quem == ch.dono
        hora = op.get("hora") or self._hora()
        if saida:
            dig = min(0.75, 0.22 + 0.008 * len(texto))
            ch.rascunhos.append((self.t, self.t + dig, texto))
            self.sfx.append((self.t, "teclas:%.2f" % dig, 0.6))
            self.t += dig
            self.sfx.append((self.t, "envio", 0.7))
        else:
            dig = op.get("dig", 0.3 if len(texto) < 40 else 0.5)
            if dig:
                self._digitando(quem, dig)
                self.t += dig
            self.sfx.append((self.t, "receb", 0.75))
        it = self._add(Item("texto", self.t, quem, texto, hora, saida, extra=dict(enc=op.get("enc", False))))
        it.t_lido = self.t + 0.6
        if op.get("ler", True):
            d, _ = self.voz(quem, texto, self.t + 0.12)
            self.t += 0.12 + d + op.get("pausa", 0.14)
        else:
            self.t += op.get("pausa", 1.0)
        return it

    def ev_audio(self, quem, texto, **op):
        ch = self.chat()
        saida = quem == ch.dono
        a, pal = vozes.fala(op.get("voz", quem), texto)
        dur = len(a) / SR
        if not saida:
            self.sfx.append((self.t, "receb", 0.75))
        else:
            self.sfx.append((self.t, "envio", 0.7))
        t_play = self.t + 0.4
        it = self._add(Item("audio", self.t, quem, texto, op.get("hora") or self._hora(), saida,
                            extra=dict(dur=dur, t_play=t_play if op.get("tocar", True) else 1e9,
                                       pal=[(s + t_play, e + t_play, w) for s, e, w in pal],
                                       voz=op.get("voz", quem), enc=op.get("enc", False),
                                       transcricao=op.get("transcricao", True))))
        if op.get("tocar", True):
            self.vozes.append((t_play, som.telefone(a) * 0.95))
            self.t = t_play + dur + 0.3
        else:
            self.t += op.get("pausa", 1.2)
        return it

    def ev_foto(self, quem, img, legenda=None, **op):
        ch = self.chat()
        saida = quem == ch.dono
        self.sfx.append((self.t, "envio" if saida else "receb", 0.75))
        if isinstance(img, str):
            img = os.path.join(AQUI, "assets", "fotos", img)
        self._add(Item("foto", self.t, quem, legenda or "", op.get("hora") or self._hora(), saida,
                       extra=dict(img=img, h_max=op.get("h_max", 560), w=op.get("w", 600))))
        if op.get("zoom"):
            self.zooms.append((self.t + 0.45, self.t + op.get("pausa", 1.8) + 0.1, img))
            self.sfx.append((self.t + 0.45, "whoosh", 0.4))
        if legenda:
            d, _ = self.voz(quem, legenda, self.t + 0.45)
            self.t += 0.45 + d + 0.25
        else:
            self.t += op.get("pausa", 1.8)

    def ev_rascunho(self, texto, segura=1.0):
        """O dono do celular digita, hesita e apaga (sem enviar)."""
        ch = self.chat()
        dig = min(0.9, 0.25 + 0.03 * len(texto))
        apaga = 0.5
        ch.rascunhos.append((self.t, self.t + dig, texto))
        ch.rascunhos.append((self.t + dig, self.t + dig + segura, texto + "\x00"))
        ch.rascunhos.append((self.t + dig + segura, self.t + dig + segura + apaga, texto + "\x01"))
        self.sfx.append((self.t, "teclas:%.2f" % dig, 0.6))
        self.sfx.append((self.t + dig + segura, "teclas:%.2f" % apaga, 0.4))
        self.t += dig + segura + apaga + 0.3

    def ev_digitando(self, quem, dur):
        self._digitando(quem, dur)
        self.t += dur + 0.15

    def ev_apagar(self, quem):
        ch = self.chat()
        it = next(i for i in reversed(ch.itens) if i.quem == quem and i.tipo != "chip")
        it.t_apaga = self.t
        self.sfx.append((self.t, "apaga", 0.8))
        self.t += 0.8

    def ev_status(self, texto):
        ch = self.chat()
        ch.subs.append((self.t, 1e9, texto, False))

    def ev_sistema(self, texto):
        ch = self.chat()
        ch.itens.append(Item("sistema", self.t, texto=texto))
        self.sfx.append((self.t, "receb", 0.5))
        self.t += 1.4

    def ev_pausa(self, s):
        self.t += s

    def ev_hora(self, h):
        self.chat().horas.append((self.t, h))

    def ev_fim(self, linha1, linha2, pergunta):
        self.tela("fim", (linha1, linha2, pergunta))
        self.sfx.append((self.t, "tantan", 0.9))
        t0 = self.t
        self.t += 1.3
        d, pal = self.voz("narrador", pergunta, self.t)
        self.fim_pal = [(s + self.t, e + self.t, w) for s, e, w in pal]
        self.t += d + 1.8
        self.t_fim = t0

    def _hora(self):
        ch = self.chat()
        h = ch.horas[-1][1] if ch.horas else "12:00"
        return h

    # -------------------------------------------- áudio
    def audio(self):
        n = int((self.dur + 0.5) * SR)
        voz = np.zeros(n)
        for t0, a in self.vozes:
            i = int(t0 * SR)
            voz[i:i + len(a)] += a[:max(0, n - i)]
        fx = np.zeros(n)
        for t0, nome, g in self.sfx:
            if nome.startswith("teclas:"):
                s = som.teclas(float(nome.split(":")[1]))
            else:
                s = som.EFEITOS[nome]()
            i = int(t0 * SR)
            fx[i:i + len(s)] += g * s[:max(0, n - i)]
        mus = som.trilha(self.dur + 0.5, seed=self.n)
        mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
        # ducking pela envoltória da voz
        env = np.abs(voz)
        k = int(0.25 * SR)
        env = np.convolve(env, np.ones(k) / k, mode="same")
        duck = 1.0 - 0.62 * np.clip(env / 0.02, 0, 1)
        # a trilha some na tela final (fica só o tan-tan-tan) e entra suave no começo
        t = np.arange(n) / SR
        fade = np.clip(t / 1.5, 0, 1) * np.clip((self.t_fim - t) / 0.8 + 1, 0, 1)
        mix = voz * 1.0 + fx * 0.5 + mus * 0.32 * duck * fade
        return mix.astype(np.float32)

    # -------------------------------------------- vídeo
    def quadro(self, t):
        tela = None
        anterior = None
        for i, tl in enumerate(self.telas):
            if tl[0] <= t:
                anterior, tela = tela, tl
        im = self._tela(tela, t)
        # transição: a tela nova entra deslizando da direita
        dt = t - tela[0]
        if anterior is not None and dt < 0.28 and tela[1] in ("chat", "fim", "titulo"):
            velho = self._tela(anterior, t)
            p = ease(dt / 0.28)
            base = Image.new("RGB", (W, H))
            base.paste(velho, (round(-W * 0.3 * p), 0))
            base.paste(im, (round(W * (1 - p)), 0))
            im = base
        im = self._overlays(im, t, tela)
        return im

    def _tela(self, tela, t):
        tipo, arg = tela[1], tela[2]
        if tipo == "bloqueio":
            return self._bloqueio(arg, t).convert("RGB")
        if tipo == "titulo":
            return self._titulo(t - tela[0])
        if tipo == "fim":
            return self._fim(arg, t - tela[0], t)
        return self._chat(self.chats[arg], t)

    # ---- tela de bloqueio (gancho)
    def _bloqueio(self, hora, t):
        if not hasattr(self, "_bloq_bg"):
            g = np.linspace(0, 1, H)[:, None]
            a = np.array([40, 18, 60])[None, None, :] * (1 - g[..., None]) + np.array([8, 6, 20])[None, None, :] * g[..., None]
            self._bloq_bg = Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8))
        im = self._bloq_bg.copy().convert("RGBA")
        d = ImageDraw.Draw(im)
        zap.barra_status(im, "", escuro=True)
        d.rectangle((0, zap.STATUS_Y, W, zap.HEADER_Y), fill=(0, 0, 0, 0))
        d.text((W / 2, 330), self.dados.get("dia", "sábado, 14 de outubro"), font=zap.inter(40, 500), fill=(230, 230, 240), anchor="mm")
        d.text((W / 2, 470), hora, font=zap.inter(230, 300), fill=(255, 255, 255), anchor="mm")
        zap.banda_marca(im, self.mod.TITULO, f"Parte {self.dados['parte']}/5")
        return im

    def _notif(self, im, titulo, texto, p):
        w, x0 = 960, 60
        f1, f2 = zap.inter(38, 650), zap.inter(42, 430)
        linhas = zap.quebra(texto, f2, w - 150)
        h = 110 + len(linhas) * 56 + 20
        card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=(245, 245, 247, 240))
        d.rounded_rectangle((28, 30, 108, 110), 20, fill=(37, 211, 102))
        d.ellipse((46, 48, 90, 92), outline=(255, 255, 255), width=5)
        d.polygon([(48, 96), (52, 82), (62, 90)], fill=(255, 255, 255))
        d.text((130, 62), "WHATSAPP", font=zap.inter(28, 600), fill=(120, 120, 125), anchor="ls")
        d.text((w - 34, 62), "agora", font=zap.inter(28, 450), fill=(120, 120, 125), anchor="rs")
        zap.desenha_linha(card, 130, 108, zap.tokens(titulo), f1, (20, 20, 20))
        for i, ln in enumerate(linhas):
            zap.desenha_linha(card, 130, 164 + i * 56, ln, f2, (40, 40, 40))
        y = round(640 - (1 - ease(p)) * 120)
        a = min(1, p * 2)
        if a < 1:
            card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(card, (x0, y))

    # ---- cartão de título
    def _titulo(self, dt):
        im = Image.new("RGBA", (W, H), C["amarelo"])
        d = ImageDraw.Draw(im)
        # listras diagonais suaves
        for k in range(-H, W + H, 120):
            d.line([(k, 0), (k + H, H)], fill=(255, 205, 0), width=40)
        p = ease(dt / 0.45)
        t1 = zap.tarja(marca.NOME, 54, cor_txt=C["amarelo"], ang=4)
        im.alpha_composite(t1, (round((W - t1.width) / 2), 360))
        t2 = zap.tarja(self.mod.TITULO.upper(), 104, maxw=880, ang=-3)
        x = round((W - t2.width) / 2 - (1 - p) * W)
        im.alpha_composite(t2, (x, 620))
        p2 = ease((dt - 0.35) / 0.4)
        f = zap.inter(78, 900)
        d.text((W / 2 + (1 - p2) * W, 1010), f"PARTE {self.dados['parte']}", font=f, fill=C["preto"], anchor="mm")
        f2 = zap.inter(56, 700)
        d.text((W / 2 + (1 - p2) * W * 1.2, 1110), self.dados["nome"], font=f2, fill=C["preto"], anchor="mm")
        return im.convert("RGB")

    # ---- tela final
    def _fim(self, arg, dt, t):
        l1, l2, perg = arg
        im = Image.new("RGBA", (W, H), C["preto"])
        d = ImageDraw.Draw(im)
        p = ease(dt / 0.5)
        f = zap.inter(150 if len(l1) < 12 else 104, 900)
        d.text((W / 2, 400 - (1 - p) * 200), l1, font=f, fill=C["amarelo"], anchor="mm")
        d.text((W / 2, 540), l2, font=zap.inter(50, 700), fill=(240, 240, 240), anchor="mm")
        if dt > 1.3:
            k = None
            for i, (s, e, w) in enumerate(getattr(self, "fim_pal", [])):
                if s <= t:
                    k = i
            tj = zap.tarja(perg, 58, cor_fundo=C["amarelo"], cor_txt=C["preto"], maxw=860, ang=-2)
            pp = ease((dt - 1.3) / 0.3)
            tj = tj.resize((max(1, round(tj.width * (0.7 + 0.3 * pp))), max(1, round(tj.height * (0.7 + 0.3 * pp)))))
            im.alpha_composite(tj, (round((W - tj.width) / 2), round(860 - tj.height / 2)))
        logo = self._logo(240)
        im.alpha_composite(logo, ((W - 240) // 2, 1130))
        d.text((W / 2, 1430), marca.NOME_FIM, font=zap.inter(60, 800), fill=(255, 255, 255), anchor="mm")
        chamada = getattr(self.mod, "CHAMADA", "Segue e compartilha!")
        fc = zap.inter(42, 600)
        zap.desenha_linha(im, (W - zap.larg_linha(zap.tokens(chamada), fc)) / 2, 1520, zap.tokens(chamada), fc, C["amarelo"])
        return im.convert("RGB")

    def _zoom_img(self, img):
        if not hasattr(self, "_zc"):
            self._zc = {}
        if img not in self._zc:
            ft = img() if callable(img) else Image.open(img).convert("RGB")
            esc = min(980 / ft.width, 1250 / ft.height)
            ft = ft.resize((round(ft.width * esc), round(ft.height * esc)), Image.LANCZOS)
            m = Image.new("L", ft.size, 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, ft.width - 1, ft.height - 1), 24, fill=255)
            ft = ft.convert("RGBA")
            ft.putalpha(m)
            self._zc[img] = ft
        return self._zc[img]

    def _logo(self, tam):
        if not hasattr(self, "_logo_c"):
            import logos
            self._logo_c = getattr(logos, marca.LOGO)()
        im = self._logo_c.resize((tam, tam), Image.LANCZOS).convert("RGBA")
        m = Image.new("L", (tam * 3, tam * 3), 0)
        ImageDraw.Draw(m).ellipse((0, 0, tam * 3, tam * 3), fill=255)
        im.putalpha(m.resize((tam, tam), Image.LANCZOS))
        return im

    # ---- conversa
    def _render_item(self, it, ch, t):
        nome = cor_nome = None
        if ch.grupo and not it.saida and it.rabo and it.tipo in ("texto", "audio", "foto", "apagada"):
            nome = self.mod.CHATS[ch.id].get("nomes", {}).get(it.quem) or self.p[it.quem].get("nome_grupo", self.nome(it.quem))
            cor_nome = self.p[it.quem].get("cor_nome", self.cor(it.quem))
        if it.tipo == "chip":
            return zap.chip_data(it.texto), 0
        if it.tipo == "sistema":
            return zap.chip_sistema(it.texto), 0
        if t >= it.t_apaga:
            return zap.balao_apagada(it.hora, it.saida, it.rabo, nome, cor_nome)
        if it.tipo == "texto":
            return zap.balao_texto(it.texto, it.hora, it.saida, it.rabo, nome, cor_nome,
                                   lido=t >= it.t_lido, encaminhada=it.extra.get("enc", False))
        if it.tipo == "foto":
            return zap.balao_foto(it.extra["img"], it.hora, it.saida, it.rabo, it.texto or None, nome, cor_nome,
                                  h_max=it.extra["h_max"], w=it.extra["w"])
        if it.tipo == "audio":
            e = it.extra
            prog = min(1, max(0, (t - e["t_play"]) / e["dur"]))
            tocando = 0 < prog < 1
            tr = None
            if e["transcricao"] and t >= e["t_play"]:
                # revela o texto original (com pontuação) na proporção das palavras já faladas
                orig = it.texto.split()
                ditas = sum(1 for s, _, w in e["pal"] if s <= t)
                tr = " ".join(orig[:round(len(orig) * ditas / max(1, len(e["pal"])))])
            return zap.balao_audio(it.hora, it.saida, it.rabo, e["dur"], prog, self.nome(e["voz"]), self.cor(e["voz"]),
                                   transcricao=tr, nome=nome, cor_nome=cor_nome, encaminhada=e["enc"], tocando=tocando)

    def _chat(self, ch, t):
        im = zap.papel_parede().copy().convert("RGBA")
        # itens visíveis e altura total (o item novo "cresce" para a rolagem ficar suave)
        vis = []
        for it in ch.itens:
            if it.t <= t:
                b, pad = self._render_item(it, ch, t)
                vis.append((it, b, pad))
        dig = [dg for dg in ch.digitando if dg[0] <= t < dg[1]]
        if dig:
            b, pad = zap.balao_digitando(t)
            vis.append((Item("dig", dig[0][0], dig[0][2]), b, pad))
        alturas = []
        for it, b, pad in vis:
            h = b.height - 2 * pad if pad else b.height
            esp = 10 if (it.tipo in ("chip", "sistema")) else (18 if it.rabo else 4)
            p = ease((t - it.t) / 0.22)
            alturas.append((h + esp) * p)
        total = sum(alturas) + 24
        area = zap.CHAT_Y1 - zap.CHAT_Y0 - 22
        desloc = max(0, total - area)
        y = zap.CHAT_Y0 + 14 - desloc
        for (it, b, pad), hh in zip(vis, alturas):
            esp = 10 if (it.tipo in ("chip", "sistema")) else (18 if it.rabo else 4)
            y += esp * min(1, hh / max(1, esp + 1))
            p = ease((t - it.t) / 0.22)
            if it.tipo in ("chip", "sistema"):
                x = (W - b.width) // 2 - 50
            elif it.saida:
                x = zap.DIR - (b.width - pad)
            else:
                x = zap.ESQ - pad
            if p < 1:
                esc = 0.85 + 0.15 * p
                bw, bh = max(1, round(b.width * esc)), max(1, round(b.height * esc))
                b2 = b.resize((bw, bh), Image.BILINEAR)
                b2.putalpha(b2.getchannel("A").point(lambda v: int(v * p)))
                ox = x + (b.width - bw if it.saida else 0)
                if b2.height + y - pad > zap.CHAT_Y0 - 200:
                    im.alpha_composite(b2, (round(ox), round(y - pad)))
            else:
                if y - pad + b.height > zap.CHAT_Y0 - 50 and y - pad < zap.CHAT_Y1:
                    im.alpha_composite(b, (round(x), round(y - pad)))
            y += hh - esp * min(1, hh / max(1, esp + 1))
        # moldura do app por cima (esconde o que rolou para trás do cabeçalho)
        hora = next((h for t0, h in reversed(ch.horas) if t0 <= t), ch.horas[0][1])
        sub, verde = ch.sub, False
        for t0, t1, s, v in ch.subs:
            if t0 <= t < t1:
                sub, verde = s, v
        zap.barra_status(im, hora)
        cor_av = (90, 110, 120) if ch.grupo else self.cor(ch.com)
        zap.cabecalho(im, ch.titulo, sub, cor_av, ch.grupo, verde)
        rasc = ""
        for t0, t1, s in ch.rascunhos:
            if t0 <= t < t1:
                if s.endswith("\x00"):      # parado, cursor piscando
                    rasc = s[:-1]
                elif s.endswith("\x01"):    # apagando
                    s = s[:-1]
                    rasc = s[:max(0, int(len(s) * (1 - (t - t0) / (t1 - t0))))]
                else:
                    rasc = s[:max(1, int(len(s) * (t - t0) / (t1 - t0 - 0.12)))]
        zap.barra_entrada(im, rasc, cursor=bool(rasc) and int(t * 3) % 2 == 0)
        zap.teclado(im)
        fim = self.dados.get("fim_texto", "Continua na Parte %d" % (self.dados["parte"] + 1))
        zap.banda_parte(im, fim if t >= self.dur - 2.4 else f"Parte {self.dados['parte']}")
        return im.convert("RGB")

    # ---- camadas por cima: narrador e notificação
    def _overlays(self, im, t, tela):
        im = im.convert("RGBA")
        for t0, t1, titulo, texto in self.notifs:
            if tela[1] == "bloqueio" and t0 <= t < (t1 or 1e9) + 0.3:
                p = (t - t0) / 0.35 if t < (t1 or 1e9) else 1 - (t - t1) / 0.3
                self._notif(im, titulo, texto, max(0, min(1, p)))
        for t0, t1, img in self.zooms:
            if t0 <= t < t1:
                a = min(1, (t - t0) / 0.2, (t1 - t) / 0.2)
                im.alpha_composite(Image.new("RGBA", (W, H - zap.BANDA), (0, 0, 0, int(200 * a))), (0, zap.BANDA))
                ft = self._zoom_img(img)
                esc = (0.9 + 0.1 * ease((t - t0) / 0.25)) * min(1, (t1 - t) / 0.2 * 0.1 + 0.9)
                fw, fh = max(1, round(ft.width * esc)), max(1, round(ft.height * esc))
                f2 = ft.resize((fw, fh), Image.BILINEAR).convert("RGBA")
                if a < 1:
                    f2.putalpha(int(255 * a))
                im.alpha_composite(f2, ((W - fw) // 2, round(860 - fh / 2)))
        for t0, t1, texto, pal in self.narr:
            if t0 - 0.1 <= t < t1:
                a = min(1, (t - t0 + 0.1) / 0.2, (t1 - t) / 0.15)
                if tela[1] != "bloqueio":
                    veu = Image.new("RGBA", (W, H - zap.BANDA), (0, 0, 0, int(175 * a)))
                    im.alpha_composite(veu, (0, zap.BANDA))
                k = None
                for i, (s, e, w) in enumerate(pal):
                    if s <= t:
                        k = i
                tj = zap.tarja(texto, 62, maxw=880, destaque=k, ang=-2)
                if a < 1:
                    tj.putalpha(tj.getchannel("A").point(lambda v: int(v * a)))
                y = 1180 if tela[1] == "bloqueio" else 860
                im.alpha_composite(tj, (round((W - tj.width) / 2), round(y - tj.height / 2)))
        return im.convert("RGB")


# ------------------------------------------------------------------ render
_EP = None


def _init(serie, n):
    global _EP
    _EP = Ep(serie, n)


def _quadro(i):
    return _EP.quadro(i / FPS).tobytes()


def render(serie, n):
    ep = Ep(serie, n)
    os.makedirs(OUT, exist_ok=True)
    nome = f"{serie}_ep{n}"
    wav = os.path.join(OUT, nome + ".f32")
    a = ep.audio()
    import pyloudnorm
    med = pyloudnorm.Meter(SR)
    ganho = 10 ** ((-14.5 - med.integrated_loudness(a.astype(np.float64))) / 20)
    (a * ganho).astype(np.float32).tofile(wav)
    nq = int(ep.dur * FPS)
    mp4 = os.path.join(OUT, nome + ".mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", wav,
           "-af", "alimiter=limit=0.89:attack=3:release=60,aresample=48000", "-ac", "2",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", mp4]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(4, initializer=_init, initargs=(serie, n)) as pool:
        for k, fr in enumerate(pool.imap(_quadro, range(nq), chunksize=8)):
            pr.stdin.write(fr)
            if k % 300 == 0:
                print(f"{nome}: {k}/{nq}", flush=True)
    pr.stdin.close()
    pr.wait()
    os.remove(wav)
    print("ok", mp4, f"{ep.dur:.1f}s")


def frames(serie, n, ts):
    ep = Ep(serie, n)
    ims = [ep.quadro(t) for t in ts]
    esc = 0.36
    w, h = round(W * esc), round(H * esc)
    folha = Image.new("RGB", (w * len(ims) + 10 * (len(ims) - 1), h), "white")
    for i, q in enumerate(ims):
        folha.paste(q.resize((w, h), Image.LANCZOS), (i * (w + 10), 0))
    os.makedirs(OUT, exist_ok=True)
    folha.save(os.path.join(OUT, "frames.jpg"), quality=88)
    print(f"dur {ep.dur:.1f}s")


if __name__ == "__main__":
    serie, n = sys.argv[1], int(sys.argv[2])
    if "--frame" in sys.argv:
        frames(serie, n, [float(x) for x in sys.argv[sys.argv.index("--frame") + 1:]])
    elif "--dur" in sys.argv:
        ep = Ep(serie, n)
        print(f"{serie} ep{n}: {ep.dur:.1f}s")
        for t0, _, txt, _ in ep.narr:
            pass
    else:
        render(serie, n)
