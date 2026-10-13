
"""Programa principal del sistema academico."""

from views import MenuCRUD

from views_academico import (
    EstudianteController,
    DocenteController,
    MateriaController,
    MatriculaController,
    MenuMatriculas
)

from shared.herramientas import (
    imprimir_titulo,
    imprimir_error,
    imprimir_info
)


# =====================================================
# MENU PRINCIPAL DEL SISTEMA
# =====================================================

class MenuPrincipal:

    def __init__(self):

        self.estudiantes = EstudianteController()
        self.docentes = DocenteController()

        self.materias = MateriaController(
            self.docentes
        )

        self.matriculas = MatriculaController(
            self.estudiantes,
            self.materias
        )

        self.menu_estudiantes = MenuCRUD(
            self.estudiantes
        )

        self.menu_docentes = MenuCRUD(
            self.docentes
        )

        self.menu_materias = MenuCRUD(
            self.materias
        )

        self.menu_matriculas = MenuMatriculas(
            self.matriculas
        )

    # -------------------------------------------------
    # MOSTRAR OPCIONES PRINCIPALES
    # -------------------------------------------------

    def mostrar_opciones(self):

        imprimir_titulo(
            "SISTEMA DE NEGOCIO ACADEMICO"
        )

        print("1. Estudiantes")
        print("2. Docentes")
        print("3. Materias")
        print("4. Matriculas y notas")
        print("0. Salir")

    # -------------------------------------------------
    # EJECUTAR EL PROGRAMA
    # -------------------------------------------------

    def ejecutar(self):

        while True:

            self.mostrar_opciones()

            opcion = input(
                "\nSeleccione una opcion: "
            ).strip()

            if opcion == "1":
                self.menu_estudiantes.ejecutar()

            elif opcion == "2":
                self.menu_docentes.ejecutar()

            elif opcion == "3":
                self.menu_materias.ejecutar()

            elif opcion == "4":
                self.menu_matriculas.ejecutar()

            elif opcion == "0":
                imprimir_info(
                    "Gracias por utilizar el sistema"
                )
                break

            else:
                imprimir_error(
                    "Opcion no valida"
                )


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == "__main__":
    programa = MenuPrincipal()
    programa.ejecutar()
