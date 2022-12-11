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

    def create_prompt(self, servicio: str):
        if self._username_ and self._admin_token_:
            if self._playing_media_:
                return "Admin_Playing>>" + servicio + "@" + self._username_ + "> "
            return "Admin>>" + servicio + "@" + self._username_ + "> "
        if self._username_:
            if self._playing_media_:
                return "Playing>>" + servicio + "@" + self._username_ + "> "
            return servicio + "@" + self._username_ + "> "
        if self._admin_token_:
            return "Admin>>" + servicio + "@Anónimo> "
        return servicio + "@Anónimo> "



    def name_searching(self):
        ''' Implementa la búsqueda de videos por nombre '''
        media_list = []
        full_title = False
        print("\nOpciones disponibles:")
        print("1. Buscar medio por nombre completo")
        print("2. Buscar medio por parte del nombre\n")
        option = input("Opción (1/2): ")
        while not option.isdigit() or int(option) < 1 or int(option) > 2:
            option = input("Inserta una opción válida: ")

        if option == "1":
            full_title = True
        elif option == "2":
            full_title = False

        title = input("\nInsertar titulo: ")
        while title == "":
            title = input("\nInsertar titulo: ")

        id_list = self._catalog_prx_.getTilesByName(title, full_title)

        if len(id_list) > 0:
            for title_id in id_list:
                try:
                    media_list.append(self._catalog_prx_.getTile(title_id, self._user_token_))
                except IceFlix.Unauthorized:
                    print("Usuario no autorizado")
                except(IceFlix.WrongMediaId, IceFlix.TemporaryUnavailable):
                    pass
        else:
            return []

        return media_list


    def tag_searching(self):
        media_list = []
        tag_list = self.ask_for_tags()

        if not tag_list:
            return -1

        option = input("¿Quieres que tu búsqueda coincida con todas tus etiquetas? (s/n): ")
        while option not in ('s', 'n'):
            option = input("Inserta una opción válida: ")

        all_tags = None
        if option == "s":
            all_tags = True
        elif option == "n":
            all_tags = False

        try:
            id_list = self._catalog_prx_.getTilesByTags(tag_list, all_tags, self._user_token_)
        except IceFlix.Unauthorized:
            print("Usuario no autorizado")
            return 0

        if len(id_list) > 0:
            for title_id in id_list:
                try:
                    media_list.append(self._catalog_prx_.getTile(title_id, self._user_token_))
                except(IceFlix.WrongMediaId, IceFlix.TemporaryUnavailable): # pylint: disable=invalid-name
                    print("No hay un servicio de catalogo disponible")
                except IceFlix.WrongMediaId:
                    print("El video no se encuentra en el catalogo")
        else:
            return -1

        return media_list

    def ask_for_tags():
        ''' Implementa la petición de tags por parte del usuario '''
        tag_list = []
        print("Inserta sus etiquetas. Para salir, dejar en blanco:")

        while 1:
            tag = input("Etiqueta: ")
            if tag == "":
                break
            tag_list.append(tag)

        return tag_list
    
    def add_tags(self, media_object):
        
        tags_list = self.ask_for_tags()
        try:
            self._catalog_prx_.addTags(media_object.mediaId, tags_list, self._user_token_)
        except IceFlix.Unauthorized: # pylint: disable=invalid-name
            print("Usuario no autorizado")
            input()
        except IceFlix.WrongMediaId:
            print("El video no se encuentra en el catalogo")
            input()
        else:
            print("Etiquetas añadidas correctamente")
            input("Pulsa enter para continuar...")

        return 0


    def remove_tags(self, media_object):
       
        tags_list = self.ask_for_tags()
        try:
            self._catalog_prx_.removeTags(media_object.mediaId, tags_list, self._user_token_)
        except IceFlix.Unauthorized: # pylint: disable=invalid-name
            print("Usuario no autorizado")
            input()
        except IceFlix.WrongMediaId:
            print("El video no se encuentra en el catalogo")
            input()
        else:
            print("Etiquetas eliminadas correctamente")
            input("Pulsa enter para continuar...")
        return 0   

    def login(self):
        ''' Implementa la función de iniciar sesión '''
        if self.logged:
            print("Ya hay una sesión activa")
            input()
            return
        user = input("Nombre de usuario: ")
        password = getpass.getpass("Contraseña: ")
        hash_password = hashlib.sha256(password.encode()).hexdigest()
        self._password_hash_ = hash_password
        try:
            self._auth_prx_ = self._main_prx_.getAuthenticator()
            self._user_token_ = self._auth_prx_.refreshAuthorization(user, hash_password)
            self.refreshed_token = True

            communicator = self.communicator()
            topic_manager = IceStorm.TopicManagerPrx.checkedCast(  #pylint: disable=no-member
                communicator.propertyToProxy("IceStorm.TopicManager"))
            try:
                topic = topic_manager.create(REVOCATIONS_TOPIC)
            except IceStorm.TopicExists:  #pylint: disable=no-member
                topic = topic_manager.retrieve(REVOCATIONS_TOPIC)
            self.revocations_publisher = RevocationsSender(topic)
            self.revocations_subscriber = RevocationsListener(self)
            self.revocations_subscriber_prx = self.adapter.addWithUUID(self.revocations_subscriber)
            self.revoke_topic_prx = topic.subscribeAndGetPublisher({},
                                                                   self.revocations_subscriber_prx)
            self.revoke_topic = topic
            self.logged = True

        except IceFlix.TemporaryUnavailable:
            print("No hay ningún servicio de Autenticación disponible")
            input()
            return

        except IceFlix.Unauthorized:
            print("Credenciales no válidas")
            input()
            return
        self._username_ = user
        input("Registrado correctamente. Pulsa Enter para continuar...")
    
    
    def logout(self):
        ''' Implementa la función de cerrar sesión '''
        if self.logged:
            self._username_ = None
            self._user_token_ = None
            self._password_hash_ = None
            self.revoke_topic.unsubscribe(self.revocations_subscriber_prx)
            self.revoke_topic_prx = None
            self.revoke_topic = None
            self.revocations_subscriber = None
            self.revocations_listener = None
            self.logged = False
        else:
            input("No hay ninguna sesión iniciada. Pulsa Enter para continuar...")

    
        """------------------------------------------------------------------------------------------------------"""
    def setup_logging():
        """Configure the logging."""
        logging.basicConfig(level=logging.DEBUG)


    def main_service():
        """Handles the `mainservice` CLI command."""
        setup_logging()
        logging.info("Main service starting...")
        sys.exit(MainApp().main(sys.argv))


    def catalog_service(self):
        try:
            self._catalog_prx_ = self._main_prx_.getCatalog()
        except IceFlix.TemporaryUnavailable:
            print("No hay ningún servicio de Catálogo disponible")
            return 0

        while 1:
            system("clear")
            self.format_prompt()  #pylint: disable=too-many-function-args
            max_option = 3
            print("Opciones disponibles:")
            print("1. Búsqueda por nombre")
            print("2. Búsqueda por etiquetas")
            print("3. Volver\n")
            if self._playing_media_:
                print("4. Detener reproducción")
                max_option = 4

            option = input(self.create_prompt("CatalogService"))
            while not option.isdigit() or int(option) < 1 or int(option) > max_option:
                if option == "":
                    option = input(self.create_prompt("CatalogService"))
                else:
                    option = input("Inserta una opción válida: ")

            if option == "1":
                media_list = self.name_searching()
                if len(media_list) == 0:
                    print("\nNo se han encontrado resultados")
                    input("Pulsa enter para continuar...")
                    continue

                selected_media = self.select_media(media_list)
                if selected_media == -1:
                    continue

                try:
                    self.ask_function(selected_media)
                except IceFlix.Unauthorized: # pylint: disable=invalid-name
                    print("Usuario no autorizado")
                    input("Presiona Enter para continuar...")
                except IceFlix.WrongMediaId:
                    print("El video no se encuentra en el catalogo")
                    input("Presiona Enter para continuar...")
                else:
                    continue

            elif option == "2":
                media_list = self.tag_searching()
                if media_list == -1:
                    print("\nNo se han encontrado resultados")
                    input("Pulsa enter para continuar...")
                    continue
                if media_list == 0:
                    input("Pulsa enter para continuar...")
                    continue

                selected_media = self.select_media(media_list)
                if selected_media == -1:
                    continue

                try:
                    self.ask_function(selected_media)
                except IceFlix.Unauthorized: # pylint: disable=invalid-name
                    print("Usuario no autorizado")
                    input("Presiona Enter para continuar...")
                except IceFlix.WrongMediaId:
                    print("El video no se encuentra en el catalogo")
                    input("Presiona Enter para continuar...")
                else:
                    continue

            elif option == "3":
                return 0

            elif option == "4":
                self._media_player_.stop()
                self._stream_controller_prx_.stop()
                self._playing_media_ = False

    def streamprovider_service():
        """Handles the `streamingservice` CLI command."""
        print("Streaming service")
        sys.exit(0)


    def authentication_service(self):
        while 1:
            system("clear")
            self.format_prompt()  #pylint: disable=too-many-function-args
            print("1. Añadir usuario")
            print("2. Eliminar usuario")
            print("3. Salir")

            option = input(self.create_prompt("AuthenticatorService"))
            while not option.isdigit() or int(option) < 1 or int(option) > 3:
                option = input("Inserta una opción válida: ")

            if option == "1":
                new_user = input("Introduce el nuevo nombre de usuario: ")
                new_password = getpass.getpass("Nueva Password: ")
                new_hash_password = hashlib.sha256(new_password.encode()).hexdigest()
                try:
                    auth = self._main_prx_.getAuthenticator()
                    auth.addUser(new_user, new_hash_password, self._admin_token_)
                except IceFlix.TemporaryUnavailable:
                    print("No hay ningún servicio de Autenticación disponible")
                    input()
                except IceFlix.Unauthorized:
                    print("Usuario no autorizado como administrador")
                    input()
                else:
                    input("Usuario creado correctamente. Pulsa Enter para continuar...")
                continue

            if option == "2":
                delete_user = input("Introduce un usuario válido para eliminarlo: ")
                try:
                    auth = self._main_prx_.getAuthenticator()
                    auth.removeUser(delete_user, self._admin_token_)
                except IceFlix.TemporaryUnavailable:
                    print("No hay ningún servicio de Autenticación disponible")
                    input()
                except IceFlix.Unauthorized:
                    print("Usuario no autorizado como administrador")
                    input()
                else:
                    if delete_user == self._username_:
                        self._username_ = None
                        self._user_token_ = None
                    input("Usuario borrado correctamente. Pulsa Enter para continuar...")
                continue

            if option == "3":
                return 0

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
