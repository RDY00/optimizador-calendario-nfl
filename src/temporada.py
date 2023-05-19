""" Representa ejemplares para el algoritmo de optimización """

class temporadaNFL:
  """ Describe los datos de una temporada de la NFL """

  # Para optimizar la velocidad de acceso a los atributos
  __slots__ = ("equipos", "partidos", "estadios", "navidad", "thanksgiving")

  def __init__(self, equipos: tuple, partidos: tuple, estadios: tuple,
      navidad: tuple, thanksgiving: int):
    """ Constructor a partir de los datos

    Parámetros
    ----------
    equipos : tuple
      Tupla de los equipos que jugarán la temporada en forma de diccionarios
    partidos : tuple 
      Tupla de los partidos que se jugarán la temporada en forma de diccionarios
    estadios : tuple 
      Tupla de los estadios que serán usados en la temporada como diccionarios
    navidad : tuple
      Tupla (semana de navidad, día de navidad) para la temporada
    thanksgiving : int
      Semana de la temporada correspondiente al día de acción de gracias
    """
    self.equipos = equipos
    self.partidos = partidos
    self.estadios = estadios
    self.navidad = navidad
    self.thanksgiving = thanksgiving

  @classmethod
  def leer_archivo(cls, archivo):
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
    return None # return cls(los parametros en orden)

