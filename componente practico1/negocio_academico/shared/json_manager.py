
import json
import os


class GestorJSON:
    def __init__(self, archivo):
        self.archivo = archivo

    def leer(self):
        if not os.path.exists(self.archivo):
            return []

        with open(self.archivo, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def guardar(self, datos):
        carpeta = os.path.dirname(self.archivo)

        if carpeta:
            os.makedirs(carpeta, exist_ok=True)

        with open(self.archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
