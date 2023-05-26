""" Modulo que leer los archivos de datos y genera graficas y tablas """

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from genetico import AlgoritmoGenetico, AlgoritmoGeneticoOX1

ITERACIONES = 5
VALORES = range(8,21)
COLUMNAS = ["N", "Repeticiones", "Promedio Generaciones", "Porcentaje de Exito", "Tiempo"]

RUTA = Path.cwd() / "data"
# RUTA.mkdir(exist_ok=True)
RUTA_GRAF = Path.cwd().parent / "graphs"
RUTA_GRAF.mkdir(exist_ok=True)

# Se que no es lo correcto pero es un parche para las gráficas del punto extra
comparaciones = [[], []]

def graficas(N: int, promedios: list, mejor: list) -> None:
  fig, ax = plt.subplots()
  ax.plot(mejor, label="Mejor individuo")
  ax.plot(promedios, "--", label="Promedio")
  ax.set_title(f"Evolución del mejor individuo ({N})")
  ax.set_xlabel("Generación")
  ax.set_ylabel("Evaluación")
  ax.legend()
  fig.savefig(RUTA_GRAF / f"Graf_{N}.png", bbox_inches="tight")

def comparacion() -> None:
  fig, ax = plt.subplots()
  for i, (v1,v2) in enumerate(zip(*comparaciones)):
    l = max(len(v1), len(v2))
    v1t = list(v1)
    v1t += v1t[-1:] * (l-(len(v1t)))
    v2t = list(v2)
    v2t += v2t[-1:] * (l-(len(v2t)))
    ax.plot(v1t, label="PMX")
    ax.plot(v2t, label="OX1")
    ax.set_title(f"Evolución promedio ({VALORES[i]})")
    ax.set_xlabel("Generación")
    ax.set_ylabel("Evaluación")
    ax.legend()
    fig.savefig(RUTA_GRAF / f"Graf_{VALORES[i]}_comparacion.png", bbox_inches="tight")
    ax.cla()

def datos_ox1() -> None:
  resultado = []
  for i in VALORES:
    generaciones = 0
    tiempos = 0.0
    exitos = 0
    promedio = []
    l = 0

    print(f"Generando datos de {i}...", end="")
    for j in range(ITERACIONES):
      with open(RUTA / f"Data_{i}_{j}_OX1.json", "r") as f:
        aux = json.load(f)
        generaciones += aux["generacion"]
        tiempos += aux["tiempo"]
        if(aux["es_optimo"]): exitos += 1
        promedio.append(aux["optimos"])
        l = max(l, len(aux["optimos"]))

    aux_prom = np.array([v + v[-1:]*(l-len(v)) for v in promedio]).sum(axis=0) / len(promedio)
    comparaciones[1].append(aux_prom)
    # graficas(i, aux_prom, mejor)
    
    fila = (i, ITERACIONES, generaciones/ITERACIONES, (exitos/ITERACIONES)*100, tiempos/ITERACIONES)
    resultado.append(fila)

    print("Listo UwU")

  df = pd.DataFrame(resultado, columns = COLUMNAS).set_index('N')
  # df.to_excel(Path.cwd().parent / 'ejecuciones.xls')
  df.to_csv(Path.cwd().parent / 'ejecuciones_OX1.csv')

def obtener_promedios() -> None:
  resultado = []
  for i in VALORES:
    generaciones = 0
    tiempos = 0.0
    exitos = 0
    promedio = []
    mejor = []
    mejor_eval = float("-inf")
    l = 0

    print(f"Generando datos de {i}...", end="")
    for j in range(ITERACIONES):
      with open(RUTA / f"Data_{i}_{j}.json", "r") as f:
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

    aux_prom = np.array([v + v[-1:]*(l-len(v)) for v in promedio]).sum(axis=0) / len(promedio)
    comparaciones[0].append(aux_prom)
    mejor = mejor + mejor[-1:]*(l-len(mejor))
    graficas(i, aux_prom, mejor)
    
    fila = (i, ITERACIONES, generaciones/ITERACIONES, (exitos/ITERACIONES)*100, tiempos/ITERACIONES)
    resultado.append(fila)

    print("Listo UwU")

  df = pd.DataFrame(resultado, columns = COLUMNAS).set_index('N')
  df.to_excel(Path.cwd().parent / 'ejecuciones.xls')

if __name__ == "__main__":
  obtener_promedios()
  datos_ox1()
  comparacion()

