import json
import os

class Table:
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.indexes = {}

        if os.path.exists(filename):
            with open(filename, 'r') as file:
                self.data = json.load(file)
                self.create_indexes()

    def create_indexes(self):
        for record in self.data:
            self.update_indexes(record)

    def update_indexes(self, record):
        for key, value in record.items():
            if key not in self.indexes:
                self.indexes[key] = {}
            if value not in self.indexes[key]:
                self.indexes[key][value] = []
            self.indexes[key][value].append(record)

    def add_record(self, record):
        self.data.append(record)
        self.update_indexes(record)
        self.save_to_json()

    def save_to_json(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file, indent=4)

    def index_by_idRobot(self):
        self.indexes['idRobot'] = {}
        for record in self.data:
            id_robot = record.get('idRobot')
            if id_robot not in self.indexes['idRobot']:
                self.indexes['idRobot'][id_robot] = []
            self.indexes['idRobot'][id_robot].append(record)

    def index_by_estado(self):
        self.indexes['estado'] = {}
        for record in self.data:
            estado = record.get('estado')
            if estado not in self.indexes['estado']:
                self.indexes['estado'][estado] = []
            self.indexes['estado'][estado].append(record)

    def get_records_by_index(self, key, value):
        if key in self.indexes and value in self.indexes[key]:
            return self.indexes[key][value]
        else:
            return []

    def get_all_records(self):
        return self.data

    def get_records_by_idRobot(self, id_robot):
        return self.get_records_by_index('idRobot', id_robot)
