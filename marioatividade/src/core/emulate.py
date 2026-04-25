from pyboy import PyBoy, WindowEvent
from .models import *
import random


def reset_inputs(pyboy: PyBoy) -> None:
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)


def step(pyboy: PyBoy, action: str) -> None:
    if action == "right":
        pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    elif action == "left":
        pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
    elif action == "jump":
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)


def init(g: Game) -> float:
    pyboy = start(g.rom, g.show, g.speed, g.state)
    score = play(pyboy, g.boot, g.assess)
    stop(pyboy)
    return score


def start(rm: str, wn: str, sp: int, st: str) -> PyBoy:
    pyboy = PyBoy(rm, window_type=wn)
    pyboy.set_emulation_speed(sp)
    try:
        with open(st, "rb") as file:
            pyboy.load_state(file)
    except:
        pass
    return pyboy


def play(pyboy: PyBoy, b: Individuo, assess: bool) -> float:
    vida_inicial = pyboy.get_memory_value(0xDA15)
    melhor_x = pyboy.get_memory_value(0xC202)
    score = 0
    passos_totais = 0

    left_consecutivo = 0
    left_antes_progresso = False
    passos_mesma_posicao = 0
    historico_posicoes = []
    loop_detectado = False
    regiao_atual = melhor_x // 100
    ultima_regiao = regiao_atual

    for i, g in enumerate(b.genes):
        reset_inputs(pyboy)

        if g["action"] == "left":
            left_consecutivo += 1
            score -= 3
            if left_consecutivo > 5:
                score -= 5
        else:
            if left_consecutivo > 0:
                left_consecutivo = 0
                left_antes_progresso = True

        for passo in range(g["weight"]):
            step(pyboy, g["action"])
            pyboy.tick()
            passos_totais += 1

            if not assess:
                continue

            x = pyboy.get_memory_value(0xC202)

            if x > melhor_x:
                ganho = x - melhor_x
                score += ganho * 10
                melhor_x = x

                if left_antes_progresso and ganho > 20:
                    score += 100
                    left_antes_progresso = False

                passos_mesma_posicao = 0

                nova_regiao = melhor_x // 100
                if nova_regiao > ultima_regiao:
                    bonus = 500 * (nova_regiao - ultima_regiao)
                    score += bonus
                    ultima_regiao = nova_regiao
            else:
                passos_mesma_posicao += 1

            if passos_mesma_posicao > 100 and passos_mesma_posicao % 20 == 0:
                score -= 10

            historico_posicoes.append(x)
            if len(historico_posicoes) > 50:
                historico_posicoes.pop(0)
                if max(historico_posicoes) - min(historico_posicoes) < 5:
                    if not loop_detectado:
                        score -= 300
                        loop_detectado = True

            score += 1

            if pyboy.get_memory_value(0xDA15) < vida_inicial:
                score -= 200
                return max(score, 0)

    return score


def state(g: Game) -> None:
    pyboy = start(g.rom, g.show, g.speed, g.state)
    play(pyboy, g.boot, g.assess)
    with open("./src/state.bin", "wb") as file:
        pyboy.save_state(file)
    stop(pyboy)


def stop(p: PyBoy) -> None:
    p.stop()


def clear(rom: str) -> None:
    pyboy = PyBoy(rom, window_type="null")
    try:
        with open("./state.bin", "rb") as file:
            pyboy.load_state(file)
    except:
        pass
    try:
        with open("./src/state.bin", "wb") as file:
            pyboy.save_state(file)
    except:
        pass
    stop(pyboy)