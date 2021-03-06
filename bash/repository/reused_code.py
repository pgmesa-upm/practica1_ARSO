
import logging
from logging import Logger

import program.controllers.containers as containers
import dependencies.register.register as register
from dependencies.utils.tools import objectlist_as_dict, remove_many


def target_containers(logger:Logger=None):
    """Decorador que permite reutilizar el codigo de algunos comandos.
    Comprueba que haya contenedores creados y despues devuelve los 
    contenedores diana sobre los que se va a aplicar el comando.
    Nota: 
    Si no se pasa ningun contenedor en el comando (argumentos que 
    recibe get_targets) se asume que se quiere aplicar el comando a
    todos los contenedores existentes.

    Args:
        logger (Logger, optional): logger del fichero que va a 
            utilizar el decorador

    Returns:
        function: devuelve la funcion que ha llamado al decorador
            con el decorador ya aplicado
    """
    if logging == None:
        logger = logging.getLogger(__name__)
    def _target_containers(cmd):
        def get_targets(*args, **opt_args):
            cs = register.load(containers.ID)
            if cs == None:
                msg = " No existen contenedores creados por el programa"
                logger.error(msg)
                return
            # Comprobamos si hay que operar sobre todos los existentes 
            # o solo algunos en concreto
            names_given = list(args)
            c_dict = objectlist_as_dict(cs, "name")
            target_cs = cs
            if len(args) != 0: 
                valid_names = filter(lambda name: name in c_dict, names_given)
                target_cs = list(map(lambda valid: c_dict[valid], valid_names))
            # Notificamos los incorrectos. Eliminamos los nombres validos 
            # de los que nos han pasado y si siguen quedando nombres 
            # significa que no son validos. 
            remove_many(names_given, *c_dict.keys())
            for wrong in names_given:
                err_msg = f" No existe el contenedor '{wrong}' en este programa"
                logger.error(err_msg)
            # En caso de que haya algun contenedor valido
            if len(target_cs) != 0:
                cmd(*target_cs, **opt_args)
        return get_targets
    return _target_containers

# --------------------------------------------------------------------