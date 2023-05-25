""" Modulo que implementa la ejecución para obtención de datos """

import json
from pathlib import Path
from genetico import AlgoritmoGenetico
from temporada import TemporadaNFL
from evaluacion.evaluacion2023 import EvaluacionNFL2023
import numpy as np

ITERACIONES = 1
VALORES = range(8,21)
P_MUTACION = 0.1
P_CRUZA = 0.8
TAM_POBLACION = 50
T_LIMITE = 3600 * 2 # segundos
MUESTRA_CADA = 1000
GRAFICA_CADA = 1000

# Las semillas estás fijas, se pueden volver aleatorias quitando el 42 (semilla)
SEMILLAS = np.random.default_rng(42).integers(32767, size=ITERACIONES)

RUTA = Path.cwd() / "data"
RUTA.mkdir(exist_ok=True)

def guardar_datos() -> None:
  """ Ejecuta los algoritmos el número de iteaciones determinado 

  Parámetros
  ----------
  Algoritmo: AlgoritmoGenetico
    Instancia del algoritmo a utilizar
  nombre: Callable
    Función que determina el nombre de los archivos con respecto al ejemplar
    y la ejecución
  """
  temporada = TemporadaNFL.leer_archivo("../data/temporada2023.txt")
  evaluacion = EvaluacionNFL2023(temporada)
  problema = AlgoritmoGenetico(temporada, evaluacion)
  for i in range(ITERACIONES):
    resultado = problema.ejecutar(
      TAM_POBLACION, T_LIMITE, P_CRUZA, P_MUTACION, SEMILLAS[i],
      MUESTRA_CADA, GRAFICA_CADA)
    resultado["solucion"] = list(map(int, resultado["solucion"].flatten()))
    with open(RUTA / f"ejecucuion_{i}.json", "w") as f:
      json.dump(resultado, f, indent=2)
    print(f"Datos del ejemplar {i} guardados UwU", end="\n\n")
    
if __name__ == "__main__":
  print("Semillas:", list(SEMILLAS), end="\n\n")
  guardar_datos()
  print(f"Datos guardados en {RUTA}")

