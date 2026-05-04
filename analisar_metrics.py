# analisar_metrics.py
# Lê metrics.csv, calcula médias e permite registrar vencedores manualmente.

import pandas as pd
from pathlib import Path

ARQUIVO = "metrics.csv"


def carregar():
    path = Path(ARQUIVO)
    if not path.exists():
        print("Arquivo metrics.csv não encontrado.")
        return None

    df = pd.read_csv(path)

    # Corrige nome digitado errado se existir
    if "estador_visitados" in df.columns:
        df = df.rename(columns={"estador_visitados": "estados_visitados"})

    return df


# def mostrar_resumo(df):
#     print("\n========== RESUMO GERAL ==========\n")

#     print(f"Total de registros: {len(df)}")

#     print("\nMédias gerais:")
#     print(f"Estados visitados: {df['estados_visitados'].mean():.2f}")
#     print(f"Tempo (ms):        {df['tempo(ms)'].mean():.2f}")
#     print(f"Profundidade:      {df['profundidade'].mean():.2f}")

#     print("\nMaior tempo:", df["tempo(ms)"].max())
#     print("Menor tempo:", df["tempo(ms)"].min())

#     print("\nMaior estados:", df["estados_visitados"].max())
#     print("Menor estados:", df["estados_visitados"].min())

def mostrar_resumo(df):
    print("\n========== RESUMO GERAL ==========\n")

    algoritmos = ["minimax", "alfa-beta"]

    for alg in algoritmos:
        df_alg = df[df["algoritmo"] == alg]

        if len(df_alg) == 0:
            continue

        print(f"\n--- {alg.upper()} ---\n")

        print(f"Total de registros: {len(df_alg)}")

        print("\nMédias:")
        print(f"Estados visitados: {df_alg['estados_visitados'].mean():.2f}")
        print(f"Tempo (ms):        {df_alg['tempo(ms)'].mean():.2f}")
        print(f"Profundidade:      {df_alg['profundidade'].mean():.2f}")

        print("\nMaior tempo:", df_alg["tempo(ms)"].max())
        print("Menor tempo:", df_alg["tempo(ms)"].min())

        print("\nMaior estados:", df_alg["estados_visitados"].max())
        print("Menor estados:", df_alg["estados_visitados"].min())

        print("\n--------------------------")


def mostrar_por_algoritmo(df):
    print("\n========== POR ALGORITMO ==========\n")

    agrupado = df.groupby("algoritmo").agg(
        partidas=("algoritmo", "count"),
        media_estados=("estados_visitados", "mean"),
        media_tempo=("tempo(ms)", "mean"),
        media_profundidade=("profundidade", "mean"),
    )

    print(agrupado.round(2))


def mostrar_vitorias(df):
    print("\n========== RESULTADOS ==========\n")

    preenchidos = df[df["vencedor"].notna() & (df["vencedor"] != "")]

    if len(preenchidos) == 0:
        print("Nenhum vencedor preenchido ainda.")
        return

    print(preenchidos["vencedor"].value_counts())


def preencher_vencedores(df):
    vazios = df[df["vencedor"].isna() | (df["vencedor"] == "")]

    if len(vazios) == 0:
        print("Todos vencedores já preenchidos.")
        return df

    print(f"\nExistem {len(vazios)} linhas sem vencedor.")
    print("Digite um valor para todas:")
    print("win / loss / draw")
    valor = input("Valor: ").strip()

    df.loc[vazios.index, "vencedor"] = valor
    df.to_csv(ARQUIVO, index=False)
    print("Arquivo atualizado.")

    return df


def menu():
    while True:
        df = carregar()
        if df is None:
            return

        print("\n========== MENU ==========")
        print("1 - Ver resumo geral")
        print("2 - Ver resumo por algoritmo")
        print("3 - Ver vitórias/derrotas")
        print("4 - Preencher vencedores vazios")
        print("5 - Sair")

        op = input("Escolha: ").strip()

        if op == "1":
            mostrar_resumo(df)

        elif op == "2":
            mostrar_por_algoritmo(df)

        elif op == "3":
            mostrar_vitorias(df)

        elif op == "4":
            df = preencher_vencedores(df)

        elif op == "5":
            break

        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()