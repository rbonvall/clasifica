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

puntos_equipos = {'L': (3, 0), 'E': (1, 1), 'V': (0, 3)}
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


def crear_dominios(partidos, puntaje):
    posiciones = dict((eq, pos) for (pos, _, eq, _) in tabla_de_posiciones(puntaje))

    # los partidos seran asignados en este orden:
    # * primero los partidos de Chile,
    # * luego en orden de relevancia ascendente, donde la relevancia es el
    #   negativo de la suma de las posiciones de los equipos
    def relevancia(partido):
        local, visita = partido
        return ('Chile' in partido, posiciones[local] + posiciones[visita])
    partidos = sorted(partidos, reverse=True, key=relevancia)

    dominios = []
    for partido in partidos:
        local, visita = partido
        if local == 'Chile':
            resultados_por_asignar = 'V'
        elif visita == 'Chile':
            resultados_por_asignar = 'L'
        elif posiciones[local] < posiciones[visita]:
            resultados_por_asignar = 'LEV'
        else:
            resultados_por_asignar = 'VEL'
        dominios.append((partido, resultados_por_asignar))
    return dominios


def estado(posicion, cuantos):
    '''Dada la posicion de un equipo y cuantos equipos comparten su posicion,
    retorna una tupla (clasifica, repechaje, eliminado), donde cada elemento
    es True si el equipo puede encontrarse en esa situacion.'''

    mejor, peor = posicion, posicion + cuantos - 1
    clasifica = mejor <= 4
    repechaje = mejor <= 5 <= peor
    eliminado = 6 <= peor
    return (clasifica, repechaje, eliminado)


def analizar_resultados(dominio_partidos, resultados, puntos, casos=set()):
    equipo = 'Chile'
    pos, c = ((pos, c) for (pos, c, eq, _) in tabla_de_posiciones(puntos) if eq == equipo).next()
    (clasifica, repechaje, eliminado) = estado(pos, c)

    caso = {
        (True,  True,  True):  'Eliminado por diferencia de goles',
        (False, True,  True):  'Eliminado por diferencia de goles',
        (True,  True,  False): 'Repechaje por diferencia de goles',
        (True,  False, False): 'Clasificado',
        (False, True,  False): 'Repechaje',
        (False, False, True):  'Eliminado',
    }[clasifica, repechaje, eliminado]
    if caso not in casos:
        print 'Caso:', caso
        print 'Resultados:', resultados.tostring()
        print 'Tabla:', list(tabla_de_posiciones(puntos))
        casos.add(caso)
        if len(casos) == 5:
            exit()


def backtrack(dominio_partidos, resultados, puntos, i=0):
    if i == len(resultados):
        print resultados.tostring()
        analizar_resultados(dominio_partidos, resultados, puntos)
    else:
        #if i % partidos_por_fecha == 0:
        #    # ya terminamos de asignar una fecha completa,
        #    # y podemos revisar si el quinto puede alcanzar a Chile.
        #    fechas_restantes = (len(partidos) - i) // partidos_por_fecha
        (equipo_local, equipo_visita), dominio = dominio_partidos[i]
        for resultado in dominio:
            puntos_local, puntos_visita = puntos_equipos[resultado]
            resultados[i] = resultado
            puntos[equipo_local] += puntos_local
            puntos[equipo_visita] += puntos_visita
            backtrack(dominio_partidos, resultados, puntos, i + 1)
            puntos[equipo_local] -= puntos_local
            puntos[equipo_visita] -= puntos_visita


def main():
    resultados = array('c', ' ' * len(partidos))
    puntaje = puntaje_inicial.copy()
    dominio = crear_dominios(partidos, puntaje)
    backtrack(dominio, resultados, puntaje)

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()

