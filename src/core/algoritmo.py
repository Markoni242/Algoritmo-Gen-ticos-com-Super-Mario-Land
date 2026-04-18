
from multiprocessing import Pool, cpu_count
from .emulate import init, state
from .models import *
from typing import List
import random
import json
import copy
import os


TOP = 3
ELITE_SIZE = 2
EXPLARATION_RATE = 0.1
POP_SIZE = 20
GENERATIONS = 20
MUTATION_RATE = 0.3
GENES_LENGTH = 1000
MAX_STEPS = 30
MIN_STEPS = 1
ACTIONS = [
    "left",
    "right",
    "jump" 
]

def individuo() -> Individuo:
    return Individuo(
        score = 0,
        genes = [
            {
                "action": random.choice( ACTIONS ),
                "weight": random.randint(
                    MIN_STEPS, MAX_STEPS
                )
            } for _ in range( GENES_LENGTH )
        ]
    )

def propagation( m: Individuo, i: Individuo ) -> Individuo:
    
    b = Individuo( 0, m.genes + i.genes )

    g = Game(
        boot = b,
        speed = 0,
        show = "null",
        rom = "mario.gb",
        state= "./state.bin"
    )

    score = init( g )

    b.score = score

    if ( score > m.score):
        state( g )
        return b
    
    return m

def worker( p : Individuo ) -> Individuo:

    score = init(
        Game(
            boot = p,
            speed = 0,
            show = "null",
            rom = "mario.gb",
            state= "./src/state.bin"
        )
    )

    p.score = score

    return p

def assess( pop : List[Individuo] ) -> List[Individuo]:

    with Pool( min(6, cpu_count()) ) as p:
        result = p.map(worker, pop)

    for i, r in enumerate(result):
        print(f"IND {i}: {r.score}")

    return result

def crossover( p1 : Individuo, p2 : Individuo) -> (List[dict], List[dict]):
    c = random.randint(0, len(p1.genes) - 1)
    g1 = p1.genes[:c] + p2.genes[c:]
    g2 = p2.genes[:c] + p1.genes[c:]
    return g1, g2

def mutation( p :Individuo ) -> None:
    for g in p.genes:
        if random.random() < MUTATION_RATE:
            g["action"] = random.choice(ACTIONS)
            g["weight"] = random.randint(
                MIN_STEPS, MAX_STEPS
            )
    return p

def tournament( pop : List[Individuo], k = 3 ) -> Individuo:
    c = random.sample(pop, k)
    c.sort(
        key=lambda x: x.score,
        reverse=True
    )
    return c[0]

def selection( pop : List[Individuo] ) -> (Individuo, Individuo):
    p1 = tournament( pop )
    p2 = tournament( pop )
    return p1, p2

def training( m : Individuo ) -> Individuo:

    stagnation = 0

    pop = [
        individuo() for _ in range( POP_SIZE )
    ]

    for g in range( GENERATIONS ):

        print(f"\nGERACAO {g} ----------------")

        pop = assess( pop )

        pop.sort(
            key=lambda x: x.score,
            reverse=True
        )
        
        for e in pop[:TOP]:
            m = propagation( m, e )

        new_pop = pop[:ELITE_SIZE]

        while len(new_pop) < POP_SIZE:

            if random.random() < EXPLARATION_RATE:

                new_pop.append(
                    individuo()
                )

                continue
            
            p1, p2 = selection(pop)
            g1, g2 = crossover(p1, p2)

            f1 = mutation(
                Individuo(0, g1)
            )
            f2 = mutation(
                Individuo(0, g2)
            )

            if ( random.random() < 0.4 ):
                new_pop.append(f1)

            else:
                new_pop.append(f2)

        pop = new_pop

    return m
