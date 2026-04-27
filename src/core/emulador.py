
from pyboy import PyBoy, WindowEvent
from core.heuristica import * 
from typing import List
from dataclasses import dataclass

@dataclass
class Jogo:
    jogador: List[str]
    rom:str = "mario.gb"
    velocidade:int = 0
    janela:str = "SDL2"
    estado:str = "state.bin"

class Emulador:
    
    def __init__(self, jogo):
        
        self.jogo = jogo
    
    def iniciar(self):
        
        pyboy = start( self.jogo )
        
        dto = play(
            pyboy, self.jogo.jogador
        )
        
        pyboy.stop()
        
        return dto

def start( jogo ):

    p = PyBoy(
        jogo.rom, window_type = jogo.janela
    )

    p.set_emulation_speed( jogo.velocidade )

    with open( jogo.estado, "rb" ) as f:
        p.load_state( f )

    return p

def play( pyboy, bot ):
    
    victory = False

    _break = False

    x = 0

    acc = 0

    lifes = 3

    last_scroll = 0

    pyboy.set_memory_value(0xDA15, lifes)
    
    mx = -1
    
    for g in bot:

        if ( _break ): break

        reset_inputs(pyboy)

        for _ in range( g["peso"] ):
            
            if ( _break ): break
            
            step(pyboy, g["acao"])

            pyboy.tick()
            
            local = pyboy.get_memory_value(0xC202)
            scroll = pyboy.get_memory_value(0xFF43)
        
            l = pyboy.get_memory_value(0xDA15)

            if ( l < lifes ):

                lifes = l

                if ( lifes == 2 ):
                    _break = True
            
            if (not _break):   
                if ( scroll < last_scroll):
                    if ( x > mx -1 ):
                        acc += 256
                        
    
                last_scroll = scroll
    
                x = local + acc + scroll
                
                if ( x > mx ):
                    mx = x
    
                if ( x == 2392 ):
                    victory = True
                    _break = True

    p = pyboy.get_memory_value(0xC0A1)

    return JogoDTO(
        distancia = mx,
        pontos = p,
        tempo = -1,
        vidas = lifes,
        vitoria = victory
    )
    
def reset_inputs( pyboy : PyBoy )  -> None:
    pyboy.send_input(WindowEvent.RELEASE_ARROW_RIGHT)
    pyboy.send_input(WindowEvent.RELEASE_ARROW_LEFT)
    pyboy.send_input(WindowEvent.RELEASE_BUTTON_A)


def step( pyboy : PyBoy, action: str ) -> None:

    if action == "right":
        pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT)

    elif action == "left":
        pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT)

    elif action == "jump":
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A)