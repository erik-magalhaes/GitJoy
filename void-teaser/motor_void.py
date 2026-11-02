"""Motor visual do teaser VOID: galpão em raycast (numpy), névoa, luzes que piscam, silhuetas e acabamento.

Tudo procedural (sem rostos, sem texto). Imagens em float32 RGB 0..1 (linear "de olho"), 1080x1920.
"""
import functools
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
FPS = 30


# ------------------------------------------------------------------ utilidades
def ruido(w, h, escala, seed):
    """Ruído suave (valor) em [0,1] com detalhe em 3 oitavas."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(3):
        s = max(2, int(escala / (2 ** o)))
        g = rng.random((h // s + 2, w // s + 2)).astype(np.float32)
        g = cv2.resize(g, (w + 2 * s, h + 2 * s), interpolation=cv2.INTER_CUBIC)[s:s + h, s:s + w]
        out += g * amp
        tot += amp
        amp *= 0.5
    out /= tot
    return np.clip((out - out.min()) / (out.max() - out.min() + 1e-6), 0, 1)


@functools.lru_cache(maxsize=4)
def textura_nevoa(seed=1):
    return ruido(W + 600, H + 600, 220, seed)


def nevoa(t, seed=1, vel=(18, -6)):
    """Camada de névoa que desliza devagar (W x H)."""
    T = textura_nevoa(seed)
    x = int(300 + vel[0] * t) % 600
    y = int(300 + vel[1] * t) % 600
    a = T[y:y + H, x:x + W]
    T2 = textura_nevoa(seed + 7)
    x2 = int(300 - vel[0] * 0.6 * t) % 600
    y2 = int(300 + vel[1] * 0.4 * t) % 600
    b = T2[y2:y2 + H, x2:x2 + W]
    return np.clip(0.55 * a + 0.45 * b, 0, 1)


def camera(img, zoom=1.0, cx=0.5, cy=0.5, rot=0.0, sx=0.0, sy=0.0):
    """Recorta/zoom/gira uma imagem (qualquer tamanho) para W x H. cx,cy = centro em fração da imagem."""
    h, w = img.shape[:2]
    base = max(W / w, H / h) * zoom
    M = cv2.getRotationMatrix2D((cx * w, cy * h), rot, base)
    M[0, 2] += W / 2 - cx * w + sx
    M[1, 2] += H / 2 - cy * h + sy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def bloom(img, limiar=0.6, raio=41, forca=0.6):
    br = np.clip(img - limiar, 0, None)
    b = cv2.GaussianBlur(br, (0, 0), raio / 3)
    b2 = cv2.GaussianBlur(br, (0, 0), raio)
    return img + forca * (b + 0.6 * b2)


@functools.lru_cache(maxsize=2)
def _vinheta(forca):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.6)) ** 2)
    return np.clip(1 - forca * d ** 2.2, 0, 1)[..., None].astype(np.float32)


def acabamento(img, vinheta=0.55, tom=True):
    """Gradação 'thriller': pretos frios, médios aço, altas levemente quentes; vinheta suave; tonemap."""
    img = np.maximum(img, 0)
    img = img / (1 + 0.35 * img)  # tonemap suave
    if tom:
        lum = img.mean(axis=2, keepdims=True)
        sombra = np.array([0.92, 1.0, 1.10], np.float32)
        alta = np.array([1.05, 1.0, 0.95], np.float32)
        m = np.clip(lum * 1.6, 0, 1)
        img = img * (sombra * (1 - m) + alta * m)
        # tira saturação geral
        img = lum + (img - lum) * 0.82
    img = img * _vinheta(vinheta)
    return np.clip(img, 0, 1)


def para_u8(img):
    # pontilhado leve para não fazer banding no degradê escuro
    rng = np.random.default_rng()
    d = rng.random((H, W, 1), dtype=np.float32) / 255.0
    return np.clip(img * 255 + d * 255 - 0.5, 0, 255).astype(np.uint8)


def gradua_foto(rgb, des=0.55, gamma=1.25, frio=True):
    img = rgb.astype(np.float32) / 255.0
    lum = img.mean(axis=2, keepdims=True)
    img = lum + (img - lum) * (1 - des)
    img = img ** gamma
    if frio:
        img = img * np.array([0.93, 0.99, 1.08], np.float32)
    return img


# ------------------------------------------------------------------ galpão (raycast)
class Galpao:
    """Caixa de galpão vista de dentro. Superfícies: piso, teto, paredes, pilares; lâmpadas em grupos."""

    def __init__(self, cam=(0.0, 1.6, 0.0), f=1050, horizonte=0.5, largura=11.0, altura=9.0, fundo=46.0,
                 pilares=None, lampadas=None, porta_fundo=True, seed=3, olhar_y=0.0, piso_brilho=1.0,
                 cor_luz=(1.0, 0.9, 0.75), haze=(0.07, 0.08, 0.095)):
        self.cam = np.array(cam, np.float32)
        self.f, self.hz = f, horizonte * H
        self.L, self.A, self.F = largura, altura, fundo
        self.pilares = pilares if pilares is not None else [(sx * 7.0, z) for z in range(8, 44, 8) for sx in (-1, 1)]
        self.lampadas = lampadas if lampadas is not None else [
            (sx * 4.5, 6.8, z, (k + (sx > 0)) % 2) for k, z in enumerate(range(7, 44, 7)) for sx in (-1, 1)]
        self.porta = porta_fundo
        self.seed = seed
        self.cor_luz = np.array(cor_luz, np.float32)
        self.haze = np.array(haze, np.float32)
        self.piso_brilho = piso_brilho
        self.olhar_y = olhar_y
        self._render()

    def proj(self, X, Y, Z):
        c = self.cam
        z = Z - c[2]
        return (W / 2 + self.f * (X - c[0]) / z, self.hz - self.f * (Y - c[1]) / z + self.olhar_y * 0)

    def _render(self):
        c = self.cam
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (x - W / 2) / self.f
        dy = -(y - self.hz) / self.f
        dz = np.ones_like(dx)
        big = np.float32(1e9)
        t = np.full(dx.shape, big, np.float32)
        sup = np.zeros(dx.shape, np.int8)  # 0 fundo 1 piso 2 teto 3 parede dir 4 parede esq 5 pilar
        with np.errstate(divide="ignore", invalid="ignore"):
            cand = [
                (np.where(dy < 0, (0 - c[1]) / dy, big), 1),
                (np.where(dy > 0, (self.A - c[1]) / dy, big), 2),
                (np.where(dx > 0, (self.L - c[0]) / dx, big), 3),
                (np.where(dx < 0, (-self.L - c[0]) / dx, big), 4),
                (np.full_like(dx, self.F - c[2]), 0),
            ]
        for tt, k in cand:
            m = (tt > 0) & (tt < t)
            t = np.where(m, tt, t)
            sup = np.where(m, k, sup)
        # pilares: caixas 0,6 x 0,6 (face da frente e laterais)
        pil_id = np.full(dx.shape, -1, np.int16)
        for i, (px, pz) in enumerate(self.pilares):
            for (plano, eixo, lim) in (("z", pz - 0.3, (px - 0.3, px + 0.3)),
                                       ("x", px - 0.3 if px > c[0] else px + 0.3, (pz - 0.3, pz + 0.3))):
                with np.errstate(divide="ignore", invalid="ignore"):
                    if plano == "z":
                        tt = (eixo - c[2]) / dz
                        hx = c[0] + dx * tt
                        ok = (hx > lim[0]) & (hx < lim[1])
                    else:
                        tt = (eixo - c[0]) / dx
                        hz = c[2] + dz * tt
                        ok = (hz > lim[0]) & (hz < lim[1])
                    hy = c[1] + dy * tt
                    ok &= (tt > 0) & (hy > 0) & (hy < self.A) & (tt < t)
                t = np.where(ok, tt, t)
                sup = np.where(ok, 5, sup)
                pil_id = np.where(ok, i, pil_id)
        X = c[0] + dx * t
        Y = c[1] + dy * t
        Z = c[2] + dz * t
        self.t, self.sup, self.X, self.Y, self.Z = t, sup, X, Y, Z

        # ---- albedo e textura
        rng = np.random.default_rng(self.seed)
        tex = ruido(W, H, 60, self.seed)
        alb = np.full(dx.shape, 0.12, np.float32)
        piso = sup == 1
        conc = ruido(W, H, 18, self.seed + 1)
        alb = np.where(piso, 0.10 + 0.035 * conc + 0.015 * tex, alb)
        # paredes corrugadas
        cor_d = 0.5 + 0.5 * np.sin(Z * 2 * np.pi / 0.35)
        cor_b = 0.5 + 0.5 * np.sin(X * 2 * np.pi / 0.35)
        alb = np.where((sup == 3) | (sup == 4), 0.07 + 0.05 * cor_d + 0.03 * tex, alb)
        alb = np.where(sup == 0, 0.06 + 0.04 * cor_b + 0.03 * tex, alb)
        # janelas altas no fundo (luz fria de fora)
        jan = (sup == 0) & (Y > 6.2) & (Y < 7.6) & (np.abs((X % 3.0) - 1.5) < 1.0)
        # portão no fundo
        if self.porta:
            port = (sup == 0) & (np.abs(X) < 3.2) & (Y < 5.0)
            alb = np.where(port, 0.05 + 0.03 * (0.5 + 0.5 * np.sin(Y * 2 * np.pi / 0.25)), alb)
        # teto: treliças a cada 8 m + vigas longitudinais
        teto = sup == 2
        tre = (np.abs(((Z + 4) % 8) - 4) < 0.25) | (np.abs(((X + 3.5) % 7) - 3.5) < 0.12)
        alb = np.where(teto, np.where(tre, 0.10, 0.035), alb)
        alb = np.where(sup == 5, 0.06 + 0.03 * tex, alb)
        self.alb = alb

        # ---- luz ambiente (névoa de profundidade)
        neb = 1 - np.exp(-t / 38.0)
        amb = alb[..., None] * np.array([0.25, 0.28, 0.33], np.float32) * (1 - neb[..., None])
        amb += neb[..., None] * self.haze
        amb = np.where(jan[..., None], np.array([0.20, 0.26, 0.34], np.float32) * (1 - 0.5 * neb[..., None]), amb)
        self.amb = amb.astype(np.float32)

        # ---- contribuições das lâmpadas por grupo
        ng = 1 + max((g for *_, g in self.lampadas), default=0)
        self.grupos = [np.zeros((H, W, 3), np.float32) for _ in range(ng)]
        hor2 = dx * dx + dz * dz
        for (lx, ly, lz, g) in self.lampadas:
            if lz - c[2] < 0.6:
                continue
            # luz nas superfícies
            vx, vy, vz = lx - X, ly - Y, lz - Z
            d2 = vx * vx + vy * vy + vz * vz
            cosn = np.where(piso, vy / np.sqrt(d2), 0.35 + 0.0 * vy)
            cosn = np.where(teto, 0.05, cosn)
            cone = np.clip(vy / np.sqrt(d2), 0, 1) ** 2.5  # luminária aponta para baixo
            ilum = 9.0 * cone * np.clip(cosn, 0, 1) / (1 + d2)
            ilum *= (alb * (1.6 if True else 1))
            # brilho molhado do piso (reflexo alongado da lâmpada)
            sx, sy = self.proj(lx, ly, lz)
            sxr, syr = self.proj(lx, -ly, lz)
            refl = np.exp(-((x - sxr) / (6 + 1600 / (lz - c[2]))) ** 2 - ((y - syr) / (60 + 4000 / (lz - c[2]))) ** 2)
            refl = np.where(piso, refl * 0.22 * self.piso_brilho * (0.8 + 0.4 * conc), 0)
            # volume (cone de luz na névoa)
            tst = ((lx - c[0]) * dx + (lz - c[2]) * dz) / hor2
            hx = c[0] + dx * tst - lx
            hz_ = c[2] + dz * tst - lz
            dist_h = np.sqrt(hx * hx + hz_ * hz_)
            yy = c[1] + dy * tst
            abaixo = np.clip(ly - yy, 0, None)
            raio = 0.12 + abaixo * 0.55
            vol = np.exp(-(dist_h / raio) ** 2) * np.exp(-abaixo / 7.0) * (abaixo > 0) * (tst > 0) * (tst < t)
            vol = vol * 0.9 / (0.6 + raio) * np.exp(-tst / 60.0)
            # a própria lâmpada (ponto brilhante + halo)
            r_l = 420 / (lz - c[2])
            bulbo = np.exp(-(((x - sx) ** 2 + ((y - sy) * 1.6) ** 2) / (r_l * r_l)))
            halo = np.exp(-(((x - sx) ** 2 + (y - sy) ** 2) / (r_l * r_l * 30)))
            luz = (ilum + refl)[..., None] * self.cor_luz + (vol * 0.38)[..., None] * self.cor_luz * np.array(
                [1, 0.98, 0.95]) + (bulbo * 2.2 + halo * 0.08)[..., None] * self.cor_luz
            self.grupos[g] += luz.astype(np.float32)
            # luminária (cúpula escura acima da lâmpada)
        for k in range(len(self.grupos)):
            self.grupos[k] = cv2.GaussianBlur(self.grupos[k], (0, 0), 1.2)

    def quadro(self, niveis):
        img = self.amb.copy()
        for g, n in zip(self.grupos, niveis):
            if n > 0:
                img += g * n
        return img


# ------------------------------------------------------------------ silhuetas
def _cap(d, a, b, r, fill=255):
    (x1, y1), (x2, y2) = a, b
    d.line([a, b], fill=fill, width=int(2 * r))
    d.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=fill)
    d.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=fill)


def figura(tipo, h, pose=0.0, S=3):
    """Máscara (float 0..1) de uma pessoa de COSTAS (ou de frente, preta), altura h px.
    tipo: 'atirador', 'hacker' (sentado), 'mulher', 'lider', 'lider_frente'. pose: fase de animação.
    Devolve (mask, (ax, ay)) com âncora = pés no centro."""
    hh = int(h * S)
    ww = int(hh * 0.7)
    im = Image.new("L", (ww, hh + 20), 0)
    d = ImageDraw.Draw(im)
    cx = ww / 2
    u = hh  # 1 unidade = altura
    if tipo == "mulher":
        ombro, cint, quad = 0.105, 0.065, 0.088
    elif tipo in ("lider", "lider_frente"):
        ombro, cint, quad = 0.150, 0.118, 0.115
    else:
        ombro, cint, quad = 0.128, 0.098, 0.095
    topo = 0.0
    cab_h, cab_w = 0.125, 0.092
    if tipo in ("lider", "lider_frente"):
        cab_w = 0.098
    # cabeça
    d.ellipse([cx - cab_w / 2 * u, topo * u, cx + cab_w / 2 * u, (topo + cab_h) * u], fill=255)
    # pescoço
    d.rectangle([cx - 0.026 * u, 0.10 * u, cx + 0.026 * u, 0.16 * u], fill=255)
    if tipo == "mulher":
        # cabelo preso: rabo de cavalo descendo nas costas
        d.ellipse([cx - 0.05 * u, 0.0 * u, cx + 0.05 * u, 0.135 * u], fill=255)
        _cap(d, (cx + 0.004 * u, 0.10 * u), (cx + 0.012 * u, 0.29 * u), 0.020 * u)
    y_ombro = 0.175
    # tronco (trapézio ombro -> cintura -> quadril)
    if tipo in ("lider", "lider_frente"):
        # sobretudo longo
        pts = [(cx - ombro * u, y_ombro * u), (cx + ombro * u, y_ombro * u),
               (cx + 0.135 * u, 0.45 * u), (cx + 0.15 * u, 0.80 * u), (cx - 0.15 * u, 0.80 * u),
               (cx - 0.135 * u, 0.45 * u)]
        d.polygon(pts, fill=255)
        d.ellipse([cx - ombro * u - 0.03 * u, (y_ombro - 0.02) * u, cx - ombro * u + 0.06 * u, (y_ombro + 0.06) * u], fill=255)
        d.ellipse([cx + ombro * u - 0.06 * u, (y_ombro - 0.02) * u, cx + ombro * u + 0.03 * u, (y_ombro + 0.06) * u], fill=255)
        # gola levantada
        d.polygon([(cx - 0.07 * u, 0.13 * u), (cx + 0.07 * u, 0.13 * u), (cx + 0.09 * u, 0.19 * u), (cx - 0.09 * u, 0.19 * u)], fill=255)
    else:
        pts = [(cx - ombro * u, y_ombro * u), (cx + ombro * u, y_ombro * u),
               (cx + cint * u, 0.40 * u), (cx + quad * u, 0.52 * u), (cx - quad * u, 0.52 * u),
               (cx - cint * u, 0.40 * u)]
        d.polygon(pts, fill=255)
        r_o = 0.045 * u
        d.ellipse([cx - ombro * u - r_o * 0.4, y_ombro * u - r_o * 0.6, cx - ombro * u + r_o * 1.4, y_ombro * u + r_o * 1.4], fill=255)
        d.ellipse([cx + ombro * u - r_o * 1.4, y_ombro * u - r_o * 0.6, cx + ombro * u + r_o * 0.4, y_ombro * u + r_o * 1.4], fill=255)
    # braços
    br = 0.034 * u if tipo != "mulher" else 0.027 * u
    if tipo == "atirador":
        # braços levantados à frente: de costas só aparecem os cotovelos abertos
        for s in (-1, 1):
            _cap(d, (cx + s * (ombro - 0.02) * u, (y_ombro + 0.02) * u), (cx + s * (ombro + 0.03) * u, 0.27 * u), br)
            _cap(d, (cx + s * (ombro + 0.03) * u, 0.27 * u), (cx + s * 0.03 * u, 0.22 * u), br * 0.9)
    elif tipo != "hacker":
        bal = 0.012 * math.sin(pose * 2 * math.pi)
        for s in (-1, 1):
            ox = cx + s * (ombro - 0.015) * u
            cot = (cx + s * (ombro + 0.012) * u, 0.34 * u)
            mao = (cx + s * (ombro + 0.005 + s * bal) * u, 0.47 * u)
            _cap(d, (ox, (y_ombro + 0.02) * u), cot, br)
            _cap(d, cot, mao, br * 0.85)
            d.ellipse([mao[0] - br, mao[1] - br * 0.6, mao[0] + br, mao[1] + br * 1.6], fill=255)
    # pernas
    if tipo == "hacker":
        pass
    elif tipo == "lider_frente":
        ph = math.sin(pose * 2 * math.pi)
        for s, fase in ((-1, ph), (1, -ph)):
            topo_p = (cx + s * 0.06 * u, 0.74 * u)
            pe = (cx + s * 0.065 * u + fase * 0.01 * u, (0.985 - 0.02 * max(0, fase)) * u)
            _cap(d, topo_p, pe, 0.05 * u)
    else:
        lw = 0.048 * u if tipo != "mulher" else 0.040 * u
        abre = 0.06 if tipo != "mulher" else 0.045
        for s in (-1, 1):
            _cap(d, (cx + s * 0.05 * u, 0.53 * u), (cx + s * abre * u, 0.975 * u), lw)
            # botas
            d.ellipse([cx + s * abre * u - lw * 1.1, 0.95 * u, cx + s * abre * u + lw * 1.1, 1.0 * u], fill=255)
        d.polygon([(cx - quad * u, 0.50 * u), (cx + quad * u, 0.50 * u), (cx + 0.0, 0.60 * u)], fill=255)
    if tipo == "hacker":
        # sentado: cabeça, ombros, encosto da cadeira
        d.rectangle([cx - 0.17 * u, 0.30 * u, cx + 0.17 * u, 0.62 * u], fill=255)
        d.rounded_rectangle([cx - 0.20 * u, 0.26 * u, cx + 0.20 * u, 0.70 * u], radius=int(0.06 * u), fill=255)
        d.rectangle([cx - 0.02 * u, 0.70 * u, cx + 0.02 * u, 0.90 * u], fill=255)
        for s in (-1, 1):
            _cap(d, (cx, 0.90 * u), (cx + s * 0.2 * u, 0.97 * u), 0.012 * u)
        # capuz
        d.ellipse([cx - 0.075 * u, 0.0, cx + 0.075 * u, 0.15 * u], fill=255)
        # braços para a frente (cotovelos)
        for s in (-1, 1):
            _cap(d, (cx + s * (ombro - 0.02) * u, 0.2 * u), (cx + s * (ombro + 0.04) * u, 0.33 * u), br)
    a = np.asarray(im, np.float32) / 255.0
    a = cv2.GaussianBlur(a, (0, 0), S * 2.5)
    a = np.clip((a - 0.5) * 6 + 0.5, 0, 1)
    a = cv2.resize(a, (int(ww / S), int((hh + 20) / S)), interpolation=cv2.INTER_AREA)
    return a, (a.shape[1] / 2, h)


def cola_silhueta(img, mask, x, y, rim_cor=(0.9, 0.85, 0.8), rim=0.9, preto=0.012, borda=6, luz_topo=0.7, some_base=0.0):
    """Cola a silhueta preta com luz de recorte (rim) na borda. (x,y) = posição dos pés."""
    mh, mw = mask.shape
    x0, y0 = int(round(x - mw / 2)), int(round(y - (mh - 20 / 3 * 0) )) - 0
    y0 = int(round(y - mh + mh * 0.0))
    x1, y1 = x0 + mw, y0 + mh
    cx0, cy0 = max(0, x0), max(0, y0)
    cx1, cy1 = min(W, x1), min(H, y1)
    if cx1 <= cx0 or cy1 <= cy0:
        return img
    m = mask[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    bl = cv2.GaussianBlur(mask, (0, 0), borda)[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    aro = np.clip(m - bl, 0, 1) * 2.2
    if some_base > 0:  # a parte de baixo some na névoa do chão
        yy0 = np.linspace(cy0 - y0, cy1 - y0, cy1 - cy0)[:, None] / mh
        f = np.clip((1 - yy0) / some_base, 0, 1) ** 1.2
        m = m * f
        aro = aro * f
    # mais luz em cima (cabeça/ombros) do que embaixo
    yy = np.linspace(cy0 - y0, cy1 - y0, cy1 - cy0)[:, None] / mh
    aro *= (luz_topo + (1 - luz_topo) * (1 - yy)) * rim
    reg = img[cy0:cy1, cx0:cx1]
    base = reg * (1 - m[..., None]) + preto * m[..., None]
    reg[:] = base + aro[..., None] * np.array(rim_cor, np.float32)
    return img
