#!/usr/bin/env python

from array import array
from operator import itemgetter
from itertools import groupby
from sys import exit

puntaje_inicial = {
    'Brazil':    27,
    'Chile':     26,
    'Paraguay':  24,
    'Argentina': 22,
    'Ecuador':   20,
    'Uruguay':   18,
    'Colombia':  17,
    'Venezuela': 17,
    'Bolivia':   12,
    'Peru':       7,
}

partidos = [
    ('Argentina', 'Brazil'),
    ('Chile',     'Venezuela'),
    ('Colombia',  'Ecuador'),
    ('Paraguay',  'Bolivia'),
    ('Peru',      'Uruguay'),

    ('Uruguay',   'Colombia'),
    ('Paraguay',  'Argentina'),
    ('Brazil',    'Chile'),
    ('Bolivia',   'Ecuador'),
    ('Venezuela', 'Peru'),

    ('Venezuela', 'Paraguay'),
    ('Bolivia',   'Brazil'),
    ('Argentina', 'Peru'),
    ('Colombia',  'Chile'),
    ('Ecuador',   'Uruguay'),

    ('Paraguay',  'Colombia'),
    ('Uruguay',   'Argentina'),
    ('Peru',      'Bolivia'),
    ('Brazil',    'Venezuela'),
    ('Chile',     'Ecuador'),
]

res_ptsL_ptsV = [('L', 3, 0), ('V', 0, 3), ('E', 1, 1),]
equipos = list(puntaje_inicial.keys())
partidos_por_fecha = len(equipos) // 2


def tabla_de_posiciones(puntos):
    '''A partir de un diccionario {equipo: puntaje}, genera tuplas
    [(posicion, cuantos, equipo, puntaje)] ordenadas por posicion.
    'cuantos' es la cantidad de equipos con el mismo puntaje
    (y por lo tanto en la misma posicion).'''

    puntajes_ordenados = sorted(puntos.items(), key=itemgetter(1), reverse=True)
    posicion = 1
    for pts, equipos in groupby(puntajes_ordenados, itemgetter(1)):
        equipos = list(equipos)
        cuantos = len(equipos)
        for (equipo, _) in equipos:
            yield (posicion, cuantos, equipo, pts)
        posicion += cuantos


def estado(posicion, cuantos):
    '''Dada la posicion de un equipo y cuantos equipos comparten su posicion,
    retorna una tupla (clasifica, repechaje, eliminado), donde cada elemento
    es True si el equipo puede encontrarse en esa situacion.'''

    mejor, peor = posicion, posicion + cuantos - 1
    clasifica = mejor <= 4
    repechaje = mejor <= 5 <= peor
    eliminado = 6 <= peor
    return (clasifica, repechaje, eliminado)


def backtrack(resultados, puntos, i=0):
    if i == len(resultados):
        for (pos, c, eq, _) in tabla_de_posiciones(puntos):
            if eq == 'Chile':
                (_, _, el) = estado(pos, c)
                if el:
                    print "Chile puede quedar eliminado"
                    print resultados.tostring()
                    print list(tabla_de_posiciones(puntos))
                    exit()
                return
        else:
            print "Error: no encontramos a Chile"
            exit()
    else:
        #if i % partidos_por_fecha == 0:
        #    # ya terminamos de asignar una fecha completa,
        #    # y podemos revisar si el quinto puede alcanzar a Chile.
        #    fechas_restantes = (len(partidos) - i) // partidos_por_fecha
        equipo_local, equipo_visita = partidos[i]
        for resultado, puntos_local, puntos_visita in res_ptsL_ptsV:
            resultados[i] = resultado
            puntos[equipo_local] += puntos_local
            puntos[equipo_visita] += puntos_visita
            backtrack(resultados, puntos, i + 1)
            puntos[equipo_local] -= puntos_local
            puntos[equipo_visita] -= puntos_visita


def main():
    resultados = array('c', ' ' * len(partidos))
    puntaje = puntaje_inicial.copy()
    backtrack(resultados, puntaje)

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()

