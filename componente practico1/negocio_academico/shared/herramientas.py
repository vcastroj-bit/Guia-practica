
"""Funciones auxiliares para la interfaz de consola."""


def imprimir_titulo(titulo):
    print('\n' + '=' * 55)
    print(titulo.center(55))
    print('=' * 55)


def imprimir_exito(mensaje):
    print('✓', mensaje)


def imprimir_error(mensaje):
    print('✗', mensaje)


def imprimir_info(mensaje):
    print('•', mensaje)


def confirmar(texto='¿Confirmar? (s/n): '):
    return input(texto).strip().lower() in ('s', 'si', 'sí')
