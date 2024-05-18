import json
import argparse
from concurrent.futures import ThreadPoolExecutor
from robot import Robot
from logevento import LogEvento
from estadoprograma import EstadoPrograma
from table import Table

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
    tabla.append(registro)  # Agregar el registro directamente a la tabla

def procesar_robots(args, robots_table):
    robots_table.index_by_idRobot()  # Indexar por idRobot

    if args.consultar_idRobot is not None:
        registros_robot = robots_table.get_records_by_idRobot(args.consultar_idRobot)
        if registros_robot:
            print(f"Registros encontrados para idRobot {args.consultar_idRobot}:")
            for registro in registros_robot:
                print(registro)
        else:
            print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
    else:
        robot = Robot(args.tipoRobot, args.idRobot, args.encendido)
        agregar_registro(robots_table.data, robot.__dict__)

def procesar_log_eventos(args, log_eventos_table):
    log_eventos_table.index_by_idRobot()  # Indexar por idRobot

    if args.consultar_idRobot is not None:
        registros_log_eventos = log_eventos_table.get_records_by_idRobot(args.consultar_idRobot)
        if registros_log_eventos:
            print(f"Registros encontrados para idRobot {args.consultar_idRobot}:")
            for registro in registros_log_eventos:
                print(registro)
        else:
            print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
    else:
        log_evento = LogEvento(args.timeStamp, args.idRobot, args.avenida, args.calle, args.sirenas)
        agregar_registro(log_eventos_table.data, log_evento.__dict__)

def procesar_estado_programa(args, estado_programa_table):
    if args.consultar_estado is not None:
        registros_estado = estado_programa_table.get_records_by_index('estado', args.consultar_estado)
        if registros_estado:
            print(f"Registros encontrados para estado {args.consultar_estado}:")
            for registro in registros_estado:
                print(registro)
        else:
            print(f"No se encontraron registros para estado {args.consultar_estado}")
    else:
        estado_programa = EstadoPrograma(args.timeStamp, args.estado)
        agregar_registro(estado_programa_table.data, estado_programa.__dict__)

def main():
    parser = argparse.ArgumentParser(description='Manejo de base de datos simulada en formato JSON')
    parser.add_argument('tabla', choices=['Robots', 'LogEventos', 'EstadoPrograma'],
                        help='Tabla en la que se desea agregar un registro')
    parser.add_argument('--tipoRobot', type=int, help='Tipo del robot')
    parser.add_argument('--idRobot', type=int, help='ID del robot')
    parser.add_argument('--encendido', choices=['true', 'false'], help='Indica si el robot está encendido')
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

    encendido = args.encendido == 'true'

    robots_table = Table('robots.json')
    log_eventos_table = Table('log_eventos.json')
    estado_programa_table = Table('estado_programa.json')

    with ThreadPoolExecutor(max_workers=8) as executor:
        if args.tabla == 'Robots':
            future = executor.submit(procesar_robots, args, robots_table)
        elif args.tabla == 'LogEventos':
            future = executor.submit(procesar_log_eventos, args, log_eventos_table)
        elif args.tabla == 'EstadoPrograma':
            future = executor.submit(procesar_estado_programa, args, estado_programa_table)

        # Esperar a que la operación en el ThreadPoolExecutor haya terminado antes de continuar
        future.result()

    # Guardar datos después de cada operación
    guardar_base_datos(robots_table.data, robots_table.filename)
    guardar_base_datos(log_eventos_table.data, log_eventos_table.filename)
    guardar_base_datos(estado_programa_table.data, estado_programa_table.filename)

if __name__ == "__main__":
    main()
