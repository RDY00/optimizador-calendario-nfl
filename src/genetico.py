""" Implementación del algoritmo genético """

import numpy as np
import time
from tqdm.auto import tqdm
from temporada import TemporadaNFL
from evaluacion import EvaluacionNFL

class AlgoritmoGenetico:
  """ Algoritmo Genético para las N-Reinas """

  # Optimizar accesos
  __slots__ = ("ejemplar", "evalua_solucion", "p_cruza" "p_mutacion",
               "p_cruza_filas", "p_muta_filas", "poblacion",
               "tam_poblacion", "mejor", "total_eval", "cdf", "semilla", "rng")

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
    self.p_cruza_filas = 0
    self.p_muta_filas = 0
    # Datos población
    self.poblacion = None
    self.tam_poblacion = 0
    self.mejor = None
    self.total_eval = 0
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
      (self.ejemplar.num_equipos,self.ejemplar.num_semanas,2), dtype=np.uint16)

    # Rellenamos filas aleatoriamente
    for i in range(self.ejemplar.num_equipos):
      partidos = np.array(
        self.ejemplar.equipos["partidos"] + [self.ejemplar.bye])
      rng.shuffle(partidos)
      sol[i,:,0] = partidos

    # Reparamos filas
    self.repara_filas(sol)

    lista_horarios = []
    # Rellenamos columnas
    for semana in range(self.ejemplar.num_semanas):
      # Horarios esterales de la semana aleatorios
      horarios = self.ejemplar.horarios_semana(semana)
      rng.shuffle(horarios)
      lista_horarios.append(horarios)

    self.agrega_horarios(0, sol.shape[1], sol, lista_horarios)

      # # Obtenemos partidos y sus índices
      # partidos, inv = np.unique(sol[:,semana,0], return_inverse=True)
      # # Es el contador con el índice para repartir horarios a bye
      # ind_bye = len(partidos)
      # if partidos[-1] == self.ejemplar.bye: ind_bye-=1

      # # Repartimos equipo por equipo
      # for equipo,ind in enumerate(inv):
      #   partido = sol[equipo,semana,0]
      #   # Cuando es bye y |horarios| > |partidos|
      #   if partido == self.ejemplar.bye and ind_bye < len(horarios):
      #     sol[equipo,semana,1] = horarios[ind_bye]
      #     ind_bye += 1
      #   # Cuando |horarios| <= |partidos| siempre entra aqui
      #   elif ind < len(horarios):
      #     sol[equipo,semana,1] = horarios[ind]
      #   # Cuando |horarios| < |partidos| algunos partidos se quedan en 0

    return {
      "solucion" : sol,
      "evaluacion" : self.evalua_solucion(sol)
    }

  def repara_filas(self, solucion: np.ndarray, inicio: int = 0) -> None:
    """ Repara las filas de una solución para que tenga un formato válido

    Recorre todas las filas de arriba a abajo para asegurarse de que todos los
    partidos estén correctamente marcado en ambos equipos que los juegan.

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a reparar, la reparación ocurre sobre está misma (se modifica)
    inicio : int
      Fila de inicio para la reparacíon, se recorren todas las filas empezando
      desde esa. Por defecto es 0
    """
    # Diccionario con el orden de los partidos para tener búsqueda de O(1)
    orden_partidos = [{} for i in range(self.ejemplar.num_equipos)]

    for equipo,juegos in enumerate(solucion):
      for semana,partido in enumerate(juegos):
        orden_partidos[equipo][partido] = semana

    for i in range(solucion.shape[0]):
      equipo = (i+inicio) % solucion.shape[0]
      for semana,partido in enumerate(solucion[equipo,:,0]):
        # Encontramos al equipo contra el que juega
        contra = self.ejemplar.equipo_contra(equipo, partido)
        # Si es BYE no hacemos nada
        if contra is None: continue
        # Si el partido es correcto terminamos
        if solucion[contra,semana,0] == partido: continue
        # Sino, intercambiamos el partido de colisión con el que va
        partido_colision = solucion[contra,semana,0]
        ind_partido = orden_partidos[contra][partido]
        solucion[contra,semana,0], solucion[contra,ind_partido,0] = \
          solucion[contra,ind_partido,0], solucion[contra,semana,0]
        # Actualizamos el diccionario de índices
        orden_partidos[contra][partido] = semana
        orden_partidos[contra][partido_colision] = ind_partido

    # VERSION CON PROPAGACION
    # # Reparación desde la fila modificada
    # for equipo in range(solucion.shape[0]):
    #   e = equipo
    #   for semana,partido in enumerate(solucion[equipo,:,0]):
    #     s, p = semana, partido
    #     # Repetimos hasta que no haya más colisiones
    #     while True:
    #       # Si es BYE terminamos
    #       if p == self.ejemplar.bye: break
    #       # Obtenemos al equipo contra el que se juega en contra (c)
    #       local = self.ejemplar.partidos[p]["local"]
    #       visitante = self.ejemplar.partidos[p]["visitante"]
    #       c = local if local != e else visitante
    #       # Si el partido está bien posicionado terminamos esta iteración
    #       if solucion[c,s,0] == p: break
    #       # Sino, intercambiamos posiciones con el partido mal posicionado (pc)
    #       pc = solucion[c,s,0] # Partido de la colisión con p
    #       sc = orden_partidos[c][p] # Semana de la colisión con p
    #       solucion[c,s,0], solucion[c,sc,0] = solucion[c,sc,0], solucion[c,s,0]
    #       # Actualizamos valores para la nueva iteración
    #       orden_partidos[c][p], orden_partidos[c][pc] = orden_partidos[c][pc], \
    #                                                     orden_partidos[c][p]
    #       e, p, s = c, pc, sc
    #       if p == partido: break # No alteramos la fila que estamos moviendo
    #       # assert p != partido, "No debería de tocarse esa fila nunca" # Debug

  def agrega_horarios(self, inicio: int, fin: int, solucion: np.ndarray,
      horarios: list) -> None:
    """ Repara las columnas de una solución para que vuelva a ser fatible 

    TODO: Cambiar esto

    Se asegura de que cada partido tenga el mismo horario asignado en ambas
    apariciones por semana en el intervalo de semanas [inicio,fin) de la
    solucion.

    Como esta función está pensada para reparar la cruza entre columnas,
    recibe al padre del que se heredo la sección de horarios para recuperar el
    orden original de los partidos de esa semana.

    El hijo se cambia directamente.
    
    Parámetros
    ----------
    inicio : int
      Inicio del rango de semanas a alterar
    fin : int
      fin del rango de semanas a alterar
    solucion : np.ndarray
      Solución a la que se le agregarán los horarios
    horarios : lista
      Lista de los horarios por semana. Deben de haber inicio - fin horarios
    """
    for h,semana in zip(range(inicio,fin),horarios):
      # Obtenemos los partidos y sus índices para reconstruirlos
      partidos, inv = np.unique(solucion[:,semana,0], return_inverse=True)
      ind_bye = len(partidos) # Índice para repartir horarios bye
      if partidos[-1] == self.ejemplar.bye: ind_bye-=1

      # Repartimos equipo por equipo
      for equipo,ind in enumerate(inv):
        partido = solucion[equipo,semana,0]
        # Cuando es bye y |h| > |partidos|
        if partido == self.ejemplar.bye and ind_bye < len(h):
          sol[equipo,semana,1] = h[ind_bye]
          ind_bye += 1
        # Cuando |h| <= |partidos| siempre entra aqui
        elif ind < len(h):
          solucion[equipo,semana,1] = h[ind]
        # Cuando |h| < |partidos| algunos partidos se quedan en 0

    # # p = padre.copy()
    # for semana in range(inicio, fin):
    #   for equipo,partido in enumerate(hijo[:,semana,0]):
    #     if partido == self.ejemplar.bye: continue
    #     # Encontramos contra quien juega
    #     contra = self.ejemplar.equipo_contra(equipo, partido)
    #     # Si es BYE no hacemos nada
    #     if contra is None: continue
    #     # Si los horarios están bien, no hacemos nada
    #     if hijo[contra,semana,1] == hijo[equipo,semana,1]: continue
    #     # Sino, intercambiamos el horario mal con el correcto
    #     partido_colision = padre[equipo,semana,0]
    #     equipo_colision = self.ejemplar.equipo_contra(equipo, partido_colision)
    #     hijo[contra,semana,1], hijo[equipo_colision,semana,1] = \
    #       hijo[equipo_colision,semana,1], hijo[contra,semana,1]
    #     # Actualizamos los indices
    #     # p[contra,semana,1], p[equipo_colision,semana,1] = \
    #     #   p[equipo_colision,semana,1], p[contra,semana,1]

  def cruza_filas(self, sol1: np.ndarray, sol2: np.ndarray) -> tuple:
    """ Aplica cruza por filas entre los padres
    
    Los hijos tiene las filas alternadas una a una de los padre en distinto
    orden (un hijo tiene las filas pares de sol1 y las impares de sol2 y el
    otro las tiene invertidas).

    La dimesión de los horarios se hereda directamente de cada padre:
    hijo1 tiene los de padre1 e hijo2 los de padre2.

    Después de asignar las filas, las soluciones se reparan.

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
    hijo1 = np.zeros(sol1.shape)
    hijo2 = np.zeros(sol2.shape)

    # La dimensión de horarios es igual
    hijo1[:,:,1] = sol1[:,:,1]
    hijo2[:,:,1] = sol2[:,:,1]
    
    for equipo in range(sol1.shape[0]):
      if equipo % 2 == 0:
        hijo1[equipo,:,0] = sol1[equipo,:,0]
        hijo2[equipo,:,0] = sol2[equipo,:,0]
      else:
        hijo1[equipo,:,0] = sol2[equipo,:,0]
        hijo2[equipo,:,0] = sol1[equipo,:,0]

    self.repara_filas(hijo1)
    self.repara_filas(hijo2)

    return hijo1, hijo2

  def cruza_cols(self, sol1: np.ndarray, sol2: np.ndarray) -> tuple:
    """ Aplica cruza por columnas entre los padres
    
    Se hace cruce de un punto entre los horarios, se escoge un número entre
    0 y el número se semanas como cruce y cada hijo tiene la mitad de horarios
    de la semana (0,cruce] de un padre y la de [cruce,semanas) del otro.

    La dimesión de los partidos se hereda directamente de cada padre:
    hijo1 tiene los de padre1 e hijo2 los de padre2.
    

    Después de asignar las columnas, las soluciones se reparan.

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
    hijo1 = sol1.copy()
    hijo2 = sol2.copy()

    # Punto de cruce
    cruce = rng.integers(sol1.shape[0])

    # Rellenamos horarios por orden relativo
    datos_horarios = (sol2,hijo1,cruce,sol2.shape[1]), (sol1,hijo2,0,cruce)

    for padre,hijo,inicio,fin in datos_horarios:
      lista_horarios = []
      for semana in range(inicio,fin):
        # Obtenemos los horarios por orden de aparición
        _, ind = np.unique(padre[:,semana,1], return_indexes=True)
        # Quitamos el primer índice porque seguro es NONE (0)
        horarios = padre[np.sort(ind[1:]),semana,1][1:]
        lista_horarios.append(horarios)
      # Cruzamos con el hijo
      self.agrega_horarios(inicio, fin, hijo, lista_horarios)

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
    equipo = np.integers(solucion.shape[0])
    semanas = np.integers(0, solucion.shape[1], 2)
    
    solucion[equipo,semanas[0],0], solucion[equipo,semanas[1],0] = \
      solucion[equipo,semanas[1],0], solucion[equipo,semanas[0],0]

    self.repara_filas(solucion, equipo)

  def muta_cols(self, solucion: np.ndarray) -> None:
    """ Muta una solución por columnas

    Intercambia los horarios de dos partidos de una semana aleatoria, luego
    repara la solución.

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a mutar
    """
    # Obtenemos semana y equipos aleatorios
    semana = np.integers(solucion.shape[1])
    while True:
      equipos = np.integers(0,solucion.shape[0],2)
      partido1 = solucion[equipos[0],semana,0]
      partido2 = solucion[equipos[1],semana,0]
      if self.ejemplar.bye in equipos or partido1 != partido2: break
    
    # Intercambiamos los horarios
    solucion[equipos[0],semana,1], solucion[equipos[1],semana,1] = \
      solucion[equipos[1],semana,1], solucion[equipos[0],semana,1]

    # Propagamos el cambio
    contras = [self.ejemplar.equipo_contra(e) for e in equipos]
    solucion[contras[0],semana,1] = solucion[equipos[0],semana,1]
    solucion[contras[1],semana,1] = solucion[equipos[1],semana,1]

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
      val = rng.random()
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
      if rng.random() < self.p_mutacion:
        if rng.random() < self.p_cruza_filas:
          h1, h2 = self.cruza_filas(h1,h2)
        else:
          h1, h2 = self.cruza_cols(h1,h2)

      # Mutación
      if rng.random() < self.p_cruza:
        if rng.random() < self.p_muta_filas:
          self.muta_filas(h1)
          self.muta_filas(h2)
        else:
          self.muta_cols(h1)
          self.muta_cols(h2)

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
      p_cruza: float = 0.8, p_mutacion: float = 0.1, p_cruza_filas: float = 0.5,
      p_muta_filas: float = 0.5, semilla: int = None) -> dict:
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
      Probabilidad de mutar a cada invidivuo. Por defectto es 0.1
    p_cruza_filas : float
      Probabilidad de cruzar por filas, la probabilidad de cruzar por columnas
      es complementaria.
      Por defecto es 0.5
    p_muta_filas : float
      Probabilidad de mutar por filas, la probabilidad de mutar por columnas es
      complementaria.
      Por defecto es 0.5
    semilla : int
      Semilla para los valores aleatorios, si es None se usa time.time().
      Por defecto es None.

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

