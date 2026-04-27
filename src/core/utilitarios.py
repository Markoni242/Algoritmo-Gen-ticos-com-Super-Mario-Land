
import json

def carregar( caminho ):
    with open(caminho, "r") as f:
        return json.load(f)
    
def salvar( caminho, dados ):
    with open(caminho, "w") as f:
        json.dump(dados, f)

def limpar( rom : str ) -> None:
    pyboy = PyBoy( rom, window_type="null" )

    with open( "./state.bin", "rb" ) as file:
        pyboy.load_state( file )

    with open( "./core/state.bin", "wb" ) as file:
        pyboy.save_state( file )

    pyboy.stop()