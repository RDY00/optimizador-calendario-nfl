def read(file):
  with open(file) as data:
    info = data.readlines()
  i, p = get_partidos(info,0)
  i, e = get_estadios(info,i)
  i, q = get_equipos(info,i)
  s = info[i].split()
  partidos = tuple(p)
  estadios = tuple(e)
  equipos = tuple(q)
  thanksgiving = int(s[0])
  navidad = (s[1], s[2])
  return partidos, estadios, equipos, thanksgiving, navidad
  
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