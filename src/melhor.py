
from core.utilitarios import *

from core.algoritimo import *

from core.emulador import *

dados = carregar( "backup.json" )

solucao = Solucao(
    dados
)

melhor = solucao.melhor()

print(melhor["pontos"])

e = Emulador(
    Jogo(

        jogador = melhor["genes"]

    )
)

e.iniciar()