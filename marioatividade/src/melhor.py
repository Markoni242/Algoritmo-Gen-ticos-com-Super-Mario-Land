from core.emulate import init
from core.models import *
import json
import os
import sys

def carregar_individuo(arquivo="backup.json"):
    if not os.path.exists(arquivo):
        return None
    with open(arquivo, "r") as f:
        return json.load(f)

def executar(data, velocidade=1, mostrar_janela=True):
    mario = Individuo(score=data["score"], genes=data["genes"])
    init(Game(
        boot=mario,
        speed=velocidade,
        show="SDL2" if mostrar_janela else "null",
        rom="mario.gb",
        state="./state.bin",
        assess=False
    ))

if __name__ == "__main__":
    arquivo = sys.argv[1] if len(sys.argv) > 1 else "backup.json"
    data = carregar_individuo(arquivo)
    if data:
        executar(data)