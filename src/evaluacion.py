""" Implementa la función para evaluar soluciones de la NFL """

import numpy as np
from temporada import TemporadaNFL
from abc import ABC

class EvaluacionNFL(ABC):
  """ Define la estructura de las funciones de evaluación para calendarios """

  __slots__ = ("ejemplar", "reglas")

  def __init__(self, ejemplar: TemporadaNFL):
    self.ejemplar = ejemplar
    self.reglas = []
    self.max_eval = 0
    self.carga_reglas()

  @abstractmethod
  def carga_reglas(self):
    pass

  def __call__(self, solucion: np.ndarray) -> int:
    """ Evalúa una solución codificada dada

    Parámetros
    ----------
    solucion : np.ndarray
      Solución codificada a evaluar

    Devuelve
    --------
    int : Evaluacion obtenida según las reglas de la función
    """
    return self.max_eval - sum(r(solucion) for r in self.reglas)

