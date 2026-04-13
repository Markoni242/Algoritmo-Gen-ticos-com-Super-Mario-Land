from pyboy import PyBoy
import random
import json
import os
import signal
import sys

# ================= CONFIG =================
ROM = "mario.gb"

POP_SIZE = 30
GENES_LENGTH = 20
GENERATIONS = 10
MUTATION_RATE = 0.25

ACTIONS = [None, "left", "right", "jump"]

# ================= GLOBAL =================
melhor_global = -999999
melhor_ind_global = None
sem_melhora = 0

mapa_perigo = {}  # memória de mortes

# ================= SALVAR =================
def salvar(nome, individuo, fitness):
    with open(nome, "w") as f:
        json.dump({
            "genes": individuo,
            "fitness": fitness
        }, f)

# ================= CTRL+C =================
def sair(sig, frame):
    print("\nSalvando antes de sair...")
    if melhor_ind_global:
        salvar("melhor_individuo.json", melhor_ind_global, melhor_global)
    sys.exit(0)

signal.signal(signal.SIGINT, sair)

# ================= CARREGAR =================
def carregar_melhor():
    if os.path.exists("melhor_individuo.json"):
        with open("melhor_individuo.json", "r") as f:
            data = json.load(f)
            print("Carregado melhor indivíduo anterior")
            return data["genes"], data["fitness"]
    return None, -999999

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

    for _ in range(100):
        pyboy.tick()

    pyboy.button("start")

    for _ in range(30):
        pyboy.tick()

    vida_inicial = pyboy.memory[0xDA15]
    melhor_x = pyboy.memory[0xC202]

    i = 0
    pulo_frames = 0
    score = 0
    parado = 0
    ultimo_x = melhor_x

    while True:
        pyboy.tick()

        acao = individuo[i % len(individuo)]

        # ================= EXECUÇÃO =================
        if acao == "left":
            pyboy.button("left")

        elif acao == "right":
            pyboy.button("right")

        elif acao == "jump":
            pulo_frames = random.randint(4, 8)  

        if pulo_frames > 0:
            pyboy.button("a")
            pulo_frames -= 1

        x = pyboy.memory[0xC202]

        # ================= PROGRESSO =================
        if x > melhor_x:
            score += (x - melhor_x) * 5
            melhor_x = x

        # ================= SOBREVIVÊNCIA =================
        score += 0.05

        # ================= PARADO =================
        if x == ultimo_x:
            parado += 1
            score -= 0.2
        else:
            parado = 0

        ultimo_x = x

        # ================= PERIGO =================
        if perigo_a_frente(pyboy):
            if acao == "jump":
                score += 3
            else:
                score -= 3

        # ================= MEMÓRIA DE MORTE =================
        if x in mapa_perigo:
            score -= mapa_perigo[x] * 2

        # ================= MORTE =================
        if pyboy.memory[0xDA15] < vida_inicial:
            score -= 500
            mapa_perigo[x] = mapa_perigo.get(x, 0) + 1
            break

        # ================= TRAVA =================
        if parado > 80:
            score -= 50
            break

        # ================= LIMITE =================
        if i > 3000:
            break

        i += 1

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
        random.choice(ACTIONS) if random.random() < MUTATION_RATE else g
        for g in ind
    ]

# ================= INICIALIZAÇÃO =================
melhor_salvo, melhor_fit_salvo = carregar_melhor()

if melhor_fit_salvo > melhor_global:
    melhor_global = melhor_fit_salvo
    melhor_ind_global = melhor_salvo

populacao = []

for _ in range(POP_SIZE):
    if melhor_salvo and random.random() < 0.4:
        populacao.append(melhor_salvo.copy())
    else:
        populacao.append(criar_individuo())

# ================= TREINO =================
for gen in range(GENERATIONS):
    print(f"\n===== Geração {gen} =====")

    avaliados = []

    for i, ind in enumerate(populacao):
        fit = avaliar(ind)
        avaliados.append((ind, fit))
        print(f"{i}: {fit}")

    avaliados.sort(key=lambda x: x[1], reverse=True)

    melhor_ind = avaliados[0][0]
    melhor_fit = avaliados[0][1]

    print(" Melhor:", melhor_fit)

  
    salvar("backup.json", melhor_ind, melhor_fit)

    
    if melhor_fit > melhor_global:
        melhor_global = melhor_fit
        melhor_ind_global = melhor_ind
        sem_melhora = 0

        salvar("melhor_individuo.json", melhor_ind, melhor_fit)
        print(" Novo melhor salvo!")

    else:
        sem_melhora += 1

    # reset se travar
    if sem_melhora > 15:
        print(" RESET POPULAÇÃO")
        populacao = [criar_individuo() for _ in range(POP_SIZE)]
        sem_melhora = 0
        continue

    selecionados = selecionar(avaliados)

    nova_pop = [ind for ind, _ in avaliados[:3]]

    while len(nova_pop) < POP_SIZE:
        p1, _ = random.choice(selecionados)
        p2, _ = random.choice(selecionados)

        filho = mutar(cruzar(p1, p2))
        nova_pop.append(filho)

    populacao = nova_pop

# ================= EXECUÇÃO FINAL =================
print("\n🎮 Executando melhor indivíduo...")

pyboy = PyBoy(ROM, window="SDL2")

for _ in range(100):
    pyboy.tick()

pyboy.button("start")

for _ in range(30):
    pyboy.tick()

i = 0
pulo_frames = 0

while True:
    pyboy.tick()

    acao = melhor_ind_global[i % len(melhor_ind_global)]

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
