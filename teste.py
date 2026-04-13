from pyboy import PyBoy
import random

# ================= CONFIG =================
ROM = "mario.gb"

POP_SIZE = 30
GENES_LENGTH = 200
GENERATIONS = 400
MUTATION_RATE = 0.3

ACTIONS = [
    None,
    "left",
    "right",
    "jump"
]

# ================= INDIVÍDUO =================
def criar_individuo():
    return [random.choice(ACTIONS) for _ in range(GENES_LENGTH)]

# ================= DETECÇÃO =================
def perigo_a_frente(pyboy):
    mario_x = pyboy.memory[0xC202]
    mario_y = pyboy.memory[0xC201]

    for i in range(10):
        base = 0xD100 + (i * 0x10)

        obj_x = pyboy.memory[base + 3]
        obj_y = pyboy.memory[base + 2]

        if 0 < (obj_x - mario_x) < 20:
            if abs(obj_y - mario_y) < 12:
                return True

    return False

# ================= FITNESS =================
def avaliar(individuo):
    pyboy = PyBoy(ROM, window="null")
    pyboy.set_emulation_speed(0)

    try:
        # iniciar jogo
        for _ in range(150):
            pyboy.tick()

        pyboy.button("start")

        for _ in range(40):
            pyboy.tick()

        vida_inicial = pyboy.memory[0xDA15]

        x_inicial = pyboy.memory[0xC202]
        melhor_x = x_inicial

        i = 0
        pulo_frames = 0
        score = 0

        while True:
            pyboy.tick()

            acao = individuo[i % len(individuo)]

            # ================= EXECUÇÃO =================
            if acao == "left":
                pyboy.button("left")

            elif acao == "right":
                pyboy.button("right")

            elif acao == "jump":
                pulo_frames = 6  # pulo médio

            # segurar pulo
            if pulo_frames > 0:
                pyboy.button("a")
                pulo_frames -= 1

            # ================= ESTADO =================
            x = pyboy.memory[0xC202]

            # progresso
            if x > melhor_x:
                score += (x - melhor_x) * 5
                melhor_x = x

            # leve recompensa por sobreviver
            score += 0.05

            # ================= INTELIGÊNCIA (só avaliação) =================
            if perigo_a_frente(pyboy):
                if acao == "jump":
                    score += 2
                else:
                    score -= 2

            # ================= MORTE =================
            if pyboy.memory[0xDA15] < vida_inicial:
                score -= 500
                score -= (1000 - melhor_x * 2)
                break

            # ================= FIM =================
            if i > 15000:
                break

            i += 1

    except:
        score = 0

    pyboy.stop()
    return score

# ================= GA =================
def selecionar(pop):
    pop.sort(key=lambda x: x[1], reverse=True)
    return pop[: len(pop)//2]

def cruzar(p1, p2):
    corte = random.randint(0, len(p1))
    return p1[:corte] + p2[corte:]

def mutar(ind):
    return [
        random.choice(ACTIONS) if random.random() < MUTATION_RATE else gene
        for gene in ind
    ]

# ================= TREINO =================
populacao = [criar_individuo() for _ in range(POP_SIZE)]

melhor_global = -999999
sem_melhora = 0

for gen in range(GENERATIONS):
    print(f"\n===== Geração {gen} =====")

    avaliados = []

    for i, ind in enumerate(populacao):
        fit = avaliar(ind)
        avaliados.append((ind, fit))
        print(f"Indivíduo {i} -> {fit}")

    avaliados.sort(key=lambda x: x[1], reverse=True)

    # controle de estagnação
    if avaliados[0][1] > melhor_global:
        melhor_global = avaliados[0][1]
        sem_melhora = 0
    else:
        sem_melhora += 1

    print("Melhor da geração:", avaliados[0][1])

    # reset se travar
    if sem_melhora > 10:
        print("RESETANDO POPULAÇÃO (stagnation)")
        populacao = [criar_individuo() for _ in range(POP_SIZE)]
        sem_melhora = 0
        continue

    selecionados = selecionar(avaliados)

    # elitismo
    nova_pop = [ind for ind, _ in avaliados[:2]]

    while len(nova_pop) < POP_SIZE:
        p1, _ = random.choice(selecionados)
        p2, _ = random.choice(selecionados)

        filho = cruzar(p1, p2)
        filho = mutar(filho)

        nova_pop.append(filho)

    populacao = nova_pop

# ================= MELHOR =================
melhor_ind = avaliados[0][0]

print("\nRodando melhor indivíduo...")

pyboy = PyBoy(ROM, window="SDL2")

for _ in range(150):
    pyboy.tick()

pyboy.button("start")

for _ in range(40):
    pyboy.tick()

i = 0
pulo_frames = 0

while True:
    pyboy.tick()

    acao = melhor_ind[i % len(melhor_ind)]

    if acao == "left":
        pyboy.button("left")

    elif acao == "right":
        pyboy.button("right")

    elif acao == "jump":
        pulo_frames = 6

    if pulo_frames > 0:
        pyboy.button("a")
        pulo_frames -= 1

    i += 1
