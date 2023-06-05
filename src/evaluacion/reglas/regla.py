from temporada import TemporadaNFL
import numpy as np
from abc import ABC, abstractmethod, abstractproperty

class Regla(ABC):
  """ Define la estructura de una regla para evaluar calendarios """
  def __init__(self, ejemplar: TemporadaNFL, es_dura: bool) -> None:
    """
    Parámetros
    ----------
    ejemplar : TemporadaNFL
      Ejemplar para tener contexto en las evaluaciones
    es_dura : bool
      Determina si la regla es dura o no (es blanda)
    """
    self.ejemplar = ejemplar
    self.es_dura = es_dura
    self.penalizacion = 100

  @property
  def max_eval(self) -> int:
    """ Devuelve la máxima evaluación que la regla puede dar 

    El valor no tiene que ser exacto, solo mayor al conocido
    Aplica una penalización a las reglas duras para que sean peores que las
    blandas

    Devuelve    
    --------    
    int : Valor máximo de la regla
    """
    return self.max_val * self.penalizacion if self.es_dura else self.max_val

  @abstractproperty
  def max_val(self) -> int:
    """ Devuelve la máxima evaluación que la regla puede dar

    El valor no tiene que ser exacto, solo mayor al conocido
    blandas

    Devuelve
    --------
    int : Valor máximo de la regla
    """
    raise NotImplementedError

  def __call__(self, solucion: np.ndarray) -> int:
    """ Evalua la solucion y aplica la penalización necesario a reglas duras

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a evaluar

    Devuelve
    --------
    int : Evaluación
    """
    e = self.evalua(solucion)
    return e * self.penalizacion if self.es_dura else e

  @abstractmethod
  def evalua(self, solucion: np.ndarray) -> int:
    """ Evalua la solucion en base a la regla

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a evaluar

    Devuelve
    --------
    int : Evaluación
    """
    raise NotImplementedError

  @property
  def nombre(self) -> str:
    """ Devuelve el nombre de la regla (el de su clase) """
    return self.__class__.__name__

