from dataclasses import dataclass
from typing import List

@dataclass
class Mario:
    score: float
    genes: List[dict]

@dataclass
class Individuo:
    score: float
    genes: List[dict]
    
@dataclass
class Game:
    boot: object
    state: str
    speed: int
    show: str
    rom: str
    