from multiprocessing import Pool, cpu_count
from .emulate import init
from .models import *
from typing import List
import random
import json
import copy
import os
import csv
from datetime import datetime


TOP = 3
ELITE_SIZE = 2
EXPLORATION_RATE = 0.15
POP_SIZE = 30
GENERATIONS = 100
MUTATION_RATE = 0.35
GENES_LENGTH = 500
MAX_STEPS = 25
MIN_STEPS = 2
ACTIONS = ["right", "jump", "right", "left"]


def inicializar_csv(arquivo="evolucao.csv"):
    if not os.path.exists(arquivo):
        with open(arquivo, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["geracao", "melhor_score", "media_score", "timestamp"])


def registrar_evolucao(geracao, melhor_score, media_score, arquivo="evolucao.csv"):
    with open(arquivo, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            geracao,
            round(melhor_score, 2),
            round(media_score, 2),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])


def individuo() -> Individuo:
    genes = []
    for _ in range(GENES_LENGTH):
        genes.append({
            "action": random.choice(ACTIONS),
            "weight": random.randint(MIN_STEPS, MAX_STEPS)
        })
    return Individuo(score=0, genes=genes)


def propagation(m: Individuo, i: Individuo) -> Individuo:
    if not m.genes or len(m.genes) == 0:
        m = individuo()
    if not i.genes or len(i.genes) == 0:
        i = individuo()

    ponto = random.randint(1, min(len(m.genes), len(i.genes)) - 1)
    novos_genes = m.genes[:ponto] + i.genes[ponto:]

    if len(novos_genes) > GENES_LENGTH:
        novos_genes = novos_genes[:GENES_LENGTH]

    b = Individuo(0, novos_genes)

    g = Game(
        boot=b,
        speed=0,
        show="null",
        rom="mario.gb",
        state="./state.bin"
    )

    try:
        score = init(g)
        b.score = score
    except Exception:
        return m

    if score > m.score:
        return b
    return m


def worker(p: Individuo) -> Individuo:
    try:
        score = init(
            Game(
                boot=p,
                speed=0,
                show="null",
                rom="mario.gb",
                state="./state.bin"
            )
        )
        p.score = score
    except Exception:
        p.score = 0
    return p


def assess(pop: List[Individuo]) -> List[Individuo]:
    with Pool(min(4, cpu_count())) as p:
        result = p.map(worker, pop)
    return result


def crossover(p1: Individuo, p2: Individuo) -> tuple:
    ponto = random.randint(1, min(len(p1.genes), len(p2.genes)) - 1)
    g1 = p1.genes[:ponto] + p2.genes[ponto:]
    g2 = p2.genes[:ponto] + p1.genes[ponto:]
    return g1, g2


def mutation(p: Individuo) -> Individuo:
    new_genes = copy.deepcopy(p.genes)
    for g in new_genes:
        if random.random() < MUTATION_RATE:
            g["action"] = random.choice(ACTIONS)
            g["weight"] = random.randint(MIN_STEPS, MAX_STEPS)
    return Individuo(0, new_genes)


def tournament(pop: List[Individuo], k=3) -> Individuo:
    amostra = random.sample(pop, min(k, len(pop)))
    amostra.sort(key=lambda x: x.score, reverse=True)
    return amostra[0]


def selection(pop: List[Individuo]) -> tuple:
    p1 = tournament(pop)
    p2 = tournament(pop)
    return p1, p2


def training(m: Individuo) -> Individuo:
    inicializar_csv("evolucao.csv")

    if not m.genes or len(m.genes) == 0:
        m = individuo()

    pop = [individuo() for _ in range(POP_SIZE)]

    for g in range(GENERATIONS):
        pop = assess(pop)
        pop.sort(key=lambda x: x.score, reverse=True)

        melhor = pop[0].score
        media = sum(p.score for p in pop) / len(pop)

        registrar_evolucao(g + 1, melhor, media)

        print(f"Geração {g+1}: melhor = {melhor:.2f}, média = {media:.2f}")

        for e in pop[:TOP]:
            m = propagation(m, e)

        new_pop = pop[:ELITE_SIZE]

        while len(new_pop) < POP_SIZE:
            if random.random() < EXPLORATION_RATE:
                new_pop.append(individuo())
                continue

            p1, p2 = selection(pop)
            g1, g2 = crossover(p1, p2)

            f1 = mutation(Individuo(0, g1))
            f2 = mutation(Individuo(0, g2))

            new_pop.append(f1)
            if len(new_pop) < POP_SIZE:
                new_pop.append(f2)

        pop = new_pop

        if (g + 1) % 10 == 0:
            with open(f"checkpoint_gen_{g+1}.json", "w") as f:
                json.dump({
                    "score": pop[0].score,
                    "genes": pop[0].genes,
                    "geracao": g + 1
                }, f)

    return m