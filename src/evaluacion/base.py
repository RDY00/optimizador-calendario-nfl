""" Implementa la función para evaluar soluciones de la NFL """

import numpy as np
from temporada import TemporadaNFL
from abc import ABC, abstractmethod

class EvaluacionNFL(ABC):
  """ Define la estructura de las funciones de evaluación para calendarios """

  __slots__ = ("ejemplar", "reglas", "max_eval")

  def __init__(self, ejemplar: TemporadaNFL):
    """
    Parámetros
    ----------
    ejemplar : TemporadaNFL
      Ejemplar para la evaluación
    """
    self.ejemplar = ejemplar
    self.reglas = self.carga_reglas()
    self.max_eval = sum(r.max_eval for r in reglas)

  @abstractmethod
  def carga_reglas(self) -> list:
    """ Define las reglas se que usarán en la evaluación

    Devuelve
    --------
    list : Lista con las reglas para la evaluación
    """
    raise NotImplementedError

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
    return self.max_eval - sum(r(solucion) for r in self._reglas)

