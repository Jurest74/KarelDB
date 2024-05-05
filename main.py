import json
import argparse
from robot import Robot
from logevento import LogEvento
from estadoprograma import EstadoPrograma
import threading

base_datos = {}  # Variable global para almacenar la base de datos cargada
semaphore = threading.Semaphore(1)  # Semáforo para permitir un único hilo a la vez

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
    global base_datos
    with semaphore:  # Adquirir el semáforo para permitir solo un hilo a la vez
        if tabla not in base_datos:
            base_datos[tabla] = []
        base_datos[tabla].append(registro)
        guardar_base_datos(base_datos, nombre_archivo)

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

    # Convertir el valor de encendido a un booleano
    encendido = True if args.encendido == 'True' else False

    if args.tabla == 'Robots':
        robot = Robot(args.tipoRobot, args.idRobot, encendido)
        agregar_registro('Robots', robot.__dict__)
    elif args.tabla == 'LogEventos':
        log_evento = LogEvento(args.timeStamp, args.idRobot, args.avenida, args.calle, args.sirenas)
        agregar_registro('LogEventos', log_evento.__dict__)
    elif args.tabla == 'EstadoPrograma':
        estado_programa = EstadoPrograma(args.timeStamp, args.estado)
        agregar_registro('EstadoPrograma', estado_programa.__dict__)

if __name__ == "__main__":
    nombre_archivo = 'base_datos.json'  # Nombre del archivo de base de datos
    base_datos = cargar_base_datos(nombre_archivo)  # Cargar la base de datos al inicio
    main()
