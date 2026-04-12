from pyboy import PyBoy
import random

# ================= CONFIG =================
ROM = "mario.gb"

POP_SIZE = 6
GENES_LENGTH = 100
GENERATIONS = 5
MUTATION_RATE = 0.1

ACTIONS = ["a", "left", "right", None]


# ================= INDIVÍDUO =================
def criar_individuo():
    return [random.choice(ACTIONS) for _ in range(GENES_LENGTH)]


# ================= FITNESS =================
def avaliar(individuo):
    pyboy = PyBoy(ROM, window="SDL2")
    pyboy.set_emulation_speed(0)

    try:
        # iniciar jogo
        for _ in range(200):
            pyboy.tick()

        pyboy.button("start")

        for _ in range(50):
            pyboy.tick()

        melhor_x = 0
        i = 0

        vida_inicial = pyboy.memory[0xDA15]

        while True:
            pyboy.tick()

            # ação (loop circular)
            acao = individuo[i % len(individuo)]
            if acao:
                pyboy.button(acao)

            i += 1

            # posição X
            pos_x = pyboy.memory[0xC202]
            if pos_x > melhor_x:
                melhor_x = pos_x

            # morreu de verdade
            vida_atual = pyboy.memory[0xDA15]
            if vida_atual < vida_inicial:
                break

            # passou de fase
            mundo = pyboy.memory[0x982C]
            fase = pyboy.memory[0x982E]

            if mundo != 1 or fase != 1:
                melhor_x += 1000
                break

            # limite de segurança (evita loop infinito)
            if i > 20000:
                break

        score = melhor_x

    except:
        score = 0

    pyboy.stop()
    return score


# ================= GA =================
def selecionar(pop):
    pop.sort(key=lambda x: x[1], reverse=True)
    return pop[: len(pop)//2]


def cruzar(p1, p2):
    corte = random.randint(0, GENES_LENGTH)
    return p1[:corte] + p2[corte:]


def mutar(ind):
    return [
        random.choice(ACTIONS) if random.random() < MUTATION_RATE else gene
        for gene in ind
    ]


# ================= TREINAMENTO =================
populacao = [criar_individuo() for _ in range(POP_SIZE)]

for gen in range(GENERATIONS):
    print(f"\n===== Geração {gen} =====")

    avaliados = []

    for i, ind in enumerate(populacao):
        fit = avaliar(ind)
        avaliados.append((ind, fit))
        print(f"Indivíduo {i} -> Fitness: {fit}")

    selecionados = selecionar(avaliados)

    nova_pop = [ind for ind, _ in selecionados]

    while len(nova_pop) < POP_SIZE:
        p1, _ = random.choice(selecionados)
        p2, _ = random.choice(selecionados)

        filho = cruzar(p1, p2)
        filho = mutar(filho)

        nova_pop.append(filho)

    populacao = nova_pop


# ================= MELHOR =================
avaliados_finais = [(ind, avaliar(ind)) for ind in populacao]
melhor_ind, melhor_fit = max(avaliados_finais, key=lambda x: x[1])

print("\n===== RESULTADO FINAL =====")
print("Melhor fitness:", melhor_fit)


# ================= VISUAL =================
print("\nRodando melhor indivíduo...")

pyboy = PyBoy(ROM, window="SDL2")

# iniciar jogo
for _ in range(200):
    pyboy.tick()

pyboy.button("start")

for _ in range(50):
    pyboy.tick()

# executar melhor sequência
i = 0
while True:
    pyboy.tick()

    acao = melhor_ind[i % len(melhor_ind)]
    if acao:
        pyboy.button(acao)

    i += 1

    # parar se morrer
    if pyboy.memory[0xDA15] < pyboy.memory[0xDA15]:
        break