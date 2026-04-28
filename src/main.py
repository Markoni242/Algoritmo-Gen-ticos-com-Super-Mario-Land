
from core.utilitarios import *

from core.algoritimo import *

from core.emulador import *

def resolver( solucao, g : GA ) -> Solucao:

    pop = g.populacao
    exp = g.exploracao
    gen = g.geracoes
    mut = g.mutacao
    elt = g.elite

    algoritimo = Algoritmo( pop )

    solucao = Solucao(
        dados
    )
        
    for g in range( gen ):
        
        print("\nLOOP: ", g)

        solucao.adicionar(
            agentes = algoritimo.treinar( mut, exp, elt ) 
        )

        salvar( "backup.json", solucao.list )

    return solucao


if ( __name__ == "__main__" ):

    dados = carregar( "backup.json" )

    pop = []

    if ( len(dados) == 0 ):
        pop = populacao( 75 )
    else:
        pop = dados[ len(dados) - 1 ]
    
    solucao = resolver(
        dados,
        GA(
           populacao = pop,
           exploracao= 0.25,
           geracoes = 350 - len(dados),
           mutacao = 0.4
        )
    )
    
