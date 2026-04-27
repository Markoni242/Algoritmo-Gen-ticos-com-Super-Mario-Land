
from multiprocessing import Pool, cpu_count
from dataclasses import dataclass
from core.emulador import *
from typing import List

import random
import json
import copy
import os

LENGTH = 500
ACTIONS = ["right","jump"]
MIN_STEPS = 2
MAX_STEPS = 25


@dataclass
class GA:
    populacao: List[dict]
    exploracao:float = 0.1
    geracoes:int = 10
    mutacao:float = 0.3
    elite:int = 3


class Solucao:

    def __init__(self, dados = []):
        self.list = dados

    def adicionar(self, agentes):
        self.list.append(agentes)

    def melhor(self):
        
        m = self.list[0][0]

        for p in self.list:
            
            for i in p:
                
                if m["pontos"] < i["pontos"]:
                    
                    m = i 
        return m


class Algoritmo:
    
    def __init__(self, pop):
        self.pop = pop
    
    def treinar(self, mut, exp, elt):

        pop = self.pop

        pop_size = len(pop)

        pop = avaliar( pop )

        pop.sort(
            key=lambda x: x["pontos"],
            reverse=True
        )

        nova_pop = [
            copy.deepcopy(p) for p in pop[:elt]
        ]
        
        while len(nova_pop) < pop_size:

            p1, p2 = selecionar( pop )
            g1, g2 = cruzar( p1, p2 )
            
            f1 = None
            f2 = None
            
            if ( random.random() > exp ):
                f1 = mutacao(
                    individuo( 0, g1 ), mut 
                )
                f2 = mutacao(
                    individuo( 0, g2 ), mut
                )
            else:
                f1 = individuo()
                f2 =  individuo()

            nova_pop.append( f1 ) 
            
            if len(nova_pop) < pop_size:
                nova_pop.append( f2 ) 

        self.pop = nova_pop

        return nova_pop


def worker( p : dict ) -> dict:

    e = Emulador(
        Jogo(
            jogador = p["genes"],
            janela = "null"
        )
    )
    
    dto = e.iniciar()

    p["pontos"] = pontos( dto )

    return p


def avaliar( pop : List[dict] ) -> List[dict]:
    
    with Pool( min(6, cpu_count()) ) as p:
        result = p.map(worker, pop)

    for i, p in enumerate(result):
        print(f"IND {i}: {p['pontos']}")

    return result


def _avaliar( pop : List[dict] ) -> List[dict]:

    for i, p in enumerate(pop):
        
        worker(p)
        
        print(f"IND {i}: {p['pontos']}")

    return pop


def torneio( pop : List[dict], k = 3 ) -> dict:
    c = random.sample(pop, k)
    c.sort(
        key=lambda x: x["pontos"],
        reverse=True
    )
    return c[0]

def acumular( pop : List[dict] ) -> tuple:
    
    soma = 0
    
    for p in pop:
        soma += p["pontos"]
        
    i = 0
    
    acc = 0
    
    sort = random.random() * soma
    
    pai = pop[i]
    
    while i < len(pop) and acc < sort:
        acc += pop[i]["pontos"]
        pai = pop[i]
        i = 0

    return pai


def selecionar( pop ):

    p1 = copy.deepcopy(
        acumular( pop )
    )

    p2 = copy.deepcopy(
        acumular( pop )
    )

    return p1, p2


def cruzar( p1, p2 ):
    c = random.randint(0, len(p1["genes"]) - 1)
    g1 = p1["genes"][:c] + p2["genes"][c:]
    g2 = p2["genes"][:c] + p1["genes"][c:]
    return g1, g2


def mutacao( p, r ):
    for g in p["genes"]:
        if random.random() < r:
            ng = gene()
            g["acao"] = ng["acao"]
            g["peso"] = ng["peso"] 
    return p




def individuo( s : float = 0, g : List[dict] = [] ) -> dict:

    if len(g) == 0:

        g = [
            gene() for _ in range( LENGTH )
        ]

    return {
        "pontos": s,
        "genes": g
    }

def gene():
    return {
        "acao": random.choice( ACTIONS ),
        "peso": random.randint(
            MIN_STEPS, MAX_STEPS
        )
    }

def populacao( size ):
    return [
        individuo() for _ in range( size )
    ]