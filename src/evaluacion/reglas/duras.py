from regla import Regla
from temporada import TemporadaNFL
import numpy as np

class PartidosTDAY(Regla):
  """ Revisa que DET y DAL juegen en acción de gracias """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, False)
    for ind, equipo in enumerate(self.ejemplar.equipos):
      if equipo["acronimo"] == "DET":
        self.det = ind
      elif equipo["acronimo"] == "DAL":
        self.dal = ind

  @property
  def max_val(self) -> int:
    return 2

  def evalua(self, solucion: np.ndarray) -> int:
    tday = self.ejemplar.thanksgiving
    return sum(1 if h == self.ejemplar.horarios["TDAY"] else 0
               for h in (solucion[self.dal,tday,1], solucion[self.det,tday,0]))

