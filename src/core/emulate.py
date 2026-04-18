
from pyboy import PyBoy, WindowEvent
from .models import *


def reset_inputs( pyboy : PyBoy )  -> None:
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)


def step( pyboy : PyBoy, action: str ) -> None:
    if action == "right":
        pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    elif action == "left":
        pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
    elif action == "jump":
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)


def init( g : Game  ) -> float:

    pyboy = start(
        g.rom,
        g.show,
        g.speed,
        g.state
    )

    score = play(
        pyboy,
        g.boot
    )

    stop( pyboy )

    return score
    

def start( rm: str, wn: str, sp: int, st: str ) -> PyBoy:
    pyboy = PyBoy(
        rm, window_type = wn
    )

    pyboy.set_emulation_speed(sp)

    with open( st, "rb" ) as file:
        pyboy.load_state( file )
        
    return pyboy
    

def play( pyboy : PyBoy, b : object ) -> float:

    vida_inicial = pyboy.get_memory_value(0xDA15)
    melhor_x = pyboy.get_memory_value(0xC202)
    ultimo_x = melhor_x
    parado = 0
    score = 0

    for g in b.genes:

        reset_inputs(pyboy)

        if g["action"] == "left" and g["weight"] > 10 :
            score -= 25

        for _ in range( g["weight"] ):
            
            step(pyboy, g["action"])
            
            pyboy.tick()

            x = pyboy.get_memory_value(0xC202)

            # =========================
            # PROGRESSO (PRINCIPAL)
            # =========================
            if x > melhor_x:
                ganho = x - melhor_x
                score += ganho * 10 
                melhor_x = x

            # =========================
            # DETECCAO DE STALL
            # =========================
            if x <= ultimo_x:
                parado += 1
            else:
                parado = 0

            ultimo_x = x

            # =========================
            # MORTE
            # =========================
            if pyboy.get_memory_value(0xDA15) < vida_inicial:
                score -= 800
                return score

            # =========================
            # EARLY STOP (TRAVADO)
            # =========================
            if parado > 80:
                score -= 300
                return score

    return score

def state( g : Game ) -> None:
    
    pyboy = start(
        g.rom,
        g.show,
        g.speed,
        g.state
    )
    
    play(
        pyboy,
        g.boot
    )
    
    with open( "./src/state.bin", "wb" ) as file:
        pyboy.save_state( file )

    stop( pyboy )
    

def stop( p : PyBoy ) -> None:
    p.stop()

def clear( rom ) -> None:
    pyboy = PyBoy(rom, window_type="null")
    pyboy.set_emulation_speed(0)

    for _ in range(100):
        pyboy.tick()

    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

    for _ in range(30):
        pyboy.tick()
    
    with open( "./src/state.bin", "wb" ) as file:
        pyboy.save_state( file )
        
    stop( pyboy )