""" Implementación del algoritmo genético """

import numpy as np
import time
from tqdm.auto import tqdm
from temporada import TemporadaNFL
from evaluacion.evaluacion import EvaluacionNFL

class AlgoritmoGenetico:
  """ Algoritmo Genético para las N-Reinas """

  # Optimizar accesos
  __slots__ = ("ejemplar", "evalua_solucion", "p_cruza", "p_mutacion",
               "poblacion", "tam_poblacion", "mejor", "total_eval", "cdf",
               "semilla", "rng", "max_eval")

  def __init__(self, ejemplar: TemporadaNFL,
      fun_evaluacion: EvaluacionNFL) -> None:
    """ Inicializa la instancia para el algoritmo

    Parámetros
    ----------
    ejemplar : TemporadaNFL
      Ejemplar para generar las soluciones, representa una temporada
    fun_evaluacion : EvaluacionNFL
      Función de evaluación de las soluciones
    """
    # Datos ejemplar
    self.ejemplar = ejemplar
    self.evalua_solucion = fun_evaluacion
    # Probabilidades
    self.p_cruza = 0
    self.p_mutacion = 0
    # Datos población
    self.poblacion = None
    self.tam_poblacion = 0
    self.mejor = None
    self.total_eval = 0
    self.max_eval = fun_evaluacion.max_eval
    self.cdf = None
    # Generador de aleatorios
    self.semilla = None
    self.rng = None

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

  def solucion_aleatoria(self) -> dict:
    """ Genera una solución aleatoria y la devuelve junto con su evaluación

    Devuelve
    ----------
    dict : Diccionario con las llaves 'solucion' y 'evaluacion'
    """
    sol = np.zeros(
      (self.ejemplar.num_equipos,self.ejemplar.num_semanas,2), dtype=int)

    # Rellenamos filas aleatoriamente
    for equipo in range(self.ejemplar.num_equipos):
      partidos = np.array(
        self.ejemplar.equipos[equipo]["partidos"] + [self.ejemplar.bye])
      self.rng.shuffle(partidos)
      sol[equipo,:,0] = partidos

    self.repara_filas(sol)

    # Rellenamos columnas
    for semana in range(self.ejemplar.num_semanas):
      # Horarios esterales de la semana aleatorios
      horarios = self.ejemplar.horarios_semana(semana) * 2
      horarios += [self.ejemplar.horarios["NONE"]] * \
                    (self.ejemplar.num_equipos - len(horarios))
      self.rng.shuffle(horarios)
      sol[:,semana,1] = horarios

    self.repara_columnas(sol)

    return {
      "solucion" : sol,
      "evaluacion" : self.evalua_solucion(sol)
    }

  def repara_filas(self, solucion: np.ndarray) -> None:
    """ Repara la solucion tanto como sea posible en los equipos

    Recorre todas las filas de arriba a abajo para asegurarse de la mayoría
    de los partidos estén correctamente marcado en ambos equipos que los juegan.

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a reparar
    """
    # Diccionario para tener acceso O(1)
    orden_partidos = [{} for i in range(self.ejemplar.num_equipos)]

    for equipo, juegos in enumerate(solucion):
      for semana, (partido, _) in enumerate(juegos):
        orden_partidos[equipo][partido] = semana

    for _ in range(3):
      for equipo, partidos in enumerate(solucion):
        for semana, (partido, _) in enumerate(partidos):
          contra = self.ejemplar.equipo_contra(equipo, partido)
          if contra == None: continue
          partido_contra = solucion[contra,semana,0]
          if partido_contra == partido: continue
          semana_contra = orden_partidos[contra][partido]
          solucion[contra,semana,0] = partido
          solucion[contra,semana_contra,0] = partido_contra
          orden_partidos[contra][partido] = semana
          orden_partidos[contra][partido_contra] = semana_contra

  def repara_columnas(self, solucion: np.ndarray) -> None:
    """ Repara la solucion tanto como sea posible en los horarios

    Recorre todas las columnas para asegurase de que, en donde los partidos
    están bien posicionados, se compartan los horarios.

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a reparar
    """
    for semana in range(solucion.shape[1]):
      # Cache para los horarios de la semana
      horarios_cache = {}
      for equipo in range(solucion.shape[0]):
        h = solucion[equipo,semana,1]
        if h in horarios_cache:
          horarios_cache[h].add(equipo)
        else:
          horarios_cache[h] = {equipo}

      for equipo in range(solucion.shape[0]):
        partido = solucion[equipo,semana,0]
        contra = self.ejemplar.equipo_contra(equipo, partido)
        if contra == None: continue
        partido_contra = solucion[contra,semana,0]
        if partido != partido_contra: continue
        h1 = solucion[equipo,semana,1]
        h2 = solucion[contra,semana,1]
        if h1 == h2: continue
        horarios_cache[h1].discard(equipo)
        horarios_cache[h2].discard(contra)
        cambio = horarios_cache[h1].pop()
        horarios_cache[h2].add(cambio)
        solucion[contra,semana,1] = h1
        solucion[cambio,semana,1] = h2

  def cruza_filas(self, sol1: np.ndarray, sol2: np.ndarray) -> tuple:
    """ Aplica cruza por filas entre los padres
    
    Para un hijo se toma una sección de filas de uno de los padres y se copia,
    el resto se copia del otro padre. Los horarios no requieren arreglos, para
    las filas se utiliza PXM como algoritmo de cruza.

    Parámetros
    ----------
    sol1 : np.ndarray
      Primer padre para el cruce
    sol2 : np.ndarray
      Segundo padre para el cruce

    Devuelve
    --------
    tuple : Tupla con los dos hijos generados
    """
    limite = self.ejemplar.num_equipos
    # Rango que se copia, m < n
    m = self.rng.integers(limite-1)
    n = self.rng.integers(m+1, limite) + 1

    hijo1 = sol1.copy()
    hijo2 = sol2.copy()

    # Copiamos todas esas filas
    hijo1[m:n,:,0] = sol2[m:n,:,0]
    hijo2[m:n,:,0] = sol1[m:n,:,0]

    # False de reparación
    self.repara_filas(hijo1)
    self.repara_filas(hijo2)
    self.repara_columnas(hijo1)
    self.repara_columnas(hijo2)

    return hijo1, hijo2

  def muta_filas(self, solucion: np.ndarray) -> np.ndarray:
    """ Muta una solución por filas

    Intercambia dos partidos de un equipo aleatorios de semana, luego repara la
    solución.

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a mutar
    """
    equipo = self.rng.integers(solucion.shape[0])
    semanas = self.rng.integers(0, solucion.shape[1], 2)
    
    solucion[equipo,semanas[0],0], solucion[equipo,semanas[1],0] = \
      solucion[equipo,semanas[1],0], solucion[equipo,semanas[0],0]

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
      val = self.rng.random()
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
      h1, h2 = self.selecciona_padres(2)
      
      # Cruza
      if self.rng.random() < self.p_cruza:
        h1, h2 = self.cruza_filas(h1,h2)

      # Mutación
      if self.rng.random() < self.p_mutacion:
        self.muta_filas(h1)
        self.muta_filas(h2)

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
      p_cruza: float = 0.8, p_mutacion: float = 0.01, semilla: int = None,
      muestra_cada: int = 100, grafica_cada: int = 100) -> dict:
    """ Ejecuta el algoritmo genético con los parámetros dados

    El algoritmo termina cuando termina el tiempo limite o cuando se alcanza
    alguna solución óptima.

    Parámetros
    ----------
    tam_poblacion : int
      Tamaño de la población, por defecto es 50
    t_limite : int
      Tiempo en segundo que el algoritmo se ejecutará como máximo.
      Por defecto es 60
    p_cruza : float
      Probabilidad de aplicar el operador de cruza a dos padres.
      Por defecto es 0.9
    p_mutacion : float
      Probabilidad de mutar a cada invidivuo. Por defectto es 0.01
    semilla : int
      Semilla para los valores aleatorios, si es None se usa time.time().
      Por defecto es None.
    muestra_cada : int
      Determinada cada cuántas generaciones se muestra el avance en pantalla.
    grafica_cada : int
      Determinada cada cuántas generaciones se almacenan los datos para graficar,
      lo hacemos asi para evitar sobrecargar de información.

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

    self.p_cruza = p_cruza
    self.p_mutacion = p_mutacion
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

    with tqdm(desc="Generación", unit="") as bar:
      while t_actual < timeout and self.mejor["evaluacion"] != self.max_eval:
        self.poblacion_generacional()
        generacion += 1
        # Datos estadisticos
        if generacion % grafica_cada == 0:
          optimos.append(self.mejor["evaluacion"])
          promedios.append(self.total_eval / self.tam_poblacion)
        if generacion % muestra_cada == 0:
            print(f" Generacion: {generacion}",
                  f"Evaluacion: {self.mejor['evaluacion']}",
                  f"Objetivo: {self.max_eval}")
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


