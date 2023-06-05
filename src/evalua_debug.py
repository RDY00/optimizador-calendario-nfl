import sys
from temporada import TemporadaNFL
from evaluacion.evaluacion2023 import EvaluacionNFL2023

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print(f"USO: {sys.argv[0]} EJEMPLAR SOLUCION")

  temporada = TemporadaNFL.leer_archivo(sys.argv[1])
  solucion = temporada.leer_solucion(sys.argv[2])
  if temporada.verifica_factibilidad(solucion):
    print("Todo bien c:")

