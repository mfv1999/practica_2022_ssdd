"""Submodule containing the CLI command handlers."""

import logging

import sys
import signal
import hashlib
import getpass
import Ice 
import IceStorm
import iceflixrtsp
import IceFlix


from iceflix.main import MainApp
from typing import Self
from os import system
from time import sleep 
class client(Ice.Application):
    """ INIT METHOD """
    def  __init__ (self):
        super().__init__()
        self._usurname_ = None
        self._password_hash_ = None
        self._logged = False
        self._admin_token_ = None
        self._user_token_ = None
        self._main_prx = None
        self._auth_prx = None  
        self._catlog_prx = None
        self._stream_provider_prx = None
        self._stream_controller_prx_ = None
        self._playing_media_ = False
        self._media_player_= iceflixrtsp.RTSPPlayer()
        self.refreshed_token_ = False
        self.revoke_topic_= None
        self.revoke_topic_prx = None
        self.revocations_subscriber = None
        self.revocations_subscriber_prx = None
        self.revocations_publisher = None 
        self.adapter = None

    """---------------------------------------------------------------------------------------------------"""
    """ aux methods """

    def set_main_proxy(self):
        """ este metodo establece el proxy del servicio main a usar"""
        proxy = input("introduce el proxy del servicio principal a usar")

        while proxy =="":
            proxy = input("introduce el proxy del servicio principal a usar")
        intentosDeConexion = 3
        try:
            main_proxy= self.communicator().stringToProxy(proxy)
            main_connection= IceFlix.MainPrx.checkedCast(main_proxy)
            self.adapter = self.communicator().createObjectAdapterWithEndpointd('ClientAdapter','tcp')
        except Ice.ConnectionRefusedException:
            print("la conexion no ha sido posible")
            input()
            sys.exit(0)
        else: 
            print("conectando al servicio principal")
            while intentosDeConexion >0:
                try:
                    check = main_connection.ice_isA("::IceFlix: :Main")
                    if (check):
                        break
                except Ice.ConnectionRefusedException:
                    print("no ha sido posible conectar con el servicio main, intendo de nuevo")
                    intentosDeConexion -=1
                    if (intentosDeConexion == 0 ):
                        print ("intentos macximos de conexion alcanzados")
                        return signal.SIGINT
                    sleep(5)
        self._main_prx = main_connection

    def get_admin_token(self):
        token = input("Introduce el token de administracion")

        is_admin= self._main_prx_isAdmin(token)
        if(is_admin):
            self._admin_token_= token
        else:
            self._admin_token_= None
            print("ese token no es de administrador ")
            input("pulsa enter para continuar")


        """------------------------------------------------------------------------------------------------------"""
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
        self.set_main_proxy()
        self.adapter_activate()

        """ opciones una vez iniciado con el proxy bien """

        while 1:
            print("Opciones disponibles")
            print("1. introducir token de administrador")
            print("2. login")
            print("3. logout")
            print("4 servicio de catalogo")
            print("5 servicio de autenticacion")
            print("6. reproducir archivo (servicio file)")
            print("7. salir del cliente")

            if self._playing_media_:
                print("8. detener reproduccion")
                max_option=8 


            opcion= input(self.create_prompt("MainService"))
            while not opcion.isdigit() or int(opcion)<1 or int(opcion)> 6:
                if (opcion== ""):
                    opcion= input(self.create_prompt("MainService"))     
                else:
                    opcion = input("Inserta una opcion valida:")

            if opcion == "1":
                self.get_admin_token() 
            elif opcion =="2":
                self.login()
            elif opcion == "3":
                self.logout()
            elif opcion == "4":
                self.catalog_service()
            elif opcion == "5":
                self.authenticator_service()
            elif opcion=="6":
                self.stream_provider_service()
            elif opcion == "7":
                print("Gracias por usar la aplicacion")
                return signal.SIGINT
            elif opcion == "8":
                self._media_player_.stop()
                self._stream_controller_prx_.stop()
                self._playing_media_ =False
        

        sys.exit(0)
