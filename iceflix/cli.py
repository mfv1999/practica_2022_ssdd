"""Submodule containing the CLI command handlers."""

import logging

import sys
import Ice 

from iceflix.main import MainApp
from typing import Self
from os import system



def setup_logging():
    """Configure the logging."""
    logging.basicConfig(level=logging.DEBUG)


def main_service():
    """Handles the `mainservice` CLI command."""
    setup_logging()
    logging.info("Main service starting...")
    sys.exit(MainApp().main(sys.argv))


def catalog_service():
    """Handles the `catalogservice` CLI command."""
    print("Catalog service")
    sys.exit(0)


def streamprovider_service():
    """Handles the `streamingservice` CLI command."""
    print("Streaming service")
    sys.exit(0)


def authentication_service():
    """Handles the `authenticationservice` CLI command."""
    print("Authentication service")
    sys.exit(0)


def client(self):
    """Handles the IceFlix client CLI command."""
    """ primero el cliente pide el proxy del main a usar , despues da opciones a realizar """
    print("Starting IceFlix client...")

    print("iniciando sistema")

    """ pedir proxy del main """

    """ opciones una vez iniciado con el proxy bien """

    while 1:
        print("Opciones disponibles")
        print("1. Autenticarse")
        print("2. buscar en el catalogo")
        print("3. edicion del catalogo")
        print("4 reproducir medios")
        print("5 operaciones administrativas")
        print("6. cerrar sesión")


        opcion= input(self.create_prompt("MainService"))
        while not opcion.isdigit() or int(opcion)<1 or int(opcion)> 6:
            if (opcion== ""):
                opcion= input(self.create_prompt("MainService"))     
            else:
                opcion = input("Inserta una opcion valida:")

        if opcion == 1:
            """ settup loggin o autenticator ?""" 
        elif opcion ==2:
            self.catalog_service()
        elif opcion == 3:
            """ catalog again ?"""

    sys.exit(0)
