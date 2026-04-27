
from dataclasses import dataclass


@dataclass
class JogoDTO:
    distancia:float = 0
    pontos:float = 0
    tempo:int = 0
    vidas:int = 0
    vitoria:bool = False


def pontos( dto ):

    p = dto.distancia

    if ( p == 0 ):
        p = 1

    p += dto.pontos * 0.1

    if (dto.vitoria):
        p += 1000

    return p