"""As Cadeiras em 3 partes (fiel ao causo real): Partes 1 e 2 iguais às de cadeiras/, e a Parte 3 fecha a história."""
import copy

from cadeiras.roteiro import *  # noqa: F401,F403
from cadeiras import roteiro as _base

_p3 = copy.deepcopy(_base.EPISODIOS[2])
_p3["fim_texto"] = "Fim"
# a Parte 3 original termina com a esposa do Valdir (gancho da Parte 4); aqui ela fecha a história
_corte = next(i for i, ev in enumerate(_p3["eventos"]) if ev[0] == "chat" and ev[1] == "sonia")
_p3["eventos"] = _p3["eventos"][:_corte] + [
    ("msg", "leo", "TECO, PELO AMOR DE DEUS."),
    ("msg", "teco", "Que foi? A mesa é bonita 😂", dict(dig=0.3)),
    ("chat", "valdir", "23:00"),
    ("msg", "valdir", "Boa noite, Léo! A mesa ainda tá disponível, viu? 😊", dict(dig=0.6)),
    ("msg", "valdir", "Posso mandar mais fotos? 📸", dict(dig=0.6)),
    ("rascunho", "Seu Valdir, pelo amor de", 1.2),
    ("sistema", "Você bloqueou este contato"),
    ("pausa", 2.4),
]
EPISODIOS = [_base.EPISODIOS[0], _base.EPISODIOS[1], _p3]
