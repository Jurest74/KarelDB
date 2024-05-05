class Robot:
    def __init__(self, tipoRobot, idRobot, encendido, **kwargs):
        self.tipoRobot = tipoRobot
        self.idRobot = idRobot
        self.encendido = encendido
        # Añadir otros atributos dinámicamente si existen
        for key, value in kwargs.items():
            setattr(self, key, value)
