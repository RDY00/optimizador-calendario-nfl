import numpy as np
from temporada import TemporadaNFL
from evaluacion.reglas.regla import Regla

class NoTresJuegosFuera(Regla):
  """ Penaliza equipos con tres juegos como visitante consecutivos """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, False)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_equipos
    
  def evalua(self, solucion: np.ndarray) -> int:
    penalizacion = 0
    for equipo, partidos in enumerate(solucion):
      cont_equipo = 0
      for partido, _ in partidos:
        if partido == self.ejemplar.bye or \
            self.ejemplar.partidos[partido]["local"] == equipo:
          if cont_equipo >= 3:
            penalizacion += cont_equipo - 2
          cont_equipo = 0
        else:
          cont_equipo += 1
    return penalizacion
    
class CalificacionHorarios(Regla):
  """ Evalua la calificación de partidos en  horarios estelares """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, False)
  
  @property
  def max_val(self) -> int:
    return self.ejemplar.max_calif_partido * (16 * 3 + 12)
    
  def evalua(self, solucion: np.ndarray) -> int:
    return self.max_val - sum(
      self.ejemplar.partidos[partido]["calificacion"] 
      for partidos in solucion
      for partido, horario in partidos
      if horario != self.ejemplar.horarios["NONE"] and \
        partido != self.ejemplar.bye
    )

class TodosHorarioEstelar(Regla):
  """ Penaliza por equipos sin horario estelar """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, False)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_equipos
    
  def evalua(self, solucion: np.ndarray) -> int:
    return sum(1 for partidos in solucion if np.all(partidos[:,1] == self.ejemplar.horarios["NONE"]))
    
class NoByesTempranosConsecutivos(Regla):
  """ Penaliza por equipos con dos byes  tempranos seguidos """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return self.ejemplar.num_equipos
    
  def evalua(self, solucion: np.ndarray) -> int:
    return sum(
      1 for equipo, partidos in enumerate(solucion)
      if np.any(partidos[:,:9] == self.ejemplar.bye)
      and self.ejemplar.equipos[equipo]["bye_anterior"] < 9
    )
      
class JuegosDivisionalesAlFinal(Regla):
  """ Penaliza por juegos divisionales al inicio de temporada """
  def __init__(self, ejemplar: TemporadaNFL) -> None:
    super().__init__(ejemplar, True)

  @property
  def max_val(self) -> int:
    return (self.ejemplar.num_equipos * self.ejemplar.num_semanas) // 4
    
  def evalua(self, solucion: np.ndarray) -> int:
    penalizacion = 0
    for semana in range(9):
      partidos = set(solucion[:,semana,0])
      partidos.discard(self.ejemplar.bye)
      for partido in partidos:
        dl = self.ejemplar.equipos[
          self.ejemplar.partidos[partido]["local"]]["division"]
        dv = self.ejemplar.equipos[self.ejemplar.partidos[
          partido]["visitante"]]["division"]
      if dl == dv: penalizacion += 1
    return penalizacion

