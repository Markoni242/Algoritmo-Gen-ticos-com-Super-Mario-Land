
from core.algoritmo import training
from core.emulate import init, clear
from core.models import *

import json

def load():
    with open("backup.json", "r") as f:
        return json.load(f)


def save(data):
    with open("backup.json", "w") as f:
        json.dump(data, f)


data = load()

mario = Individuo(
    score = data["score"],
    genes = data["genes"]
)

init(
    Game(
        boot = mario,
        speed = 1,
        show = "SDL2",
        rom = "mario.gb",
        state= "./state.bin",
        assess= False
    )
)
