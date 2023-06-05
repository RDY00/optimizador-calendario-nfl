""" Modulo que leer los archivos de datos y genera graficas y tablas """

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ITERACIONES = 5
EJEMPLAR = "../data/temporada2023.txt"
COLUMNAS = ["Ejemplar", "Repeticiones", "Promedio Generaciones", "Promedio", "Mejor", "Peor", "Porcentaje de Exito", "Tiempo"]

RUTA = Path.cwd() / "data"
# RUTA.mkdir(exist_ok=True)
RUTA_GRAF = Path.cwd().parent / "graphs"
RUTA_GRAF.mkdir(exist_ok=True)

# Se que no es lo correcto pero es un parche para las gráficas del punto extra
comparaciones = [[], []]

def graficas(promedios: list, mejor: list) -> None:
  fig, ax = plt.subplots()
  ax.plot(mejor, label="Mejor individuo")
  ax.plot(promedios, "--", label="Promedio")
  ax.set_title(f"Evolución del mejor individuo")
  ax.set_xlabel("Generación")
  ax.set_ylabel("Evaluación")
  ax.legend()
  fig.savefig(RUTA_GRAF / f"graf_promedios.png", bbox_inches="tight")

def resultados() -> None:
  resultado = []
  generaciones = 0
  tiempos = 0.0
  exitos = 0
  evaluaciones = []
  promedio = []
  mejor = []
  mejor_eval = float("-inf")
  l = 0

  print(f"Generando datos...", end="")
  for j in range(ITERACIONES):
    with open(RUTA / f"ejecucion_{j+1}.json", "r") as f:
      aux = json.load(f)
      generaciones += aux["generacion"]
      tiempos += aux["tiempo"]
      evaluaciones.append(aux["evaluacion"])
      if(aux["es_optimo"]): exitos += 1
      aux_eval = aux["evaluacion"] - aux["generacion"]
      if aux_eval > mejor_eval:
        mejor_eval = aux_eval
        mejor = aux["optimos"]
      promedio.append(aux["optimos"])
      l = max(l, len(aux["optimos"]))

  aux_prom = np.array([v + v[-1:]*(l-len(v)) for v in promedio]).sum(axis=0) / len(promedio)
  mejor = mejor + mejor[-1:]*(l-len(mejor))
  graficas(aux_prom, mejor)

  fila = (
    EJEMPLAR,
    ITERACIONES,
    generaciones/ITERACIONES,
    sum(evaluaciones)/ITERACIONES,
    max(evaluaciones), min(evaluaciones),
    (exitos/ITERACIONES)*100,
    tiempos/ITERACIONES
  )

  resultado.append(fila)

  print("Listo UwU")

  pd.DataFrame(resultado, columns = COLUMNAS).to_csv(Path.cwd().parent / 'ejecuciones.csv')

if __name__ == "__main__":
  resultados()

