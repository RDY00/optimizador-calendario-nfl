def repara_filas(solucion: np.ndarray) -> None:
    """ Repara una solución para que tenga un formato válido

    Recorre todas las filas de arriba a abajo para asegurarse de que todos los
    partidos estén correctamente marcado en ambos equipos que los juegan

    Parámetros
    ----------
    solucion : np.ndarray
      Solución a reparar, la reparación ocurre sobre está misma (se modifica)
    """
    # Diccionario con el orden de los partidos para tener búsqueda de O(1)
    orden_partidos = [{} for i in range(solucion.shape[0])]

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
          if p == solucion.shape[1]: break
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
          orden_partidos[c][p], orden_partidos[c][pc] = orden_partidos[c][pc], \
                                                        orden_partidos[c][p]
          e, p, s = c, pc, sc
          if p == partido: break # No alteramos la fila que estamos moviendo
          # assert p != partido, "No debería de tocarse esa fila nunca" # Debug

