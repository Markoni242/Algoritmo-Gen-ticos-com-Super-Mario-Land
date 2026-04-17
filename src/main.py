from multiprocessing import Pool, cpu_count
from pyboy import PyBoy, WindowEvent
from dataclasses import dataclass
from typing import List
import json
import os
import random
import copy

ACTIONS = ["left", "right", "jump"]

GENERATIONS = 5
POP_SIZE = 10
MUTATION_RATE = 0.25
GENES_LENGTH = 500

MAX_STEPS = 30
MIN_STEPS = 1

BACKUP = "backup.json"
ROM = "mario.gb"


# =========================
# MODEL
# =========================
@dataclass
class Individual:
    score: float
    genes: List[dict]


# =========================
# IO
# =========================
def load(file=BACKUP):
    if not os.path.exists(file):
        return {"score": 0, "genes": None}
    with open(file, "r") as f:
        return json.load(f)


def save(data):
    with open(BACKUP, "w") as f:
        json.dump(data, f)


# =========================
# INPUT
# =========================
def reset_inputs(pyboy):
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)


def press_action(pyboy, action):
    
    if action == "right":
        pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)
    
    elif action == "left":
        pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)
    
    elif action == "jump":
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)


# =========================
# EXECUCAO
# =========================
def run_individual(genes, avaliar=True):
    pyboy = PyBoy(ROM, window_type="null" if avaliar else "SDL2")
    pyboy.set_emulation_speed(0 if avaliar else 1)

    for _ in range(100):
        pyboy.tick()

    pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
    pyboy.tick()
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

    for _ in range(30):
        pyboy.tick()

    vida_inicial = pyboy.get_memory_value(0xDA15)

    melhor_x = pyboy.get_memory_value(0xC202)
    ultimo_x = melhor_x

    parado = 0
    score = 0

    for g in genes:
        reset_inputs(pyboy)

        for _ in range(min(g["weight"], MAX_STEPS)):
            press_action(pyboy, g["action"])
            pyboy.tick()

            if not avaliar:
                continue

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

            # penalidade leve por ficar parado
            if parado > 10:
                score -= 1
            
            if g["action"] == "left":
                score -= 20

            score += 0.1

            # =========================
            # MORTE
            # =========================
            if pyboy.get_memory_value(0xDA15) < vida_inicial:
                score -= 800 # mais forte
                pyboy.stop()
                return score

            # =========================
            # EARLY STOP (TRAVADO)
            # =========================
            if parado > 80:
                score -= 300
                pyboy.stop()
                return score

    pyboy.stop()
    return score


def worker(ind: Individual):
    score = run_individual(ind.genes)
    ind.score = score
    return ind


def assess(pop):
    with Pool(min(6, cpu_count())) as p:
        result = p.map(worker, pop)

    for i, r in enumerate(result):
        print(f"IND {i}: {r.score}")

    return result


# =========================
# GA
# =========================
def mutate(ind: Individual):
    for g in ind.genes:
        if random.random() < MUTATION_RATE:
            g["action"] = random.choice(ACTIONS)
            g["weight"] = random.randint(MIN_STEPS, MAX_STEPS)
    return ind


def selection(pop):
    top = pop[:len(pop)//2]
    return random.choice(top), random.choice(top)


def crossover(p1, p2):
    c = random.randint(0, len(p1.genes) - 1)

    g1 = p1.genes[:c] + p2.genes[c:]
    g2 = p2.genes[:c] + p1.genes[c:]

    return g1, g2


def random_individual():
    return Individual(
        score=0,
        genes=[
            {
                "action": random.choice(ACTIONS),
                "weight": random.randint(MIN_STEPS, MAX_STEPS)
            }
            for _ in range(GENES_LENGTH)
        ]
    )


# =========================
# TRAIN
# =========================
def training(best, pop):
    stagnation = 0

    for g in range(GENERATIONS):
        print(f"\nGERACAO {g} ----------------")

        pop = assess(pop)
        pop.sort(key=lambda x: x.score, reverse=True)

        b = pop[0]
        print("BEST:", b.score)

        if b.score > best.score:
            best = copy.deepcopy(b)
            save({"score": best.score, "genes": best.genes})
            stagnation = 0
        else:
            stagnation += 1

        if stagnation > 10:
            print("RESET POP")
            pop = [random_individual() for _ in range(POP_SIZE)]
            stagnation = 0
            continue

        new_pop = [best] # elitismo

        while len(new_pop) < POP_SIZE:
            p1, p2 = selection(pop)
            g1, g2 = crossover(p1, p2)

            f1 = mutate(Individual(0, g1))
            f2 = mutate(Individual(0, g2))

            new_pop.append(f1)

            if len(new_pop) < POP_SIZE:
                new_pop.append(f2)

        pop = new_pop

    return best


# =========================
# RUN
# =========================
if __name__ == "__main__":

    data = load()

    if ( len(data["genes"]) > 0 ):
        initial_pop = [
            random_individual() for _ in range(POP_SIZE-2)
        ]
        initial_pop.append(
            Individual(
                1, data["genes"]
            )
        )
        initial_pop.append(
            Individual(
                1, data["genes"]
            )
        )
    else:
        initial_pop = [
            random_individual() for _ in range(POP_SIZE)
        ]

    best = training(
        Individual(
            data["score"],
            data["genes"]
        ),
        initial_pop
    )
    
    print("\nMELHOR FINAL:", best.score)

    run_individual(best.genes, avaliar=False)