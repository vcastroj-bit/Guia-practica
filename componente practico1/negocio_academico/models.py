
from abc import ABC, abstractmethod


# =====================================================
# CLASE ABSTRACTA BASE DE LOS MODELOS
# =====================================================

class ModeloBase(ABC):
    """Clase base para todos los modelos del sistema."""

    CAMPOS = ()
    OBLIGATORIOS = ()

    def __init__(self, id_registro):
        self.__id = int(id_registro)

    @property
    def id(self):
        return self.__id

    @staticmethod
    def limpiar(texto):
        return str(texto).strip()

    @abstractmethod
    def a_diccionario(self):
        """Convierte un objeto en diccionario."""

    @abstractmethod
    def etiqueta(self):
        """Devuelve una descripción del objeto."""

    @classmethod
    def desde_diccionario(cls, datos):
        valores = {
            campo: datos.get(campo, "")
            for campo in cls.CAMPOS
        }

        return cls(datos["id"], **valores)

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================
# CLASE ABSTRACTA PERSONA
# =====================================================

class Persona(ModeloBase):
    """Clase base para estudiantes y docentes."""

    CAMPOS = ("nombre", "apellido", "email")
    OBLIGATORIOS = ("nombre", "apellido", "email")

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)

        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    # -------------------------------------------------
    # VALIDACION DEL CORREO ELECTRONICO
    # -------------------------------------------------

    @staticmethod
    def es_email_valido(texto):
        texto = str(texto).strip()

        if texto.count("@") != 1:
            return False

        usuario, dominio = texto.split("@")

        return (
            len(usuario) > 0
            and "." in dominio
            and not dominio.endswith(".")
        )

    # -------------------------------------------------
    # PROPIEDAD NOMBRE
    # -------------------------------------------------

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Persona.limpiar(valor)

        if not valor:
            raise ValueError("El nombre es obligatorio")

        self.__nombre = valor.title()

    # -------------------------------------------------
    # PROPIEDAD APELLIDO
    # -------------------------------------------------

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, valor):
        valor = Persona.limpiar(valor)

        if not valor:
            raise ValueError("El apellido es obligatorio")

        self.__apellido = valor.title()

    # -------------------------------------------------
    # PROPIEDAD EMAIL
    # -------------------------------------------------

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        valor = Persona.limpiar(valor)

        if not Persona.es_email_valido(valor):
            raise ValueError(
                f"Correo electronico invalido: '{valor}'"
            )

        self.__email = valor.lower()

    # -------------------------------------------------
    # NOMBRE COMPLETO
    # -------------------------------------------------

    @property
    def nombre_completo(self):
        return f"{self.__nombre} {self.__apellido}"

    # -------------------------------------------------
    # CONVERTIR OBJETO A DICCIONARIO
    # -------------------------------------------------

    def a_diccionario(self):
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "apellido": self.__apellido,
            "email": self.__email
        }
