
"""Controladores y menus del negocio academico."""

from models_academico import (
    Estudiante,
    Docente,
    Materia,
    Matricula
)

from views import CrudBase, MenuCRUD

from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    confirmar
)


# =====================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================

class EstudianteController(CrudBase):

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    NOMBRE = "estudiante"

    CAMPOS_BUSCABLES = (
        "nombre",
        "apellido",
        "email",
        "carnet"
    )

    def validar(self, datos, id_actual=None):

        for campo in self.MODELO.OBLIGATORIOS:
            if not str(datos.get(campo, "")).strip():
                raise ValueError(
                    f"El campo {campo} es obligatorio"
                )

        carnet = str(datos["carnet"]).strip().upper()
        email = str(datos["email"]).strip().lower()

        for estudiante in self.listar():

            if estudiante.id == id_actual:
                continue

            if estudiante.carnet == carnet:
                raise ValueError(
                    "El carnet ya esta registrado"
                )

            if estudiante.email == email:
                raise ValueError(
                    "El correo ya esta registrado"
                )

    def eliminar(self, id_registro):
        for matricula in MatriculaController().listar():
            if matricula.estudiante_id == int(id_registro):
                raise ValueError(
                    "No se puede eliminar un estudiante "
                    "que tiene matriculas"
                )

        return super().eliminar(id_registro)


# =====================================================
# CONTROLADOR DE DOCENTES
# =====================================================

class DocenteController(CrudBase):

    MODELO = Docente
    ARCHIVO = "data/docentes.json"
    NOMBRE = "docente"

    CAMPOS_BUSCABLES = (
        "nombre",
        "apellido",
        "email",
        "especialidad"
    )

    def validar(self, datos, id_actual=None):

        for campo in self.MODELO.OBLIGATORIOS:
            if not str(datos.get(campo, "")).strip():
                raise ValueError(
                    f"El campo {campo} es obligatorio"
                )

        email = str(datos["email"]).strip().lower()

        for docente in self.listar():

            if docente.id == id_actual:
                continue

            if docente.email == email:
                raise ValueError(
                    "El correo del docente ya existe"
                )

    def eliminar(self, id_registro):
        for materia in MateriaController(self).listar():
            if materia.docente_id == int(id_registro):
                raise ValueError(
                    "No se puede eliminar un docente "
                    "asignado a una materia"
                )

        return super().eliminar(id_registro)


# =====================================================
# CONTROLADOR DE MATERIAS
# =====================================================

class MateriaController(CrudBase):

    MODELO = Materia
    ARCHIVO = "data/materias.json"
    NOMBRE = "materia"

    CAMPOS_BUSCABLES = (
        "nombre",
        "codigo"
    )

    def __init__(self, docentes=None):
        super().__init__()

        self.docentes = (
            docentes
            if docentes is not None
            else DocenteController()
        )

    def validar(self, datos, id_actual=None):

        for campo in self.MODELO.OBLIGATORIOS:
            if not str(datos.get(campo, "")).strip():
                raise ValueError(
                    f"El campo {campo} es obligatorio"
                )

        codigo = str(datos["codigo"]).strip().upper()

        for materia in self.listar():

            if materia.id == id_actual:
                continue

            if materia.codigo == codigo:
                raise ValueError(
                    "El codigo de materia ya existe"
                )

        creditos = datos.get("creditos", 0)

        try:
            creditos = int(creditos or 0)
        except (ValueError, TypeError):
            raise ValueError(
                "Los creditos deben ser un numero"
            )

        if not 0 <= creditos <= 10:
            raise ValueError(
                "Los creditos deben estar entre 0 y 10"
            )

        docente_id = datos.get("docente_id")

        if docente_id not in (None, "", "0"):

            if self.docentes.obtener(docente_id) is None:
                raise ValueError(
                    "El docente asignado no existe"
                )

    def asignar_docente(self, materia_id, docente_id):

        materia = self.obtener(materia_id)

        if materia is None:
            raise ValueError(
                "La materia no existe"
            )

        if self.docentes.obtener(docente_id) is None:
            raise ValueError(
                "El docente no existe"
            )

        return self.actualizar(
            materia_id,
            {"docente_id": docente_id}
        )

    def materias_de_docente(self, docente_id):

        return [
            materia
            for materia in self.listar()
            if materia.docente_id == int(docente_id)
        ]

    def eliminar(self, id_registro):
        for matricula in MatriculaController().listar():
            if matricula.materia_id == int(id_registro):
                raise ValueError(
                    "No se puede eliminar una materia "
                    "que tiene matriculas"
                )

        return super().eliminar(id_registro)


# =====================================================
# CONTROLADOR DE MATRICULAS
# =====================================================

class MatriculaController(CrudBase):

    MODELO = Matricula
    ARCHIVO = "data/matriculas.json"
    NOMBRE = "matricula"

    CAMPOS_BUSCABLES = ("periodo",)

    def __init__(self, estudiantes=None, materias=None):
        super().__init__()

        self.estudiantes = (
            estudiantes
            if estudiantes is not None
            else EstudianteController()
        )

        self.materias = (
            materias
            if materias is not None
            else MateriaController()
        )

    # -------------------------------------------------
    # VALIDAR MATRICULA
    # -------------------------------------------------

    def validar(self, datos, id_actual=None):

        estudiante_id = datos.get("estudiante_id")
        materia_id = datos.get("materia_id")

        periodo = (
            str(datos.get("periodo") or "2026-1")
            .strip()
        )

        if self.estudiantes.obtener(estudiante_id) is None:
            raise ValueError(
                "El estudiante no existe"
            )

        if self.materias.obtener(materia_id) is None:
            raise ValueError(
                "La materia no existe"
            )

        for matricula in self.listar():

            if matricula.id == id_actual:
                continue

            if (
                matricula.estudiante_id == int(estudiante_id)
                and matricula.materia_id == int(materia_id)
                and matricula.periodo == periodo
            ):
                raise ValueError(
                    "El estudiante ya esta matriculado "
                    "en esa materia y periodo"
                )

    # -------------------------------------------------
    # ACTUALIZAR SIN PERDER LAS NOTAS
    # -------------------------------------------------

    def actualizar(self, id_registro, cambios):

        actual = self.obtener(id_registro)

        if actual is None:
            raise ValueError(
                "La matricula no existe"
            )

        datos = actual.a_diccionario()

        for campo, valor in cambios.items():
            if campo in self.MODELO.CAMPOS:
                datos[campo] = valor

        self.validar(datos, actual.id)

        actualizado = Matricula.desde_diccionario(datos)

        objetos = self.listar()

        for indice, objeto in enumerate(objetos):
            if objeto.id == actual.id:
                objetos[indice] = actualizado
                break

        self.guardar(objetos)

        return actualizado

    # -------------------------------------------------
    # AGREGAR NOTA
    # -------------------------------------------------

    def agregar_nota(
        self, matricula_id, tipo, valor, peso=1
    ):

        matricula = self.obtener(matricula_id)

        if matricula is None:
            raise ValueError(
                "La matricula no existe"
            )

        nota = matricula.agregar_nota(
            tipo, valor, peso
        )

        objetos = self.listar()

        for indice, objeto in enumerate(objetos):

            if objeto.id == matricula.id:
                objetos[indice] = matricula
                break

        self.guardar(objetos)

        return nota

    # -------------------------------------------------
    # BOLETIN DEL ESTUDIANTE
    # -------------------------------------------------

    def boletin(self, estudiante_id):

        estudiante = self.estudiantes.obtener(
            estudiante_id
        )

        if estudiante is None:
            raise ValueError(
                "El estudiante no existe"
            )

        matriculas = [
            matricula
            for matricula in self.listar()
            if matricula.estudiante_id == estudiante.id
        ]

        lineas = [
            "=" * 55,
            "BOLETIN ACADEMICO",
            "=" * 55,
            f"Estudiante: {estudiante.nombre_completo}",
            f"Carnet: {estudiante.carnet}",
            "-" * 55
        ]

        if not matriculas:
            lineas.append(
                "El estudiante no tiene matriculas"
            )
            return "\n".join(lineas)

        promedios = []

        for matricula in matriculas:

            materia = self.materias.obtener(
                matricula.materia_id
            )

            nombre_materia = (
                materia.nombre
                if materia is not None
                else "Materia no encontrada"
            )

            lineas.append(
                f"Materia: {nombre_materia}"
            )

            lineas.append(
                f"Periodo: {matricula.periodo}"
            )

            if matricula.notas:
                for nota in matricula.notas:
                    lineas.append(
                        f"  {nota.tipo}: {nota.valor}"
                        f" (peso {nota.peso:g})"
                    )

                promedios.append(matricula.promedio)

            else:
                lineas.append("  Sin notas")

            lineas.append(
                f"Promedio: {matricula.promedio:.2f}"
            )

            lineas.append(
                f"Estado: {matricula.estado}"
            )

            lineas.append("-" * 55)

        if promedios:
            promedio_general = (
                sum(promedios) / len(promedios)
            )
        else:
            promedio_general = 0

        lineas.append(
            f"Promedio general: {promedio_general:.2f}"
        )

        return "\n".join(lineas)

    # -------------------------------------------------
    # REPORTE DE ESTUDIANTES REPROBADOS
    # -------------------------------------------------

    def estudiantes_reprobados(self):

        resultados = []

        for matricula in self.listar():

            if matricula.estado != "Reprobado":
                continue

            estudiante = self.estudiantes.obtener(
                matricula.estudiante_id
            )

            materia = self.materias.obtener(
                matricula.materia_id
            )

            if estudiante is None or materia is None:
                continue

            resultados.append({
                "estudiante": estudiante.nombre_completo,
                "materia": materia.nombre,
                "promedio": matricula.promedio,
                "periodo": matricula.periodo
            })

        return resultados


# =====================================================
# MENU ESPECIAL DE MATRICULAS
# =====================================================

class MenuMatriculas(MenuCRUD):

    def __init__(self, controlador):
        super().__init__(controlador)

    # -------------------------------------------------
    # REGISTRAR MATRICULA
    # -------------------------------------------------

    def crear(self):

        imprimir_titulo("REGISTRAR MATRICULA")

        print("\nESTUDIANTES DISPONIBLES")
        self.mostrar_registros(
            self._controlador.estudiantes.listar()
        )

        print("\nMATERIAS DISPONIBLES")
        self.mostrar_registros(
            self._controlador.materias.listar()
        )

        try:
            estudiante_id = input(
                "\nID del estudiante: "
            ).strip()

            materia_id = input(
                "ID de la materia: "
            ).strip()

            periodo = input(
                "Periodo [2026-1]: "
            ).strip()

            datos = {
                "estudiante_id": estudiante_id,
                "materia_id": materia_id,
                "periodo": periodo or "2026-1"
            }

            matricula = self._controlador.crear(datos)

            imprimir_exito(
                "Matricula registrada correctamente"
            )

            print(matricula)

        except (ValueError, TypeError) as error:
            imprimir_error(str(error))

    # -------------------------------------------------
    # AGREGAR NOTA
    # -------------------------------------------------

    def agregar_nota(self):

        imprimir_titulo("AGREGAR NOTA")

        self.mostrar_registros(
            self._controlador.listar()
        )

        try:
            matricula_id = input(
                "\nID de la matricula: "
            ).strip()

            print("\nTIPOS DE NOTA")
            print("1. Deber")
            print("2. Leccion")
            print("3. Examen")

            opcion = input(
                "Seleccione el tipo: "
            ).strip()

            tipos = {
                "1": "deber",
                "2": "lección",
                "3": "examen"
            }

            if opcion not in tipos:
                raise ValueError(
                    "Tipo de nota no valido"
                )

            valor = input(
                "Calificacion (0-20): "
            ).strip()

            peso = input(
                "Peso de la nota [1]: "
            ).strip()

            nota = self._controlador.agregar_nota(
                matricula_id,
                tipos[opcion],
                valor,
                peso or 1
            )

            imprimir_exito(
                "Nota agregada correctamente"
            )

            print(nota)

        except (ValueError, TypeError) as error:
            imprimir_error(str(error))

    # -------------------------------------------------
    # MOSTRAR BOLETIN
    # -------------------------------------------------

    def ver_boletin(self):

        imprimir_titulo("BOLETIN ACADEMICO")

        self.mostrar_registros(
            self._controlador.estudiantes.listar()
        )

        estudiante_id = input(
            "\nID del estudiante: "
        ).strip()

        try:
            texto = self._controlador.boletin(
                estudiante_id
            )

            print("\n" + texto)

        except (ValueError, TypeError) as error:
            imprimir_error(str(error))

    # -------------------------------------------------
    # REPORTE DE REPROBADOS
    # -------------------------------------------------

    def ver_reprobados(self):

        imprimir_titulo("ESTUDIANTES REPROBADOS")

        resultados = (
            self._controlador.estudiantes_reprobados()
        )

        if not resultados:
            imprimir_info(
                "No hay estudiantes reprobados"
            )
            return

        for registro in resultados:
            print(
                f"\nEstudiante: {registro['estudiante']}"
            )

            print(
                f"Materia: {registro['materia']}"
            )

            print(
                f"Promedio: {registro['promedio']}"
            )

            print(
                f"Periodo: {registro['periodo']}"
            )

    # -------------------------------------------------
    # MOSTRAR OPCIONES
    # -------------------------------------------------

    def mostrar_opciones(self):

        imprimir_titulo("MENU DE MATRICULAS")

        print("1. Registrar matricula")
        print("2. Listar matriculas")
        print("3. Buscar matriculas")
        print("4. Consultar por ID")
        print("5. Actualizar matricula")
        print("6. Eliminar matricula")
        print("7. Agregar nota")
        print("8. Ver boletin")
        print("9. Estudiantes reprobados")
        print("0. Volver")

    # -------------------------------------------------
    # EJECUTAR MENU
    # -------------------------------------------------

    def ejecutar(self):

        while True:

            self.mostrar_opciones()

            opcion = input(
                "\nSeleccione una opcion: "
            ).strip()

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

            elif opcion == "7":
                self.agregar_nota()

            elif opcion == "8":
                self.ver_boletin()

            elif opcion == "9":
                self.ver_reprobados()

            elif opcion == "0":
                break

            else:
                imprimir_error(
                    "Opcion no valida"
                )
