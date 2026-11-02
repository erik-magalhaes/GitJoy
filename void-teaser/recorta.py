"""Recorta pessoas das fotos (rembg, modelo humano) -> assets/sil_<nome>.png (máscara alfa)."""
import sys
import numpy as np
from PIL import Image
from rembg import remove, new_session
s = new_session("u2net_human_seg")
for arg in sys.argv[1:]:
    src, nome = arg.split(":")
    im = Image.open(src).convert("RGB")
    a = np.asarray(remove(im, session=s, only_mask=True))
    Image.fromarray(a).save(f"assets/sil_{nome}.png")
    print(nome, a.shape)
