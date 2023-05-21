""" Representa ejemplares para el algoritmo de optimización """

class TemporadaNFL:
  """ Describe los datos de una temporada de la NFL """

  # Para optimizar la velocidad de acceso a los atributos
  __slots__ = ("num_equipos", "num_semanas", "equipos", "partidos",
               "estadios", "navidad", "thanksgiving", "horarios",
               "semanas_sin_horario", "bye")

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
    nombres_horarios = {"NONE", "MNF", "TNF", "SNF", "XMAS", "TDAY"}
    self.horarios = {k:v for v,k in enumerate(nombres_horarios)}
    self.semanas_sin_horario = (14,17) # Indexada desde 0
    self.bye = len(partidos)

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
    p = []
    e = []
    q = []
    indice = 0
    for i in range(len(info)):
      if(info[i] == "\n"):
        indice = i + 1
        break
      s = info[i].split()
      partido = {
        "id" : int(s[0]),
        "local" : int(s[1]),
        "visitante" : int(s[2]),
        "estadio" : int(s[3]),
        "interes" : int(s[4])
      }
      p.append(partido)
      
    for i in range(indice, len(info)):
      if(info[i] == "\n"):
        indice = i + 1
        break
      s = info[i].split()
      estadio = {
        "id" : int(s[0]),
        "huso" : s[1]
      }
      e.append(estadio)
    
    for i in range(indice, len(info), 2):
      if(info[i] == "\n"):
        indice = i + 1
        break
      s = info[i].split()
      lista = list(map(int, info[i+1].split()))
      equipo = {
        "id" : int(s[0]),
        "nombre" : s[1],
        "conferencia" : s[2],
        "division" : s[3],
        "bye_pasado" : s[4],
        "3_consecutivos" : s[5],
        "oponentes" : lista
      }
      q.append(equipo)
    
    s = info[i].split()
    partidos = tuple(p)
    estadios = tuple(e)
    equipos = tuple(q)
    thanksgiving = int(s[0])
    navidad = (int(s[1]), s[2])
    # return [partidos, estadios, equipos, thanksgiving, navidad]
    num_semanas = 18
    return cls(num_semana, equipos, partidos, estadios, navidad, thanksgiving)
  
  def get_partidos(info, indice):
    p = []
    fin = indice
    for i in range(indice, len(info)):
      if(info[i] == "\n"):
        fin = i + 1
        break
      s = info[i].split()
      partido = {
          "id" : int(s[0]),
          "local" : int(s[1]),
          "visitante" : int(s[2]),
          "estadio" : int(s[3]),
          "interes" : int(s[4])
      }
      p.append(partido)
    return fin, p
  
  def get_estadios(info, indice):
    fin = indice
    e = []
    for i in range(indice, len(info)):
      if(info[i] == "\n"):
        fin = i + 1
        break
      s = info[i].split()
      estadio = {
          "id" : int(s[0]),
          "huso" : s[1]
      }
      e.append(estadio)
    return fin, e

  def get_equipos(info, indice):
    fin = indice
    q = []
    for i in range(indice, len(info), 2):
      if(info[i] == "\n"):
        fin = i + 1
        break
      s = info[i].split()
      lista = list(map(int, info[i+1].split()))
      equipo = {
          "id" : int(s[0]),
          "nombre" : s[1],
          "conferencia" : s[2],
          "division" : s[3],
          "bye_pasado" : s[4],
          "3_consecutivos" : s[5],
          "oponentes" : lista
      }
      q.append(equipo)
    return fin, q
  
  
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

    return horarios

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

