""" Implementa la función para evaluar soluciones de la NFL """

import numpy as np
from temporada import TemporadaNFL
from evaluacion.evaluacion import EvaluacionNFL
from evaluacion.reglas.duras import *
from evaluacion.reglas.blandas import *

class EvaluacionNFL2023(EvaluacionNFL):
  """ Define la estructura de las funciones de evaluación para calendarios 2023 """
  def __init__(self, ejemplar: TemporadaNFL):
    super().__init__(ejemplar)

  def carga_reglas(self):
    return [r(self.ejemplar) for r in [
      # Duras
      HorarioFactible,
      PartidosTDAY,
      NoMasDeSeisEstelares,
      NoCuatroJuegosFuera,
      ByeEnSemanasValidas,
      NoMasDeSeisByes,
      NoEstelaresEnBye,
      #Blandas
      NoTresJuegosFuera,
      CalificacionHorarios,
      TodosHorarioEstelar,
      NoByesTempranosConsecutivos,
      JuegosDivisionalesAlFinal,
      NoMasDeDosHusosParaTNF
    ]]

