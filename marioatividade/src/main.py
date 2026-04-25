from core.algoritmo import training
from core.emulate import init
from core.models import *
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def registrar_evolucao(geracao, melhor_score, media_score, arquivo="evolucao.csv"):
    novos_dados = pd.DataFrame([{
        'geracao': geracao,
        'melhor_score': melhor_score,
        'media_score': media_score,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    if os.path.exists(arquivo):
        df_existente = pd.read_csv(arquivo)
        df_final = pd.concat([df_existente, novos_dados], ignore_index=True)
    else:
        df_final = novos_dados
    df_final.to_csv(arquivo, index=False)


def gerar_tabela_final(arquivo="evolucao.csv"):
    if not os.path.exists(arquivo):
        return None
    df = pd.read_csv(arquivo)
    print("\n" + "=" * 80)
    print("TABELA DE EVOLUÇÃO DO TREINAMENTO")
    print("=" * 80)
    print(f"{'Geração':<10} {'Melhor Score':<20} {'Média':<20} {'Melhoria':<15}")
    print("-" * 80)
    ultimo_melhor = None
    for _, row in df.iterrows():
        geracao = int(row['geracao'])
        melhor = float(row['melhor_score'])
        media = float(row['media_score'])
        if ultimo_melhor is not None:
            melhoria = melhor - ultimo_melhor
            melhoria_str = f"+{melhoria:.2f}" if melhoria > 0 else f"{melhoria:.2f}"
        else:
            melhoria_str = "-"
        print(f"{geracao:<10} {melhor:<20.2f} {media:<20.2f} {melhoria_str:<15}")
        ultimo_melhor = melhor
    print("=" * 80)
    print("\nESTATÍSTICAS FINAIS:")
    print(f"   Melhor score geral: {df['melhor_score'].max():.2f} (geração {df[df['melhor_score'] == df['melhor_score'].max()]['geracao'].values[0]})")
    print(f"   Score inicial: {df.iloc[0]['melhor_score']:.2f}")
    print(f"   Score final: {df.iloc[-1]['melhor_score']:.2f}")
    print(f"   Melhoria total: {df.iloc[-1]['melhor_score'] - df.iloc[0]['melhor_score']:.2f}")
    print(f"   Média geral: {df['melhor_score'].mean():.2f}")
    return df


def plotar_evolucao(arquivo="evolucao.csv"):
    if not os.path.exists(arquivo):
        return
    df = pd.read_csv(arquivo)
    plt.figure(figsize=(12, 6))
    plt.plot(df['geracao'], df['melhor_score'], 'b-', label='Melhor Score', linewidth=2)
    plt.plot(df['geracao'], df['media_score'], 'r--', label='Média', linewidth=2)
    plt.fill_between(df['geracao'], df['melhor_score'], df['media_score'], alpha=0.2)
    plt.xlabel('Geração')
    plt.ylabel('Score')
    plt.title('Evolução do AG - Super Mario Land')
    plt.legend()
    plt.grid(True, alpha=0.3)
    arquivo_grafico = f"evolucao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(arquivo_grafico, dpi=150, bbox_inches='tight')
    plt.show()


def load():
    if os.path.exists("backup.json"):
        with open("backup.json", "r") as f:
            data = json.load(f)
            if "genes" in data:
                data["genes"] = [g for g in data["genes"] if g["action"] in ["right", "jump", "left"]]
            return data
    return {"score": 0, "genes": []}


def save(data):
    with open("backup.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    if os.path.exists("evolucao.csv"):
        os.remove("evolucao.csv")
    data = load()
    mario = Individuo(score=data["score"], genes=data["genes"])
    resultado = training(mario)
    save({"score": resultado.score, "genes": resultado.genes})
    gerar_tabela_final()
    plotar_evolucao()
    init(Game(
        boot=resultado,
        speed=1,
        show="SDL2",
        rom="mario.gb",
        state="./state.bin",
        assess=False
    ))