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
nombre_archivo = 'base_datos.json'

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
    global base_datos, numero_registros, nombre_archivo
    with semaphore:
        if tabla not in base_datos:
            base_datos[tabla] = []
        base_datos[tabla].append(registro)
        guardar_base_datos(base_datos, nombre_archivo)
        numero_registros += 1
        if numero_registros >= 50:
            flush_base_datos()

def flush_base_datos():
    global base_datos, numero_registros, nombre_archivo
    guardar_base_datos(base_datos, nombre_archivo)
    print("JSON database flushed to disk.")
    numero_registros = 0
    base_datos.clear()
    base_datos.update(cargar_base_datos(nombre_archivo))

def main():
    global nombre_archivo
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
    parser.add_argument('--consultar_idRobot', type=int, help='ID del robot a consultar')
    parser.add_argument('--consultar_estado', type=int, help='Estado a consultar')

    args = parser.parse_args()

    print("Argumentos capturados:")
    print(args)

    encendido = True if args.encendido == 'True' else False

    # Crear instancias de todas las tablas independientemente del valor de args.tabla
    robots_table = Table('robots.json')
    log_eventos_table = Table('log_eventos.json')
    estado_programa_table = Table('estado_programa.json')

    if args.tabla == 'Robots':
        robots_table.index_by_idRobot()  # Indexar por idRobot

        # Consultar y imprimir registros por idRobot si se proporciona el argumento --consultar_idRobot
        if args.consultar_idRobot is not None:
            registros_robot = robots_table.get_records_by_idRobot(args.consultar_idRobot)
            if registros_robot:
                print(f"Registros encontrados para idRobot {args.consultar_idRobot}:")
                for registro in registros_robot:
                    print(registro)
            else:
                print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
        else:
            # Crear el objeto Robot y agregarlo a la tabla
            robot = Robot(args.tipoRobot, args.idRobot, encendido)
            robots_table.add_record(robot.__dict__)
            robots_table.save_to_json()

    elif args.tabla == 'LogEventos':
        log_eventos_table.index_by_idRobot()  # Indexar por idRobot

        # Consultar y imprimir registros por idRobot si se proporciona el argumento --consultar_idRobot
        if args.consultar_idRobot is not None:
            registros_log_eventos = log_eventos_table.get_records_by_idRobot(args.consultar_idRobot)
            if registros_log_eventos:
                print(f"Registros encontrados para idRobot {args.consultar_idRobot}:")
                for registro in registros_log_eventos:
                    print(registro)
            else:
                print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
        else:
            # Crear el objeto LogEvento y agregarlo a la tabla
            log_evento = LogEvento(args.timeStamp, args.idRobot, args.avenida, args.calle, args.sirenas)
            log_eventos_table.add_record(log_evento.__dict__)
            log_eventos_table.save_to_json()

    elif args.tabla == 'EstadoPrograma':
        # Crear instancia de la tabla EstadoPrograma
        estado_programa_table = Table('estado_programa.json')

        if args.consultar_estado is not None:
            # Consultar y mostrar registros por estado si se proporciona el argumento --consultar_estado
            registros_estado = estado_programa_table.get_records_by_index('estado', args.consultar_estado)
            if registros_estado:
                print(f"Registros encontrados para estado {args.consultar_estado}:")
                for registro in registros_estado:
                    print(registro)
            else:
                print(f"No se encontraron registros para estado {args.consultar_estado}")
        else:
            # Crear el objeto EstadoPrograma y agregarlo a la tabla
            estado_programa = EstadoPrograma(args.timeStamp, args.estado)
            estado_programa_table.add_record(estado_programa.__dict__)
            estado_programa_table.save_to_json()

    if len(log_eventos_table.data) >= 50:
        log_eventos_table.save_to_json()
    if len(estado_programa_table.data) >= 50:
        estado_programa_table.save_to_json()

if __name__ == "__main__":
    main()
