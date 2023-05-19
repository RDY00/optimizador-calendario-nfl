""" Implementación del algoritmo genético """

import numpy as np
import random, time # TODO: Reemplazar random por numpy.random
from tqdm.auto import tqdm
from temporada import temporadaNFL

class AlgoritmoGenetico:
  """ Algoritmo Genético para las N-Reinas """

  # Optimizar accesos
  __slots__ = ("ejemplar", "evalua_solucion", "p_mut_filas", "p_mut_cols",
               "p_cruza_filas", "p_cruza_cols", "poblacion", "tam_poblacion",
               "mejor", "total_eval", "cdf", "semilla", "rng")

  def __init__(self, ejemplar: temporadaNFL) -> None:
    """ Inicializa la instancia para el algoritmo


    Parámetros
    ----------
    ejemplar : temporadaNFL
      Ejemplar para generar las soluciones, representa una temporada
    """
    # Datos ejemplar
    self.ejemplar = ejemplar
    self.evalua_solucion = None
    # Probabilidades
    self.p_mut_filas = 0
    self.p_mut_cols = 0
    self.p_cruza_filas = 0
    self.p_cruza_cols = 0
    # Datos población
    self.poblacion = None
    self.tam_poblacion = 0
    self.mejor = None
    self.total_eval = 0
    self.cdf = None
    # Generador de aleatorios
    self.semilla = None
    self.rng = None

  def solucion_aleatoria(self) -> dict:
    """ Genera una solución aleatoria y la devuelve junto con su evaluación

    Devuelve
    ----------
    dict : Diccionario con las llaves 'solucion' y 'evaluacion'
    """
    
    sol = np.zeros(
      (self.ejemplar.num_equipos,self.ejemplar.num_semanas,2), dtype=np.uint16)

    for i in range(self.ejemplar.num_equipos):
      partidos = np.array(
        self.ejemplar.equipos["partidos"] + [self.ejemplar.bye])
      rng.shuffle(partidos)
      sol[i,:,0] = partidos

    self.repara_solucion(sol)

    for semana in range(self.ejemplar.num_semanas):
      horarios = self.ejemplar.horarios_semana(semana)
      if horarios is not None:
        pass

    return {
      "solucion" : sol,
      "evaluacion" : self.evalua_solucion(sol)
    }

  def repara_solucion(self, solucion: np.ndarray) -> None:
    # Diccionario con el orden de los partidos para tener búsqueda de O(1)
    orden_partidos = [{} for i in range(self.ejemplar.num_equipos)]

    for equipo,juegos in enumerate(solucion):
      for semana,partido in enumerate(juegos):
        orden_partidos[equipo][partido] = semana

    # Reparación desde la fila modificada
    for equipo in range(solucion.shape[0]):
      e = equipo
      for semana,partido in enumerate(solucion[equipo,:,0]):
        s, p = semana, partido
        # Repetimos hasta que no haya más colisiones
        while True:
          # Si es BYE terminamos
          if p == self.ejemplar.bye: break
          # Obtenemos al equipo contra el que se juega en contra (c)
          local = self.ejemplar.partidos[p]["local"]
          visitante = self.ejemplar.partidos[p]["visitante"]
          c = local if local != e else visitante
          # Si el partido está bien posicionado terminamos esta iteración
          if solucion[c,s,0] == p: break
          # Sino, intercambiamos posiciones con el partido mal posicionado (pc)
          pc = solucion[c,s,0] # Partido de la colisión con p
          sc = orden_partidos[c][p] # Semana de la colisión con p
          solucion[c,s,0], solucion[c,sc,0] = solucion[c,sc,0], solucion[c,s,0]
          # Actualizamos valores para la nueva iteración
          e, p, s = c, pc, sc
          assert p != partido, "No debería de tocarse esa fila nunca" # Debug


  def inicializa_poblacion(self) -> None:
    """ Inicializa la poblacion inicial con TAM_POBLACION individuos

    Los inviduos se generan de manera aleatoria y no evitan posibles duplicados
    por lo casos en los que la cantidad posible de individuos es menor al tamaño
    de la población.

    Se almacena el individuo óptimo a parte para la eleccióñ elitista y para
    devolver la solución óptima.
    """
    self.poblacion = [self.solucion_aleatoria() for _ in range(self.tam_poblacion)]
    self.actualzia_datos_generacion()

  def cruza(self, sol1: list, sol2: list) -> tuple:
    """ Aplica el operador de cruza usando Partially Mapped Crossover (PMX)

    PMX es un operador de cruza para permutaciones que asegura que los hijos
    hijos generados también sean permutaciones y respeta posiciones absolutas
    de los valores en los padres

    Parámetros
    ----------
    sol1 : list of int
      Primer padre para la cruza
    sol2 : list of int
      Segundo padre para la cruza

    Devuelve
    --------
    tuple : Tupla con los dos hijos generados
    """
    if random.random() > self.p_cruza:
      return sol1, sol2 # No hay cruza

    hijo1 = sol1[:]
    hijo2 = sol2[:]
    ind1, ind2 = {}, {}

    # Rango que se copia, m < n
    m = random.randrange(self.N-1)
    n = random.randrange(m+1, self.N) + 1

    # Sustituimos la seccion que se mantiene en los hijos
    for i in range(m,n):
      hijo1[i] = sol2[i]
      ind1[sol2[i]] = sol1[i]
      hijo2[i] = sol1[i]
      ind2[sol1[i]] = sol2[i]

    # Corregimos los indices de la izquierda
    for i in range(m):
      while hijo1[i] in ind1:
        hijo1[i] = ind1[hijo1[i]]
      while hijo2[i] in ind2:
        hijo2[i] = ind2[hijo2[i]]

    # Corregimos los indices de la derecha
    for i in range(n,self.N):
      while hijo1[i] in ind1:
        hijo1[i] = ind1[hijo1[i]]
      while hijo2[i] in ind2:
        hijo2[i] = ind2[hijo2[i]]

    return hijo1, hijo2

  def muta(self, solucion: list) -> list:
    """ Muta la solución intercambiando dos de sus índices

    Al mutar de esta manera aseguramos que la solución mutada siga siendo una
    permutación

    Parámetros
    ----------
    solucion : list of int
      Solución a permutar

    Devuelve
    --------
    list of int : Solución permutada
    """
    if random.random() > self.p_mutacion:
      return solucion # No hubo mutacion

    i, j = random.sample(range(self.N), 2)
    sol = solucion[:]
    sol[i], sol[j] = sol[j], sol[i]
    return sol

  def selecciona_padres(self, num_padres: int = 2) -> list:
    """ Selecciona NUM_PADRES padres para la nueva generación

    Utiliza el método de selección por ruleta y obtiene dos índices de la
    población distintos, esto no asegura que los padres sean distintos si
    se permiten repetidos en la población

    Parámetros
    ----------
    num_padres : int
      Número de padres a devolver, por defecto es 2

    Devuelve
    --------
    list of (list of int)
      Lista de los padres obtenidos
    """
    padres_ind = set()
    
    while len(padres_ind) < num_padres:
      val = random.random()
      ind = np.searchsorted(self.cdf, val)
      padres_ind.add(ind)

    return [self.poblacion[i]["solucion"] for i in padres_ind]

  def poblacion_generacional(self) -> None:
    """ Obtiene la nueva población de forma generacional

    Obtiene tantos hijos como sea necesario para llenar la nueva población
    y los muta con probabilidad P_MUTACION, al final la generación anteior
    es reemplazada por la hecha con los hijos.

    Para el paso elitista, el mejor individuo de la población actual pasa a la
    nueva directamente.
    """
    nueva_poblacion = []
    # Paso elitista, el mejor siempre pasa directamente
    nueva_poblacion.append(self.mejor)
    while len(nueva_poblacion) < self.tam_poblacion:
      # Generan hijos por cruza
      h1, h2 = self.cruza(*self.selecciona_padres(2))
      # Mutacion
      h1 = self.muta(h1)
      h2 = self.muta(h2)
      # Agregar
      nueva_poblacion.append({
        "solucion" : h1,
        "evaluacion" : self.evalua_solucion(h1)
      })

      if len(nueva_poblacion) == self.tam_poblacion:
        break # Por si sólo había espacio para un hijo

      nueva_poblacion.append({
        "solucion" : h2,
        "evaluacion" : self.evalua_solucion(h2)
      })
    
    self.poblacion = nueva_poblacion
    self.actualzia_datos_generacion()

  def actualzia_datos_generacion(self):
    """ Actualiza los datos del mejor indivuo y la suma de evaluacion """
    self.mejor = self.poblacion[0]
    self.total_eval = 0
    for v in self.poblacion:
      self.total_eval += v["evaluacion"]
      if v["evaluacion"] > self.mejor["evaluacion"]:
        self.mejor = v
    probs = [v["evaluacion"] / self.total_eval for v in self.poblacion]
    self.cdf = np.cumsum(probs)

  def ejecutar(self, tam_poblacion: int = 50, t_limite: int = 60,
      p_cruza: float = 0.8, p_mutacion: float = 0.1,
      semilla: int = None) -> dict:
    """ Ejecuta el algoritmo genético con los parámetros dados

    El algoritmo termina cuando temrina el tiempo limite o cuando se alcanza
    solución óptima

    Parámetros
    ----------
    tam_poblacion : int
      Tamaño de la población, por defecto es 50
    t_limite : int
      Tiempo en segundo que el algoritmo se ejecutará como máximo.
      Por defecto es 60
    p_cruza : float
      Probabilidad de aplibar el algoritmo de cruza a dos padres.
      Por defecto es 0.8
    p_mutacion : float
      Probabilidad de mutar a cada invidivuo. Por defectto es 0.1
    semilla : int
      Semilla para los valores aleatorios, si no de da se usa time.time()

    Devuelve
    --------
    dic : Diccionario con los datos de la ejecución

    El diccionario contiene las llaves:
    - solucion: la solución encontrada
    - evaluacion: evaluacion de la solucion
    - generacion: Generación en la que se terminó el algoritmo
    - tiempo: Tiempo total que tomó el algoritmo
    - es_optimo: Booleano que dice si la solución es óptima o no
    - optimos: Lista con las mejores evaluaciones por generación
    - promedios: Lista con el promedio de evaluación por generación
    """ 
    self.semilla = semilla if semilla is not None else int(time.time())
    self.rng = np.random.default_rng(semilla)
    self.evalua_solucion = lambda _: 0

    # self.p_cruza = p_cruza
    # self.p_mutacion = p_mutacion
    self.tam_poblacion = tam_poblacion

    optimos = []
    promedios = []

    t_inicio = time.time()
    timeout = t_inicio + t_limite
    generacion = 0

    self.inicializa_poblacion()

    optimos.append(self.mejor["evaluacion"])
    promedios.append(self.total_eval / self.tam_poblacion)

    t_actual = time.time()
        
    # with tqdm(total=t_limite, unit_scale=True) as bar:
    with tqdm(desc="Generación", unit="") as bar:
      while t_actual < timeout and self.mejor["evaluacion"] != self.max_eval:
        self.poblacion_generacional()
        generacion += 1
        # Datos estadisticos
        optimos.append(self.mejor["evaluacion"])
        promedios.append(self.total_eval / self.tam_poblacion)
        # tn_actual = time.time()
        # bar.update(tn_actual - t_actual)
        # t_actual = tn_actual
        t_actual = time.time()
        bar.update(1)

    t_total = t_actual - t_inicio

    return {
      "tiempo" : t_total,
      "es_optimo" : self.mejor["evaluacion"] == self.max_eval,
      "generacion" : generacion,
      "solucion" : self.mejor["solucion"],
      "evaluacion" : self.mejor["evaluacion"],
      "optimos" : optimos,
      "promedios" : promedios 
    }

