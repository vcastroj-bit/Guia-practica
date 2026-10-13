
"""CRUD reutilizable y menu general del sistema academico."""

from abc import ABC, abstractmethod

from shared.json_manager import GestorJSON
from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    confirmar
)


# =====================================================
# CLASE ABSTRACTA CRUD BASE
# =====================================================

class CrudBase(ABC):
    """Controlador base para todas las entidades."""

    MODELO = None
    ARCHIVO = ""
    NOMBRE = "Registro"
    CAMPOS_BUSCABLES = ()

    def __init__(self):
        self._gestor = GestorJSON(self.ARCHIVO)

    # -------------------------------------------------
    # GUARDAR INFORMACION
    # -------------------------------------------------

    def guardar(self, objetos):
        datos = [
            objeto.a_diccionario()
            for objeto in objetos
        ]

        self._gestor.guardar(datos)

    # -------------------------------------------------
    # LISTAR REGISTROS
    # -------------------------------------------------

    def listar(self):
        datos = self._gestor.leer()

        return [
            self.MODELO.desde_diccionario(registro)
            for registro in datos
        ]

    # -------------------------------------------------
    # GENERAR EL SIGUIENTE ID
    # -------------------------------------------------

    def siguiente_id(self):
        objetos = self.listar()

        if not objetos:
            return 1

        return max(objeto.id for objeto in objetos) + 1

    # -------------------------------------------------
    # VALIDACION ABSTRACTA
    # -------------------------------------------------

    @abstractmethod
    def validar(self, datos, id_actual=None):
        """Cada controlador implementa sus reglas."""

    # -------------------------------------------------
    # PREPARAR DATOS
    # -------------------------------------------------

    def preparar(self, datos):
        """Permite preparar datos antes de crear."""
        return datos

    # -------------------------------------------------
    # CREAR REGISTRO
    # -------------------------------------------------

    def crear(self, datos):
        datos = self.preparar(datos.copy())

        self.validar(datos)

        nuevo = self.MODELO(
            self.siguiente_id(),
            **datos
        )

        objetos = self.listar()
        objetos.append(nuevo)

        self.guardar(objetos)

        return nuevo

    # -------------------------------------------------
    # BUSCAR REGISTRO POR ID
    # -------------------------------------------------

    def obtener(self, id_registro):
        try:
            id_registro = int(id_registro)
        except (TypeError, ValueError):
            return None

        for objeto in self.listar():
            if objeto.id == id_registro:
                return objeto

        return None

    # -------------------------------------------------
    # BUSCAR POR TEXTO
    # -------------------------------------------------

    def buscar(self, texto):
        texto = str(texto).strip().lower()

        resultados = []

        for objeto in self.listar():
            for campo in self.CAMPOS_BUSCABLES:
                valor = getattr(objeto, campo, "")

                if texto in str(valor).lower():
                    resultados.append(objeto)
                    break

        return resultados

    # -------------------------------------------------
    # ACTUALIZAR REGISTRO
    # -------------------------------------------------

    def actualizar(self, id_registro, cambios):
        actual = self.obtener(id_registro)

        if actual is None:
            raise ValueError("El registro no existe")

        datos = actual.a_diccionario()

        for campo, valor in cambios.items():
            if campo in self.MODELO.CAMPOS:
                datos[campo] = valor

        self.validar(datos, actual.id)

        nuevo = self.MODELO.desde_diccionario(datos)

        objetos = self.listar()

        for indice, objeto in enumerate(objetos):
            if objeto.id == actual.id:
                objetos[indice] = nuevo
                break

        self.guardar(objetos)

        return nuevo

    # -------------------------------------------------
    # ELIMINAR REGISTRO
    # -------------------------------------------------

    def eliminar(self, id_registro):
        actual = self.obtener(id_registro)

        if actual is None:
            raise ValueError("El registro no existe")

        objetos = [
            objeto for objeto in self.listar()
            if objeto.id != actual.id
        ]

        self.guardar(objetos)

        return True


# =====================================================
# CLASE MENU CRUD
# =====================================================

class MenuCRUD:
    """Menu reutilizable para los controladores."""

    def __init__(self, controlador):
        self._controlador = controlador

    # -------------------------------------------------
    # MOSTRAR REGISTROS
    # -------------------------------------------------

    def mostrar_registros(self, objetos):
        if not objetos:
            imprimir_info("No hay registros para mostrar")
            return

        for objeto in objetos:
            print(objeto)

    # -------------------------------------------------
    # PEDIR DATOS
    # -------------------------------------------------

    def pedir_datos(self, actuales=None):
        datos = {}

        for campo in self._controlador.MODELO.CAMPOS:
            obligatorio = (
                campo in self._controlador.MODELO.OBLIGATORIOS
            )

            if actuales is None:
                valor = input(f"{campo}: ").strip()

                if not valor and obligatorio:
                    raise ValueError(
                        f"El campo {campo} es obligatorio"
                    )

                if valor or obligatorio:
                    datos[campo] = valor

            else:
                anterior = getattr(actuales, campo, "")

                if anterior is None:
                    anterior = ""

                valor = input(
                    f"{campo} [{anterior}]: "
                ).strip()

                if valor:
                    datos[campo] = valor

        return datos

    # -------------------------------------------------
    # CREAR
    # -------------------------------------------------

    def crear(self):
        imprimir_titulo(
            f"REGISTRAR {self._controlador.NOMBRE.upper()}"
        )

        try:
            datos = self.pedir_datos()

            nuevo = self._controlador.crear(datos)

            imprimir_exito("Registro creado correctamente")
            print(nuevo)

        except (ValueError, TypeError) as error:
            imprimir_error(str(error))

    # -------------------------------------------------
    # LISTAR
    # -------------------------------------------------

    def listar(self):
        imprimir_titulo(
            f"LISTADO DE {self._controlador.NOMBRE.upper()}"
        )

        objetos = self._controlador.listar()

        self.mostrar_registros(objetos)

    # -------------------------------------------------
    # BUSCAR
    # -------------------------------------------------

    def buscar(self):
        imprimir_titulo("BUSCAR REGISTRO")

        texto = input("Texto que desea buscar: ").strip()

        resultados = self._controlador.buscar(texto)

        self.mostrar_registros(resultados)

    # -------------------------------------------------
    # VER POR ID
    # -------------------------------------------------

    def ver_por_id(self):
        imprimir_titulo("CONSULTAR POR ID")

        id_registro = input("Ingrese el ID: ").strip()

        objeto = self._controlador.obtener(id_registro)

        if objeto is None:
            imprimir_error("Registro no encontrado")
            return

        print(objeto)

    # -------------------------------------------------
    # ACTUALIZAR
    # -------------------------------------------------

    def actualizar(self):
        imprimir_titulo("ACTUALIZAR REGISTRO")

        id_registro = input("Ingrese el ID: ").strip()

        actual = self._controlador.obtener(id_registro)

        if actual is None:
            imprimir_error("Registro no encontrado")
            return

        print("Presione ENTER para conservar un dato.")

        try:
            cambios = self.pedir_datos(actual)

            actualizado = self._controlador.actualizar(
                id_registro,
                cambios
            )

            imprimir_exito("Registro actualizado")
            print(actualizado)

        except (ValueError, TypeError) as error:
            imprimir_error(str(error))

    # -------------------------------------------------
    # ELIMINAR
    # -------------------------------------------------

    def eliminar(self):
        imprimir_titulo("ELIMINAR REGISTRO")

        id_registro = input("Ingrese el ID: ").strip()

        objeto = self._controlador.obtener(id_registro)

        if objeto is None:
            imprimir_error("Registro no encontrado")
            return

        print(objeto)

        if not confirmar("¿Desea eliminarlo? (s/n): "):
            imprimir_info("Operacion cancelada")
            return

        try:
            self._controlador.eliminar(id_registro)
            imprimir_exito("Registro eliminado")

        except (ValueError, TypeError) as error:
            imprimir_error(str(error))

    # -------------------------------------------------
    # MOSTRAR OPCIONES DEL MENU
    # -------------------------------------------------

    def mostrar_opciones(self):
        imprimir_titulo(
            f"MENU DE {self._controlador.NOMBRE.upper()}"
        )

        print("1. Registrar")
        print("2. Listar")
        print("3. Buscar")
        print("4. Consultar por ID")
        print("5. Actualizar")
        print("6. Eliminar")
        print("0. Volver")

    # -------------------------------------------------
    # EJECUTAR MENU
    # -------------------------------------------------

    def ejecutar(self):
        while True:
            self.mostrar_opciones()

            opcion = input("\nSeleccione una opcion: ").strip()

            if opcion == "1":
                self.crear()

            elif opcion == "2":
                self.listar()

            elif opcion == "3":
                self.buscar()

            elif opcion == "4":
                self.ver_por_id()

            elif opcion == "5":
                self.actualizar()

            elif opcion == "6":
                self.eliminar()

            elif opcion == "0":
                break

            else:
                imprimir_error("Opcion no valida")
