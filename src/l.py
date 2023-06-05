
import json
from pathlib import Path
from genetico import AlgoritmoGenetico
from temporada import TemporadaNFL
from evaluacion.evaluacion2023 import EvaluacionNFL2023
import numpy as np
import matplotlib.pyplot as plt
import sys

with open(sys.argv[1]) as f:
  datos = json.load(f)

datos["solucion"] = np.array(datos["solucion"], dtype=int).reshape((32,18,2))

print("Solución:\n")
print(datos["solucion"][:,:,0],end="\n\n")
print(datos["solucion"][:,:,1])

temporada = TemporadaNFL.leer_archivo("../data/temporada2023.txt")
elv = EvaluacionNFL2023(temporada)

print("\nOptimo:", elv.max_eval)
print("\nEvaluación:", datos["evaluacion"])

print("Análisis:\n")
print(elv.analiza_solucion(datos["solucion"]))

with open(sys.argv[2], "a") as f:
  f.write(temporada.guardar_solucion(datos["solucion"]))

fig, ax = plt.subplots()
ax.plot(datos["optimos"])
ax.set_title("Evaluación del valor óptimo")
ax.set_ylabel("Evaluación")
ax.set_xlabel("Generación")
fig.savefig("grafia.png", bbox_inches="tight")

