import json
import os
import random
import copy
from multiprocessing import Pool, cpu_count
from pyboy import PyBoy, WindowEvent

# =========================
# CONFIG
# =========================
ACTIONS = ["left", "right", "jump"]

GENERATIONS = 15
POP_SIZE = 15
MUTATION_RATE = 0.25
GENES_LENGTH = 500

MAX_STEPS = 30
MIN_STEPS = 1

BACKUP = "backup.json"
ROM = "mario.gb"

# =========================
# INPUT HELPERS (IMPORTANTE)
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
# INDIVIDUO
# =========================
class Individuo:
    def __init__(self, genes=None):
        self.score = 0
        if genes is None:
            self.genes = [Individuo.gene() for _ in range(GENES_LENGTH)]
        else:
            self.genes = copy.deepcopy(genes)

    @staticmethod
    def gene():
        return {
            "action": random.choice(ACTIONS),
            "weight": random.randint(MIN_STEPS, MAX_STEPS)
        }

    def mutate(self):
        for i in range(len(self.genes)):
            if random.random() < MUTATION_RATE:
                self.genes[i] = Individuo.gene()
        return self

    def _EXECUTE(self, pyboy, avaliar=False):
        self.score = 0

        vida_inicial = pyboy.get_memory_value(0xDA15)
        melhor_x = pyboy.get_memory_value(0xC202)

        ultimo_x = melhor_x
        parado = 0

        for g in self.genes:
            reset_inputs(pyboy)

            for _ in range(min(g["weight"], MAX_STEPS)):
                press_action(pyboy, g["action"])
                pyboy.tick()

                if not avaliar:
                    continue

                x = pyboy.get_memory_value(0xC202)

                # progresso
                if x > melhor_x:
                    self.score += (x - melhor_x) * 5
                    melhor_x = x

                self.score += 0.05

                # parado
                if x == ultimo_x:
                    parado += 1
                    self.score -= 0.2
                else:
                    parado = 0

                ultimo_x = x

                # morte
                if pyboy.get_memory_value(0xDA15) < vida_inicial:
                    self.score -= 500
                    return

                # travado
                if parado > 80:
                    self.score -= 50
                    return

    def _RUNNING(self, pyboy, avaliar=False):
        # boot
        for _ in range(100):
            pyboy.tick()

        pyboy.send_input(WindowEvent.PRESS_BUTTON_START)
        pyboy.tick()
        pyboy.send_input(WindowEvent.RELEASE_BUTTON_START)

        for _ in range(30):
            pyboy.tick()

        self._EXECUTE(pyboy, avaliar)
        pyboy.stop()

    def show(self):
        pyboy = PyBoy(ROM, window_type="SDL2")
        pyboy.set_emulation_speed(1)
        self._RUNNING(pyboy, avaliar=False)

    def avaliar(self):
        pyboy = PyBoy(ROM, window_type="headless")
        pyboy.set_emulation_speed(0)
        self._RUNNING(pyboy, avaliar=True)

# =========================
# WORKER (MULTIPROCESS)
# =========================
def avaliar_worker(genes):
    ind = Individuo(genes)

    pyboy = PyBoy(ROM, window_type="headless")
    pyboy.set_emulation_speed(0)

    ind._RUNNING(pyboy, avaliar=True)

    return {
        "score": ind.score,
        "genes": ind.genes
    }

def avaliar_paralelo(populacao):
    with Pool(min(6, cpu_count())) as p:
        resultados = p.map(
            avaliar_worker,
            [ind.genes for ind in populacao]
        )

    avaliados = []
    for i, r in enumerate(resultados):
        ind = Individuo(r["genes"])
        ind.score = r["score"]
        avaliados.append(ind)
        print(f" INDIVIDUO {i}: {ind.score}")

    return avaliados

# =========================
# GA
# =========================
class Algorithm:
    def __init__(self, data):
        self.score = data['score']
        self.genes = data['genes']

        if self.genes is None:
            self.populacao = [Individuo() for _ in range(POP_SIZE)]
        else:
            self.populacao = [
                Individuo(self.genes) if i < 2 else Individuo()
                for i in range(POP_SIZE)
            ]

    @staticmethod
    def select(pop):
        return pop[:len(pop)//2]

    @staticmethod
    def crossover(p1, p2):
        corte = random.randint(0, len(p1.genes))
        genes = p1.genes[:corte] + p2.genes[corte:]
        return [dict(g) for g in genes]

    def training(self):
        sem_melhora = 0

        for g in range(GENERATIONS):
            print(f"\nGERACAO {g} ----")

            avaliados = avaliar_paralelo(self.populacao)

            avaliados.sort(key=lambda x: x.score, reverse=True)

            melhor = avaliados[0]
            print(" -- Melhor:", melhor.score)

            if melhor.score > self.score:
                self.score = melhor.score
                self.genes = copy.deepcopy(melhor.genes)

                Application.save({
                    "score": melhor.score,
                    "genes": melhor.genes
                })

                sem_melhora = 0
            else:
                sem_melhora += 1

            if sem_melhora > 15:
                print("\nRESET POPULACAO ----")
                self.populacao = [Individuo() for _ in range(POP_SIZE)]
                sem_melhora = 0
            else:
                selecionados = Algorithm.select(avaliados)

                pop = [Individuo(i.genes) for i in avaliados[:2]]

                while len(pop) < POP_SIZE:
                    p1 = random.choice(selecionados)
                    p2 = random.choice(selecionados)

                    filho = Individuo(
                        Algorithm.crossover(p1, p2)
                    ).mutate()

                    pop.append(filho)

                self.populacao = pop

    def result(self):
        if self.genes:
            Individuo(self.genes).show()

# =========================
# APP
# =========================
class Application:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    @staticmethod
    def load(file=BACKUP):
        if not os.path.exists(file):
            return {"score": 0, "genes": None}

        with open(file, "r") as f:
            return json.load(f)

    @staticmethod
    def save(data):
        with open(BACKUP, "w") as f:
            json.dump(data, f)

    @staticmethod
    def start():
        app = Application(
            Algorithm(Application.load(BACKUP))
        )
        app.algorithm.training()
        app.algorithm.result()

# =========================
# RUN (OBRIGATÓRIO WINDOWS)
# =========================
if __name__ == "__main__":
    Application.start()