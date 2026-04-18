from dataclasses import dataclass
from typing import List

@dataclass
class Individuo:
    score: float
    genes: List[dict]
    
@dataclass
class Game:
    boot: Individuo
    state: str
    speed: int
    show: str
    rom: str
    