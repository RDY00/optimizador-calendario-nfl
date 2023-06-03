""" Modulo que leer los archivos de datos y genera graficas y tablas """

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from genetico import AlgoritmoGenetico

ITERACIONES = 1
P_MUTACION = 0.01
P_CRUZA = 0.9
TAM_POBLACION = 100
T_LIMITE = 3600 # segundos
MUESTRA_CADA = 100
GRAFICA_CADA = 100
EJEMPLAR = "../data/temporada2023.txt"

COLUMNAS = [
  "ejemplar",
  "Repeticiones",
  "Promedio Generaciones",
  "Porcentaje de Exito",
  "Tiempo"
]

RUTA = Path.cwd() / "data"
RUTA_GRAF = Path.cwd().parent / "graphs"
RUTA_GRAF.mkdir(exist_ok=True)

def graficas(promedios: list, mejor: list) -> None:
  fig, ax = plt.subplots()
  ax.plot(mejor, label="Mejor individuo")
  ax.plot(promedios, "--", label="Promedio")
  ax.set_title(f"Evolución del mejor individuo")
  ax.set_xlabel("Generación")
  ax.set_ylabel("Evaluación")
  ax.legend()
  fig.savefig(RUTA_GRAF / f"Graf_mejor.png", bbox_inches="tight")

def obtener_promedios() -> None:
  resultado = []
  generaciones = 0
  tiempos = 0.0
  exitos = 0
  promedio = []
  mejor = []
  mejor_eval = float("-inf")
  l = 0

  # temporada = TemporadaNFL.leer_archivo(EJEMPLAR)

  for i in range(ITERACIONES):
    with open(RUTA / f"Data_{i}.json", "r") as f:
      aux = json.load(f)
      generaciones += aux["generacion"]
      tiempos += aux["tiempo"]
      if(aux["es_optimo"]): exitos += 1
      aux_eval = aux["evaluacion"] - aux["generacion"]
      if aux_eval > mejor_eval:
        mejor_eval = aux_eval
        mejor = aux["optimos"]
      promedio.append(aux["optimos"])
      l = max(l, len(aux["optimos"]))

    aux_prom = np.array([v + v[-1:]*(l-len(v)) for v in promedio]).mean(axis=0)
    mejor = mejor + mejor[-1:]*(l-len(mejor))
    graficas(aux_prom, mejor)
    
    fila = (EJEMPLAR, ITERACIONES, generaciones/ITERACIONES,
            (exitos/ITERACIONES)*100, tiempos/ITERACIONES)
    resultado.append(fila)

    print("Listo UwU")

  df = pd.DataFrame(resultado, columns = COLUMNAS)
  df.to_excel(Path.cwd().parent / 'ejecuciones.xls')

if __name__ == "__main__":
  obtener_promedios()

