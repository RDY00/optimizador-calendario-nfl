import numpy as np
from temporada import TemporadaNFL
from evaluacion.reglas.regla import Regla

class HorarioFactible(Regla):
  """ Verifica que el horarios sea factible/válido """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)
    self.factor = 100

  @property
  def max_val(self) -> int:
    return self.factor * len(self.ejemplar.partidos)

  def evalua(self, solucion: np.ndarray) -> int:
    partidos_mal = set()
    for semana in range(self.ejemplar.num_semanas):
      partidos = set(solucion[:,semana,0])
      for partido in partidos:
        if partido == self.ejemplar.bye: continue
        local = self.ejemplar.partidos[partido]["local"]
        visitante = self.ejemplar.partidos[partido]["visitante"]
        if solucion[local,semana,0] != partido or \
            solucion[visitante,semana,0] != partido:
          partidos_mal.add(partido)
    return self.factor * len(partidos_mal)

class PartidosTDAY(Regla):
  """ Revisa que DET y DAL juegen en acción de gracias """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)
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

class NoMasDeSeisEstelares(Regla):
  """ Penaliza por equipos con más de 6 horarios estelares """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_equipos
    
  def evalua(self, solucion: np.ndarray) -> int:
    return sum(1 for partidos in solucion if sum(partidos[:,1] != self.ejemplar.horarios["NONE"]) > 6)

class NoCuatroJuegosFuera(Regla):
  """ Penaliza equipos con cuatro o más juegos como visitante consecutivos """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_equipos * 6
    
  def evalua(self, solucion: np.ndarray) -> int:
    penalizacion = 0
    for equipo, partidos in enumerate(solucion):
      cont_equipo = 0
      for partido, _ in partidos:
        if partido == self.ejemplar.bye or \
            self.ejemplar.partidos[partido]["local"] == equipo:
          if cont_equipo >= 4:
            penalizacion += cont_equipo - 3
          cont_equipo = 0
        else:
          cont_equipo += 1
    return penalizacion
  
class ByeEnSemanasValidas(Regla):
  """ Penaliza equipos con byes en semanas invalidas """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_equipos
    
  def evalua(self, solucion: np.ndarray) -> int:
    penalizacion = 0
    for partidos in solucion:
      for semana, (partido, _) in enumerate(partidos):
        if (semana < 4 or semana > 13) and partido == self.ejemplar.bye:
          penalizacion += 1
    return penalizacion

class NoMasDeSeisByes(Regla):
  """ Penaliza semana con más de seis byes """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_semanas
    
  def evalua(self, solucion: np.ndarray) -> int:
    penalizacion = 0
    for semana in range(self.ejemplar.num_semanas):
      partidos, counts = np.unique(solucion[:,semana,0], return_counts=True)
      if partidos[-1] == self.ejemplar.bye and counts[-1] > 6:
        penalizacion += 1
    return penalizacion

class NoEstelaresEnBye(Regla):
  """ Penaliza equipos con byes en semanas invalidas """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return 16 * 3 + 12

  def evalua(self, solucion: np.ndarray) -> int:
    penalizacion = 0
    for partidos in solucion:
      for partido, horario in partidos:
        if partido == self.ejemplar.bye and horario != self.ejemplar.horarios["NONE"]:
          penalizacion += 1
    return penalizacion

