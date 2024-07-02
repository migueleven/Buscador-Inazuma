class Character:
    def __init__(self, id, nombre, sprite, modelo_3d):
        self._id = id
        self._nombre = nombre
        self._sprite = sprite
        self._modelo_3d = modelo_3d

    # Getters
    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def sprite(self):
        return self._sprite

    @property
    def modelo_3d(self):
        return self._modelo_3d

    # Setters
    @id.setter
    def id(self, value):
        self._id = value

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @sprite.setter
    def sprite(self, value):
        self._sprite = value

    @modelo_3d.setter
    def modelo_3d(self, value):
        self._modelo_3d = value
