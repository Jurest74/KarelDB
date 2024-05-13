import json
import argparse
import os
from robot import Robot
from logevento import LogEvento
from estadoprograma import EstadoPrograma
from table import Table
import threading

base_datos = {}
semaphore = threading.Semaphore(1)
numero_registros = 0

def cargar_base_datos(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {}

def guardar_base_datos(base_datos, nombre_archivo):
    with open(nombre_archivo, 'w') as archivo:
        json.dump(base_datos, archivo, indent=4)

def agregar_registro(tabla, registro):
    global base_datos, numero_registros
    with semaphore:
        if tabla not in base_datos:
            base_datos[tabla] = []
        base_datos[tabla].append(registro)
        guardar_base_datos(base_datos, nombre_archivo)
        numero_registros += 1
        if numero_registros >= 50:
            flush_base_datos()

def flush_base_datos():
    global base_datos, numero_registros
    guardar_base_datos(base_datos, 'base_datos.json')
    print("JSON database flushed to disk.")
    numero_registros = 0
    base_datos.clear()
    base_datos.update(cargar_base_datos('base_datos.json'))

def main():
    parser = argparse.ArgumentParser(description='Manejo de base de datos simulada en formato JSON')
    parser.add_argument('tabla', choices=['Robots', 'LogEventos', 'EstadoPrograma'],
                        help='Tabla en la que se desea agregar un registro')
    parser.add_argument('--tipoRobot', type=int, help='Tipo del robot')
    parser.add_argument('--idRobot', type=int, help='ID del robot')
    parser.add_argument('--encendido', choices=['True', 'False'], help='Indica si el robot está encendido')
    parser.add_argument('--timeStamp', help='Marca de tiempo del evento')
    parser.add_argument('--avenida', type=int, help='Número de la avenida')
    parser.add_argument('--calle', type=int, help='Número de la calle')
    parser.add_argument('--sirenas', type=int, help='Cantidad de sirenas')
    parser.add_argument('--estado', type=int, choices=[0, 1, 2, 3], help='Estado del programa')

    args = parser.parse_args()

    print("Argumentos capturados:")
    print(args)

    encendido = True if args.encendido == 'True' else False

    if args.tabla == 'Robots':
        robots_table = Table('robots.json')
        robot = Robot(args.tipoRobot, args.idRobot, encendido)
        robots_table.add_record(robot.__dict__)
    elif args.tabla == 'LogEventos':
        log_eventos_table = Table('log_eventos.json')
        log_evento = LogEvento(args.timeStamp, args.idRobot, args.avenida, args.calle, args.sirenas)
        log_eventos_table.add_record(log_evento.__dict__)
    elif args.tabla == 'EstadoPrograma':
        estado_programa_table = Table('estado_programa.json')
        estado_programa = EstadoPrograma(args.timeStamp, args.estado)
        estado_programa_table.add_record(estado_programa.__dict__)

    if len(robots_table.data) >= 50:
        robots_table.save_to_json()
    if len(log_eventos_table.data) >= 50:
        log_eventos_table.save_to_json()
    if len(estado_programa_table.data) >= 50:
        estado_programa_table.save_to_json()

if __name__ == "__main__":
    nombre_archivo = 'base_datos.json'
    base_datos = cargar_base_datos(nombre_archivo)
    main()
