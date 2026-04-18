
from core.algoritmo import training
from core.emulate import init, clear
from core.models import Mario, Game

import json

def load():
    with open("backup.json", "r") as f:
        return json.load(f)


def save(data):
    with open("backup.json", "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
 
    data = load()
    
    mario = training (
        Individuo(
            score = data["score"],
            genes = data["genes"]
        )
    )
    
    save({
        "score":mario.score,
        "genes":mario.genes
    })

    init(
        Game(
            boot = mario,
            speed = 1,
            show = "SDL2",
            rom = "mario.gb",
            state= "./state.bin"
        )
    )
