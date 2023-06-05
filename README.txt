INTEGRANTES:
- Fernando Márquez Pérez
- Emiliano Domínguez Cruz

DEPENDENCIAS:
Las dependencias externas que utilizamos fueron:
- numpy (https://numpy.org/install/)
- matplotlib (https://matplotlib.org/stable/users/installing/index.html)
- pandas (http://pandas.pydata.org/pandas-docs/stable/getting_started/index.html)
- tqdm (https://pypi.org/project/tqdm/)
- openpyxl (https://pypi.org/project/openpyxl/)

El resto de las dependencias fueron: time, json y pathlib.
Pero pertenecen a la biblioteca estandar

=====================

Todos los programas están escritos en Python3:

La carpeta EVALUCAION contiene los archivo EVALUACION.PY y REGLA.PY que son las clases abstractas
para la función de evaluación. EVALUACION2023.PY contiene la implementación de la función. 
BLANDAS.PY y DURAS.PY contien las reglas utilizadas.

GENETICO.PY
Contiene las clases que implementan el algoritmo genético y la función para evaluar soluciones.

GENTICO
Es el script que permite usar GENETICO.PY desde terminal

Su uso es:
./genetico EJEMPLAR TAM_POBLACION TIEMPO_LIMITE PROB_CRUZA PROB_MUTACIO [SEMILLA] [ARCHIVO]

Pueden omitirse la semilla y el archivo para no guardar la solución

Y algunos ejemplos son:
./genetico ../data/temporada2023.txt 100 60 0.8 0.01 42 ../output/Sol_8.txt  -- Ejecuta con semilla 42
./genetico ../data/temporada2023.txt 100 60 0.8 0.01 ../output/Sol_8.txt     -- Ejecutar con semilla aleatoria
./genetico ../data/temporada2023.txt 100 60 0.8 0.01                         -- Ejecutar con semilla aleatoria y no guarda
./genetico ../data/temporada2023.txt 100 60 0.8 0.01 42                      -- Ejecutar con semilla fija y no guarda

* También puede utilizarse como python3 genetico si usarla como script no funciona
(depende de que exista /bin/env para funcionar así)

EVALUA
Contiene la funcion para evaluar soluciones desde terminal

Su uso es:
./evalua EJEMPLAR SOLUCION

Y algunos ejemplos son:
./evalua ../data/temporada2023.txt ./../output/nfl2023.txt

* También puede utilizarse como python3 evalua si usarla como script no funciona
(depende de que exista /bin/env para funcionar así)

SOLUCION-A-EXCEL

Convierte una soución codificada a formato xlsx.

Su uso es:
./solucion-a-excel EJEMPLAR SOLUCION SALIDA

Es importante que el archivo de salida tenga terminación .xslx proque de lo contrario el programa se traba al intentar guardar.

Y algunos ejemplos son:
./solucion-a-excel ../data/temporada2023.txt ./../output/nfl2023.txt salida.xslx

* También puede utilizarse como python3 solucion-a-excel si usarla como script no funciona
(depende de que exista /bin/env para funcionar así)

EJECUCIONES.PY
Contiene el código para realizar las ejecuciones y guardarlas en .json

Su uso es:
python3 ejecuciones.py
python3 ejecuciones.py > /dev/null -- Para no ver las salidas

LECTURA.PY
Contiene el código apra generar tablas y gráficas a partir de los json

Su uso es:
python3 lectura.py
python3 lectura.py > /dev/null -- Para no ver las salidas


