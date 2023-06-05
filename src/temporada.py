""" Representa ejemplares para el algoritmo de optimización """

import numpy as np

class TemporadaNFL:
  """ Describe los datos de una temporada de la NFL """

  # Para optimizar la velocidad de acceso a los atributos
  __slots__ = ("num_equipos", "num_semanas", "equipos", "partidos",
               "estadios", "navidad", "thanksgiving", "horarios",
               "semanas_sin_horario", "bye", "max_calif_partido")

  def __init__(self, num_semanas: int, equipos: tuple, partidos: tuple,
      estadios: tuple, navidad: tuple, thanksgiving: int) -> None:
    """ Constructor a partir de los datos

    Parámetros
    ----------
    num_semanas : int
      Número de semanas de la temporada
    equipos : tuple
      Tupla de los equipos que jugarán la temporada en forma de diccionarios
    partidos : tuple 
      Tupla de los partidos que se jugarán la temporada en forma de diccionarios
    estadios : tuple 
      Tupla de los estadios que serán usados en la temporada como diccionarios
    navidad : tuple
      Tupla (semana de navidad, día de navidad) para la temporada
      - La semana indexada desde 0
      - El dia puede ser: L, M, X, J, V, S, D
    thanksgiving : int
      Semana de la temporada correspondiente al día de acción de gracias
      indexada desde 0

    IMPORTANTE: El índice en la tupla equivale a su ID
    """
    self.num_equipos = len(equipos)
    self.num_semanas = num_semanas
    self.equipos = equipos
    self.partidos = partidos
    self.estadios = estadios
    self.navidad = navidad
    self.thanksgiving = thanksgiving
    # NONE - Horario normal / no definido
    # {M,T,S}NF - {Monday,Thursday,Sunday} Night Football
    # XMAS - Christmas
    # TDAY - Thanksgiving
    nombres_horarios = ("NONE", "MNF", "TNF", "SNF", "XMAS", "TDAY")
    self.horarios = {k:v for v,k in enumerate(nombres_horarios)}
    self.semanas_sin_horario = (14,17) # Indexada desde 0
    self.bye = len(partidos)
    self.max_calif_partido = max(
      partidos, key=lambda x: x["calificacion"])["calificacion"]

  @classmethod
  def leer_archivo(cls, archivo: "Path") -> "TemporadaNFL":
    """ Construye una clase desde el archivo txt

    Parámetros
    ----------
    archivo : str or Path
      Ruta al archivo que se leerá

    Devuelve
    --------
    TemporadaNFL : Objeto con los datos de la temporada leidos
    """
    with open(archivo) as data:
      info = data.readlines()

    p, e, q = [], [], []
    i = 0
    
    while info[i] != "\n":
      s = info[i].split()
      equipo = {
        # "id" : int(s[0]),
        "acronimo" : s[1],
        "conferencia" : s[2],
        "division" : s[3],
        "bye_anterior" : int(s[4]),
        "3_consecutivos" : bool(s[5]),
        "partidos" : []
      }
      q.append(equipo)
      i += 1

    i += 1
    while info[i] != "\n":
      s = info[i].split()
      estadio = {
        # "id" : int(s[0]),
        "huso" : s[1]
      }
      e.append(estadio)
      i += 1

    i += 1
    while info[i] != "\n":
      s = info[i].split()
      id_partido = int(s[0])
      local = int(s[1])
      visitante = int(s[2])
      partido = {
        # "id" : id_partido,
        "local" : local,
        "visitante" : visitante,
        "estadio" : int(s[3]),
        "calificacion" : int(s[4])
      }
      p.append(partido)
      q[local]["partidos"].append(id_partido)
      q[visitante]["partidos"].append(id_partido)
      i += 1
    
    partidos = tuple(p)
    estadios = tuple(e)
    equipos = tuple(q)
    thanksgiving = int(info[i+1])
    s = info[i+2].split()
    navidad = (int(s[0]), s[1])
    num_semanas = 18
    return cls(num_semanas, equipos, partidos, estadios, navidad, thanksgiving)

  def guardar_solucion(self, solucion: str) -> str:  
    return " ".join(map(str, solucion.flatten()))

  def leer_solucion(self, archivo: str) -> np.ndarray:  
    with open(archivo) as f:
      a = list(map(int, f.read().split()))
    return np.array(a, dtype=int).reshape(
      (self.num_equipos, self.num_semanas, -1))
  
  def horarios_semana(self, semana: int) -> list:
    """ Devuelve la lista de horarios codificados de la semana

    Parámetros
    ----------
    semana : int
      Semana de la temporada
  
    Devuelve
    --------
    list of int : Lista de horarios codificados de la semana
    """
    horarios = ["MNF", "TNF", "SNF"]

    # Semanas con horarios no predefinidos
    if semana in self.semanas_sin_horario:
      return []

    # No hay TNF, pero hay 3 de TDAY
    if semana == self.thanksgiving:
      horarios = ["MNF", "SNF"] + ["TDAY"]*3

    # Hay 3 horarios de XMAS
    if semana == self.navidad[0]:
      # Se agregan partidos al sabado
      if self.navidad[1] == "S":
        horarios += ["XMAS"]*3
      # No hay SNF
      if self.navidad[1] == "D":
        horarios = ["MNF", "TNF"] + ["XMAS"]*3
      # No hay ni SNF ni MDF
      if self.navidad[1] == "L":
        horarios = ["TNF"] + ["XMAS"]*3

    return [self.horarios[v] for v in horarios]

  def verifica_solucion(self, solucion: np.ndarray) -> bool:
    """ Verifica que una solución sea válida

    Se considera válida una solución que cumple:
    * La fila i es una permutación de los 17 partidos y el BYE del equipo i.
    * La columnas j es una permutación de los posibles horarios de la semana
      j+1 y todos los horarios aparecen en pares.

    ESTA FUNCIÓN ES PARA PRUEBAS, NO SE USA EN EL ALGORITMO

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a verificar

    Devuelve
    bool : True si la solución es correcta, False en otro caso
    """
    bien = True
    for equipo, partidos in enumerate(solucion[:,:,0]):
      ps1 = np.sort(partidos)
      ps2 = np.sort(self.equipos[equipo]["partidos"] + [self.bye])
      if np.any(ps1 != ps2):
        print(f"Error equipo = {equipo} ps1 = {ps1} ps2 = {ps2}")
        bien = False

    for semana in range(self.num_semanas):
      horarios = self.horarios_semana(semana) * 2
      horarios += [self.horarios["NONE"]] * \
                    (self.num_equipos - len(horarios))
      hs1 = np.sort(horarios)
      hs2 = np.sort(solucion[:,semana,1])
      if np.any(hs1 != hs2):
        print(f"Error semana = {semana} hs1 = {hs1} hs2 = {hs2}")
        bien = False

    return bien

  def verifica_factibilidad(self, solucion: np.ndarray):
    if not self.verifica_solucion(solucion):
      return False

    res = True
    
    for equipo, partidos in enumerate(solucion):
      for semana, (partido, horario) in enumerate(partidos):
        if partido == self.bye: continue
        contra = self.equipo_contra(equipo, partido)
        partido_contra = solucion[contra,semana,0]
        horario_contra = solucion[contra,semana,1]
        if partido_contra != partido:
          res = False
          print(f"Error en semana {semana}",
                f"en equipos {equipo} y {contra}",
                f"con los partidos {partido} y {partido_contra}")
        elif horario != horario_contra:
          res = False
          print(f"Error en semana {semana}",
                f"en equipos {equipo} y {contra}",
                f"con el partido {partido}",
                f"por los horarios {horario} {horario_contra}")

    return res


  def equipo_contra(self, equipo: int, partido: int) -> int:
    """ Devuelve el equipo contrario de un partido

    Parámetro
    ---------
    equipo : int
      Equipo del que se busca su oponente
    partido : int
      Partido a revisar, EQUIPO debe de ser uno de que lo juegan

    Devuelve
    --------
    int : Equipo contra el que juega EQUIPO en PARTIDO
    """
    if partido == self.bye: return None
    local = self.partidos[partido]["local"]
    visitante = self.partidos[partido]["visitante"]
    return local if local != equipo else visitante

