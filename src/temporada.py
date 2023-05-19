""" Representa ejemplares para el algoritmo de optimización """

class temporadaNFL:
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
  def leer_archivo(cls, archivo: "Path") -> "temporadaNFL":
    """ Construye una clase desde el archivo txt

    Parámetros
    ----------
    archivo : str or Path
      Ruta al archivo que se leerá

    Devuelve
    --------
    temporadaNFL : Objeto con los datos de la temporada leidos
    """
    # TODO: Terminar esto
    # NOTAS IMPORTANTES:
    # Las listas de partidos por equipo deben de ser tuplas o van a dar problemas
    return None # return cls(los parametros en orden)
  
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
      return None

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

