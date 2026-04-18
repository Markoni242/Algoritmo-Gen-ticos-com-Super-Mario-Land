
from core.algoritmo import training
from core.emulate import init
from core.models import Mario

if __name__ == "__main__":
    
    mario = training (
        Mario(
            genes = []
        )
    )

    init(
        Game(
            boot = mario,
            speed = 1,
            show = "DSL2",
            rom = "mario.gb",
            state= "./state.bin"
        )
    )