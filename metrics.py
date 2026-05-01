import csv
import os

ARQUIVO = "metrics.csv"

def salvar_metricas(nome_algoritmo, resultado, estados, tempo_ms, profundidade):

    existe = os.path.exists(ARQUIVO)

    with open(ARQUIVO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not existe:
            writer.writerow([
                "algoritmo",
                "resultado",
                "estados_visitados",
                "tempo_ms",
                "profundidade"
            ])

        writer.writerow([
            nome_algoritmo,
            resultado,
            estados,
            round(tempo_ms, 2),
            profundidade
        ])