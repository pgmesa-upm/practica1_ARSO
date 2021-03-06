
from .aux_classes import Command, Flag


class Cli:
    """Interfaz que se encarga de controlar que la linea de comandos
    introducida en un programa es correcta, (mira que todos los flags y 
    comandos introducidos por terminal son correctos y compatibles).
    Hace falta una configuracion previa (definir que comandos y flags
    que va a tener el programa y sus caracteristicas)"""
    def __init__(self):
        self.commands = {}
        self.flags = {"-h": Flag(
            "-h", 
            description="shows information about the commands available"
        )}
        
    def add_command(self, command:Command):
        """Añade un nuevo comando 

        Args:
            command (Command): Comando a añadir
        """
        self.commands[command.name] = command 
    
    def add_flag(self, flag:Flag):
        """Añade un nuevo Flag

        Args:
            flag (Flag): Flag a añadir
        """
        self.flags[flag.name] = flag
        
    def process_cmdline(self, args:list) -> dict:
        """Procesa los argumentos que se pasan como parametro. Informa 
        de si estos son validos o no en base a los comandos y flags 
        que conformen la cli.

        Args:
            args (list): Linea de comandos a procesar

        Raises:
            CmdLineError: Si no se han proporcionado argumentos
            CmdLineError: Si el comando no es correcto

        Returns:
            dict: diccionario con el comando, las opciones del comando
                y los flags como claves y los parametros que se les 
                hayan pasado como valores (si esque se les ha pasado
                alguno)
        """
        args.pop(0) # Eliminamos el nombre del programa
        if "-h" in args: 
            self.printHelp()
            return None
        # Miramos a ver si alguno de los flags validos esta en la 
        # linea de comandos introducida
        inFlags = self._check_flags(args)
        # Revisamos si alguno de los comandos validos esta en la 
        # linea de comandos introducida
        for cmd in self.commands.values():
            if len(args) == 0:
                raise CmdLineError("No se han proporcionado argumentos")
            if args[0] == cmd.name:
                # Separamos por partes la linea de comandos
                ant = args[0]; parts = {ant: ""}; last_index = 1
                for i, arg in enumerate(args):
                    if arg in cmd.options:
                        parts[ant] = args[last_index:i]
                        last_index = i + 1
                        ant = arg
                parts[ant] = args[last_index:]
                # Vemos si cada parte es válida y la guardamos en 
                # un diccionario
                processed_line = {"cmd": {}, "options": {}, "flags": []}
                for cmd_name, params in parts.items():
                    try:
                        command = cmd.options[cmd_name]
                        key = "options"
                    except KeyError:
                        command = cmd
                        key = "cmd"
                    checked_cmd = self._check_command(command, params)
                    dict_page = {command.name: checked_cmd}
                    processed_line[key] = dict_page
                processed_line["flags"] = inFlags
                return processed_line
        raise CmdLineError(f"El comando '{args[0]}' no se reconoce")
      
    @staticmethod
    def _check_command(cmd:Command, params:list) -> list:
        """Revisa si los parametro que se han pasado a un comando 
        (puede ser una opcion de un comando) son validos o si no se 
        le han pasado parametros y el comando los requeria.
        

        Args:
            cmd (Command): Comando a procesar
            params (list): parametros que se le han pasado al comando

        Raises:
            CmdLineError: Si los parametros no son validos para el
                comando

        Returns:
            list: lista con los parametros del comando procesados. Si 
                se han proporcionado numeros en los parametros los 
                devuelve como int y no como str
        """
        if len(params) > 0:
            if len(params) > 1 and not cmd.multi: 
                err_msg = ("No se permite mas de 1 opcion extra " +
                          f"en el comando '{cmd.name}'. Comandos " +
                          f"incorrectos -> {params[1:]}")
                raise CmdLineError(err_msg)
            if cmd.extra_arg:
                extra_args = []
                for extra in params:
                    try:
                        extra_args.append(int(extra))
                    except:
                        extra_args.append(extra)
                if cmd.choices == None:
                    return extra_args
                # Todos los extra args deben estar en choices
                for extra in extra_args:
                    if extra not in cmd.choices:
                        break
                # Si completa el bucle es que todos son validos
                else:
                    return extra_args
                err_msg = f"El parametro extra '{params[0]}' no es valido"
                raise CmdLineError(err_msg)
            else:
                err_msg = (f"El comando '{cmd.name}' no admite " + 
                                            f"parametros extra {params}")
                raise CmdLineError(err_msg)
        elif not cmd.default == None:
            return [cmd.default]
        elif not cmd.mandatory:
            return []
        else:
            err_msg = f"El comando '{cmd.name}' requiere un parametro extra"
            raise CmdLineError(err_msg)
        
    def _check_flags(self, args:list) -> list:
        """Revisa que los flags que se han proporcionado son 
        compatibles entre si

        Args:
            args (list): Linea de comandos a procesar

        Raises:
            CmdLineError: Si los comandos no son compatibles

        Returns:
            list: lista con los flags que habia en la linea de 
                de comandos proporcionada (args)
        """
        inFlags = []
        for arg in args:
            for validFlag in self.flags.values():
                if arg == validFlag.name:
                    if len(inFlags) > 0:
                        # Comprobamos que son flags compatibles
                        for flag in inFlags:
                            if (flag.name in validFlag.ncwf or 
                                        validFlag.name in flag.ncwf):
                                errmsg = (f"Las opciones '{flag}' y " + 
                                         f"'{validFlag}' no son compatibles")
                                raise CmdLineError(errmsg)
                    inFlags.append(validFlag)
        # Eliminamos los flags ya procesadas de la linea de comandos  
        for flag in inFlags: args.remove(flag.name)
        # Guardamos los nombres de los flags en vez del objeto Flag
        # entero (ya no nos hace falta)
        inFlags = list(map(lambda flag: str(flag), inFlags))
        return inFlags
      
    def printHelp(self):
        """Imprime las descripciones de cada comando y flag de la cli
        de forma estructurada"""
        print(" python3 __main__ [commands] <parameters> " + 
                                    "[options] <parameters> [flags]")
        print(" + Commands: ")
        for arg in self.commands.values():
            print(f"    -> {arg.name} --> {arg.description}")
            if len(arg.options) > 0:
                print(f"        - options:")
                for opt in arg.options.values():
                    info = f"=> '{opt.name}' --> {opt.description}"
                    print("          ", info)
        print(" + Flags: ")   
        for flag in self.flags.values():
            if not flag.description == None:
                print(f"    -> {flag.name} --> {flag.description}")
            else:
                print(f"    -> {flag.name}")

# -------------------------------------------------------------------- 
class CmdLineError(Exception):
    """Excepcion personalizada para los errores de la cli"""
    def __init__(self, msg:str, _help=True):
        hlpm = "\nIntroduce el parametro -h para acceder a la ayuda"
        if _help: 
            msg += hlpm
        super().__init__(msg)
# --------------------------------------------------------------------
        
