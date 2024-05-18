import json
import argparse
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from robot import Robot
from logevento import LogEvento
from estadoprograma import EstadoPrograma
from table import Table
from datetime import datetime
import os.path

# Definir un bloqueo para cada tabla
lock_robots = Lock()
lock_log_eventos = Lock()
lock_estado_programa = Lock()

# Nombre del archivo para el registro de transacciones
archivo_transacciones = 'registro_transacciones.json'

# Estructura para el registro de transacciones
transacciones = []

def cargar_transacciones():
    try:
        if os.path.exists(archivo_transacciones):
            with open(archivo_transacciones, 'r') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        print("Error al cargar las transacciones")
        return []

def guardar_transacciones():
    with open(archivo_transacciones, 'w') as f:
        json.dump(transacciones, f, indent=4)

# Cargar las transacciones existentes
transacciones = cargar_transacciones()

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

def registrar_transaccion(operacion, tabla, parametros, resultado):
    transacciones.append({
        'timestamp': str(datetime.now()),
        'operacion': operacion,
        'tabla': tabla,
        'parametros': parametros,
        'resultado': resultado
    })
    # Guardar transacciones actualizadas
    guardar_transacciones()

def registrar_consulta(tabla, consulta, resultado):
    transacciones.append({
        'timestamp': str(datetime.now()),
        'operacion': 'consulta',
        'tabla': tabla,
        'consulta': consulta,
        'resultado': resultado
    })
    # Guardar transacciones actualizadas
    guardar_transacciones()

def procesar_robots(args, robots_table):
    with lock_robots:
        robots_table.index_by_idRobot()  # Indexar por idRobot

        if args.consultar_ultimoEstadoIdRobot is not None:
            # Consultar el último estado del robot por ID
            registros_robot = robots_table.get_records_by_idRobot(args.consultar_ultimoEstadoIdRobot)
            if registros_robot:
                ultimo_estado = registros_robot[-1]['encendido']  # Obtener el último estado
                print(f"Último estado del robot con ID {args.consultar_ultimoEstadoIdRobot}: {ultimo_estado}")
                registrar_consulta('Robots', f"consulta de último estado por idRobot={args.consultar_ultimoEstadoIdRobot}", 'exitosa')
            else:
                print(f"No se encontraron registros para idRobot {args.consultar_ultimoEstadoIdRobot}")
                registrar_consulta('Robots', f"consulta de último estado por idRobot={args.consultar_ultimoEstadoIdRobot}", 'exitosa sin datos')
        elif args.consultar_idRobot is not None:
            # Consultar por ID del robot
            registros_robot = robots_table.get_records_by_idRobot(args.consultar_idRobot)
            if registros_robot:
                print(f"Registros encontrados para idRobot {args.consultar_idRobot}:")
                for registro in registros_robot:
                    print(registro)
                    registrar_consulta('Robots', f"consulta por idRobot={args.consultar_idRobot}", 'exitosa')
            else:
                print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
                registrar_consulta('Robots', f"consulta por idRobot={args.consultar_idRobot}", 'exitosa sin datos')
        else:
            # Realizar la inserción del nuevo registro
            robot = Robot(args.tipoRobot, args.idRobot, args.encendido)
            agregar_registro(robots_table.data, robot.__dict__)
            # Registrar la transacción de inserción
            registrar_transaccion('insercion', 'Robots', args.__dict__, 'exitosa')

        # Guardar datos después de la operación en la tabla de Robots
        guardar_base_datos(robots_table.data, robots_table.filename)



def procesar_log_eventos(args, log_eventos_table):
    with lock_log_eventos:
        log_eventos_table.index_by_idRobot()  # Indexar por idRobot

        if args.consultar_idRobot is not None:
            registros_log_eventos = log_eventos_table.get_records_by_idRobot(args.consultar_idRobot)
            if registros_log_eventos:
                print(f"Registros encontrados para idRobot {args.consultar_idRobot}:")
                for registro in registros_log_eventos:
                    print(registro)
                    registrar_consulta('LogEventos', f"consulta por idRobot={args.consultar_idRobot}", 'exitosa')
            else:
                print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
                registrar_consulta('LogEventos', f"consulta por idRobot={args.consultar_idRobot}", 'exitosa sin datos')
        else:
            log_evento = LogEvento(args.timeStamp, args.idRobot, args.avenida, args.calle, args.sirenas)
            agregar_registro(log_eventos_table.data, log_evento.__dict__)
            # Registrar la transacción de inserción
            registrar_transaccion('insercion', 'LogEventos', args.__dict__, 'exitosa')

        # Guardar datos después de la operación en la tabla de LogEventos
        guardar_base_datos(log_eventos_table.data, log_eventos_table.filename)

def procesar_estado_programa(args, estado_programa_table):
    with lock_estado_programa:
        if args.consultar_estado is not None:
            registros_estado = estado_programa_table.get_records_by_index('estado', args.consultar_estado)
            if registros_estado:
                print(f"Registros encontrados para estado {args.consultar_estado}:")
                for registro in registros_estado:
                    print(registro)
                    registrar_consulta('EstadoPrograma', f"consulta por idRobot={args.consultar_idRobot}", 'exitosa')
            else:
                print(f"No se encontraron registros para estado {args.consultar_estado}")
                registrar_consulta('EstadoPrograma', f"consulta por idRobot={args.consultar_idRobot}", 'exitosa sin datos')
        else:
            estado_programa = EstadoPrograma(args.timeStamp, args.estado)
            agregar_registro(estado_programa_table.data, estado_programa.__dict__)
            # Registrar la transacción de inserción
            registrar_transaccion('insercion', 'EstadoPrograma', args.__dict__, 'exitosa')

        # Guardar datos después de la operación en la tabla de EstadoPrograma
        guardar_base_datos(estado_programa_table.data, estado_programa_table.filename)

def procesar_log_eventos_ultima_posicion(args, log_eventos_table):
    with lock_log_eventos:
        log_eventos_table.index_by_idRobot()  # Indexar por idRobot

        if args.consultar_idRobot is not None:
            registros_log_eventos = log_eventos_table.get_records_by_idRobot(args.consultar_idRobot)
            if registros_log_eventos:
                # Ordenar los registros por timeStamp en orden descendente para obtener el más reciente
                registros_log_eventos.sort(key=lambda x: x['timeStamp'], reverse=True)
                ultima_posicion = registros_log_eventos[0]
                print(f"Última posición del robot con ID {args.consultar_idRobot}:")
                print(ultima_posicion)
                registrar_consulta('LogEventos', "consulta de ultima posición por idRobot={args.consultar_idRobot}", 'exitosa')
            else:
                print(f"No se encontraron registros para idRobot {args.consultar_idRobot}")
                registrar_consulta('LogEventos', f"consulta de ultima posición por idRobot={args.consultar_idRobot}", 'exitosa sin datos')
        else:
            print("Se requiere especificar un ID de robot para consultar su última posición")

def procesar_transacciones(args):
    if args.tabla in ['Robots', 'LogEventos', 'EstadoPrograma']:
        transacciones_relacionadas = filter(lambda x: x['tabla'] == args.tabla, transacciones)
        print(f"Transacciones relacionadas con la tabla '{args.tabla}':")
        for transaccion in transacciones_relacionadas:
            print(transaccion)
        registrar_consulta(args.tabla, f"consulta de transacciones", 'exitosa')
    else:
        print("Error: la tabla especificada no es válida.")

def main():
    parser = argparse.ArgumentParser(description='Manejo de base de datos simulada en formato JSON')
    parser.add_argument('tabla', choices=['Robots', 'LogEventos', 'EstadoPrograma'],
                        help='Tabla en la que se desea agregar un registro o consultar transacciones')
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
    parser.add_argument('--consultar_ultimaPosicionIdRobot', action='store_true', help='Consultar la última posición del robot por ID')
    parser.add_argument('--consultar_ultimoEstadoIdRobot', type=int, help='Consultar el último estado del robot por ID')
    parser.add_argument('--consultar_transacciones', action='store_true', help='Consultar las transacciones relacionadas con la tabla especificada')

    args = parser.parse_args()

    if args.consultar_transacciones:
        procesar_transacciones(args)
    else:
        encendido = args.encendido == 'true'

        robots_table = Table('robots.json')
        log_eventos_table = Table('log_eventos.json')
        estado_programa_table = Table('estado_programa.json')

        with ThreadPoolExecutor(max_workers=8) as executor:
            if args.tabla == 'Robots':
                future = executor.submit(procesar_robots, args, robots_table)
            elif args.tabla == 'LogEventos':
                if args.consultar_ultimaPosicionIdRobot:
                    future = executor.submit(procesar_log_eventos_ultima_posicion, args, log_eventos_table)
                else:
                    future = executor.submit(procesar_log_eventos, args, log_eventos_table)
            elif args.tabla == 'EstadoPrograma':
                future = executor.submit(procesar_estado_programa, args, estado_programa_table)

            future.result()

            if args.tabla == 'Robots':
                with lock_robots:
                    guardar_base_datos(robots_table.data, robots_table.filename)
            elif args.tabla == 'LogEventos':
                with lock_log_eventos:
                    guardar_base_datos(log_eventos_table.data, log_eventos_table.filename)
            elif args.tabla == 'EstadoPrograma':
                with lock_estado_programa:
                    guardar_base_datos(estado_programa_table.data, estado_programa_table.filename)

if __name__ == "__main__":
    main()