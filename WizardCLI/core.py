from os import path as ospath, name, kill, getpid, stat, rename
from typing import Union, Optional
from time import sleep
from inspect import Signature, signature
from shlex import split as splitS
from functools import wraps
from threading import Thread, Lock
from shutil import move, copy2

class CLI:
    __slots__ = ('__cmd', '__prompt', 'user', '__path', '__strformat', '__allow_cmd')
    def __init__(self,
                 prompt: str = "[{}]@[{}]\\>",
                 user: str = "Python-Cli",
                 formating: str = "{}"
                 ) -> None:
        """This object allows the creation of the CLI.

        Arguments:
            prompt (str): Text displayed in terminal when entering commands. Defaults to "[{}]@[{}]\\>".
            user (str): Username displayed in prompt. Defaults to "Python-Cli".
            formating (str): Text format for the prompt. Defaults to "".

        Example of use:
            >>> import WizardCLI
            >>> cli = WizardCLI.CLI()
            >>> @cli.command()
            >>> def hello_world():
            ...    print("Hello World")
            >>> cli.run()
        """

        self.__cmd = {}
        self.__prompt = prompt
        self.user = user
        self.__path = ospath.dirname(__file__)
        self.__strformat = formating.format
        self.__allow_cmd = {
            "help": True,
            "leave": True,
            "clear_host": True,
            "change_directory": True
        }
        if self.__allow_cmd["help"]:
            self.command(alias=["?"], doc=self.help.__doc__)(self.help)
        if self.__allow_cmd["clear-host"]:
            self.command(alias=["cls" if name == 'nt' else "clear"], name="clear-host", doc=self.clear_host.__doc__)(self.clear_host)
        if self.__allow_cmd["leave"]:
            self.command(alias=["exit"], doc=self.leave.__doc__)(self.leave)
        if self.__allow_cmd["change_directory"]:
            @self.command(alias=["cd"], doc=self.change_directory.__doc__)
            @optional(self.__path)
            def change_directory(path) -> None:
                self.change_directory(path)

    def allow(self, cmd: str, active: bool = True) -> None:
        """Enable or disable built-in CLI commands.

        Available commands that can be controlled:
            - "help": Show available commands and their usage
            - "leave": Exit the CLI
            - "clear_host": Clear the terminal screen
            - "change_directory": Change current working directory
        Default commandes are enable.

        Arguments:
            cmd (str): Name of the command to enable/disable.
            active (bool, optional): True to enable the command, False to disable it. Defaults to True.

        Example:
            >>> cli = WizardCLI.CLI()
            >>> cli.allow("help", False)  # Disable help command
            >>> cli.allow("leave", False) # Disable ability to exit
            >>> cli.allow("clear_host", False) # Disable screen clearing
            >>> cli.allow("change_directory", False) # Disable cd command

            # Re-enable a command
            >>> cli.allow("help", True)
        """
        if cmd in self.__allow_cmd:
            self.__allow_cmd[cmd] = active

    def command(self,
                name: Optional[str] = None,
                doc: Optional[str] = None,
                alias : list = []
                ) -> callable:
        """The command decorator allows you to define a function as a command for the CLI.

        Arguments:
            name (str, optional): Name of the command. Defaults to function name.
            doc (str, optional): Documentation for the command. Defaults to function docstring.
            alias (list): List of alternative names for the command. Defaults to [].

        Return:
            Callable: Decorated function that becomes a CLI command.

        Example of use:
            >>> import WizardCLI
            >>> cli = WizardCLI.CLI()
            >>> @cli.command()
            >>> def hello_world():
            ...    print("Hello World")
            >>> cli.run()
        """
        def decorator(func: callable) -> callable:
            def wrapper(name: str, doc: str, alias: list) -> None:
                if doc is None:
                    doc = ""
                data = {"function": func}
                args_info = signature(func).parameters.items()
                args, options, params = [], [], {}
                for arg_name, arg_info in args_info:
                    if arg_info.default == Signature.empty:
                        args.append((f"[{arg_name}]", arg_info.annotation))
                    elif arg_info.default is True:
                        options.append(f"-{arg_name}")
                    else:
                        params[f"--{arg_name}"] = (arg_info.annotation, arg_info.default)
                if doc != "":
                    data["doc"] = doc
                if args != []:
                    data["args"] = args
                if options != []:
                    data["options"] = options
                if params != {}:
                    data["params"] = params
                if alias != []:
                    data["alias"] = [i.lower() for i in alias]
                name = name.replace(" ", "_").lower()
                data["info"] = self.__info(name, data)
                self.__cmd[name] = data
                self.__cmd.update({i.lower(): name for i in alias})
            return wrapper(name=name if name else func.__name__, doc=doc if doc else func.__doc__, alias=alias)
        return decorator

    def leave(self) -> None:
        "Close the terminal."
        kill(getpid(), 9)

    def clear_host(self) -> None:
        "Reset the display of the terminal."
        print("\033[H\033[J", end="")

    def __format(self, name: str, cmd: dict) -> dict:
        "Format data of command."
        data = {}
        for i in [("alias", []), ("doc", ""), ("args", []), ["params", {}], ["options", []]]:
            data[i[0]] = cmd.get(i[0], i[1])
        local = ", ".join(data["alias"])
        data["la"] = local, len(local)
        local = name
        for i in [' '.join(arg[0] for arg in data["args"]), ' '.join(data["params"].keys()), ' '.join(data["options"])]:
            if len(i) != 0:
                local += " " + i
        data["lap"] = local, len(local)
        return data

    def help(self, m: bool = True) -> None:
        "Displays info about terminal commands."
        cmds = {}
        lap = la = 0
        for name, cmd in self.__cmd.items():
            if isinstance(cmd, dict):
                cmds[name] = self.__format(name, cmd)
                la = max(la, cmds[name]["la"][1])
                lap = max(lap, cmds[name]["lap"][1])
        if m:
            lines = [f"Alias  {cmds[cmd]['la'][0]+(la-cmds[cmd]['la'][1])*' '} -> {cmds[cmd]['lap'][0]+(lap-cmds[cmd]['lap'][1])*' '} {cmds[cmd]['doc']}" for cmd in sorted(cmds)]
        else:
            lines = [f"{cmd} - {cmds[cmd]['doc']}" for cmd in sorted(cmds)]
        max_length = max(len(line.split(" - ")[0]) for line in lines) if not m else 0
        if not m:
            lines = [f"{cmd.ljust(max_length)} {cmds[cmd]['doc']}" for cmd in sorted(cmds)]
        print(self.__strformat("\n".join(lines)))

    def change_directory(self, path: str) -> None:
        "Allows you to change the location of the terminal in your files."
        npath = ospath.join(self.__path, path)
        if ospath.isdir(npath):
            path = ospath.normpath(npath)
        else:
            path = ospath.normpath(path)
        if ospath.isdir(path):
            self.__path = str(path).title()
        else:
            print(self.__strformat("The path is invalid."))

    def __decode(self, tpe: object, value: any) -> object:
        "Format arguments in the types chosen when creating commands."
        if tpe is Signature.empty:
            return value
        elif hasattr(tpe, '__args__'):
            for member in tpe.__args__:
                return member(value)
        return tpe(value)

    def __info(self, name: str, data: dict) -> str:
        "Creates the information message for the commands to add in the cli."
        usage = f"\nUsage: {name}"
        txt = ""
        for i in data:
            if i == "doc":
                txt += f"\nDocumentation: {data[i]}"
            elif i == "args":
                txt += "\nArgument(s):"
                for j in data["args"]:
                    usage += f" {j[0]}"
                    tp = str(j[1]).replace("<class '", "").replace("'>", "")
                    txt += f"\n    {j[0].replace('[', '').replace(']', '')}: {tp}"
            elif i == "params":
                txt += "\nParameter(s):"
                for j in data["params"]:
                    usage += f" {j}"
                    tpe = str(data['params'][j][0]).replace("<class '", "").replace("'>", "")
                    if tpe == "None":
                        tpe = ""
                    else:
                        tpe = ": " + tpe
                    txt += f"\n    {j}{tpe} = {data['params'][j][1]}"
            elif i == "options":
                txt += "\nOption(s):"
                for j in data["options"]:
                    usage += f" {j}"
                txt += f" {j}"
            elif i == "alias":
                txt += "\nAlias: "
                txt += ", ".join(data["alias"])
        return txt[1:] + usage

    def exec(self, cmd: dict, entry: str) -> None:
        "Runs commands entered by the user."
        kwargs = {}
        if cmd.get("options"):
            for opt in cmd.get("options"):
                kwargs[opt[1:]] = False
        index = 1
        arg_i = 0
        do = False
        while index < len(entry):
            arg = entry[index]
            if arg.startswith("--"):
                value = cmd["params"].get(arg)
                if value is None:
                    print(self.__strformat("Unknown Parameter"))
                    do = True
                    break
                kwargs[arg[2:]] = None if index + 1 >= len(entry) else self.__decode(value[0], entry[index + 1])
                index += 1 if kwargs[arg[2:]] is not None else 0
            elif arg.startswith("-"):
                if arg[1:] in kwargs:
                    kwargs[arg[1:]] = True
                else:
                    if arg == "-?":
                        do = True
                        print(self.__strformat(cmd["info"]))
                        break
                    else:
                        print(self.__strformat("Unknown Option"))
                        do = True
                        break
            else:
                if arg_i < len(cmd["args"]):
                    kwargs[cmd["args"][arg_i][0].strip("[]")] = self.__decode(cmd["args"][arg_i][1], arg)
                    arg_i += 1
                else:
                    print(self.__strformat("Too many arguments provided."))
                    do = True
                    break
            index += 1
        if not do:
            cmd["function"](**kwargs)

    def run(self) -> None:
        "This method of the CLI object allows you to launch the CLI after you have created all your commands."
        while True:
            try:
                entry = splitS(input(self.__prompt.format(self.user, self.__path)))
                if not entry:
                    continue
                cmd = self.__cmd.get(entry[0].lower())
                if cmd is None:
                    print(self.__strformat(f"{entry[0]} doesn't exist.\nDo help to get the list of existing commands."))
                    continue
                if isinstance(cmd, str):
                    cmd = self.__cmd[cmd]
                self.exec(cmd, entry)
            except KeyboardInterrupt:
                kill(getpid(), 9)
            except Exception as e:
                print(self.__strformat(f"An unexpected error occurred: {e}"))


def optional(*defaults):
    """
    Set the value None to arguments that are not entered if the user has not defined a default value in the decorator.

    Example of use:
        >>> import WizardCLI
        >>> @WizardCLI.optional("World")
        >>> def hello_world(name):
        ...     print("Hello", name)
    """
    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> any:
            for i, (param_name, _) in enumerate(signature(func).parameters.items()):
                if param_name not in kwargs or kwargs[param_name] is Signature.empty:
                    if i < len(defaults):
                        kwargs[param_name] = defaults[i]
                    else:
                        kwargs[param_name] = None
            return func(*args, **kwargs)
        return wrapper
    return decorator


class File:
    __slots__ = (
        '__name', '__ext', '__path', '__encoding', '__binary',
        '__created', '__last_modif', '__perm', '__lines',
        '__tasks', '__index', '__thread', '__lock',
        '__processing', '__shutdown', '__current_path'
    )

    def __init__(self, path: str, encoding: str = "UTF-8") -> None:
        """Allows you to manage files from their own type.

        Arguments:
            path (str): The path to the file.
            encoding (str, optional): The encoding of the file. Defaults to "UTF-8".

        Example of use:
            >>> import WizardCLI
            >>> file = WizardCLI.File("test.txt", "UTF-8")
        """
        self.__lock = Lock()
        self.__thread = None
        self.__processing = False
        self.__shutdown = False
        self.__index = 0
        self.__lines = None
        self.__tasks = {
            "rename": None,
            "move": None,
            "wb": None,
            "ab": None,
        }
        self.__current_path = path
        self.__name, self.__ext = ospath.splitext(ospath.basename(path))
        self.__path = ospath.dirname(path)
        self.__encoding = encoding

        if ospath.exists(path) and ospath.isfile(path):
            self.__binary = open(path, "rb").read()
            self.__created = ospath.getctime(path)
            self.__last_modif = ospath.getmtime(path)
            self.__perm = oct(stat(path).st_mode & 0o777)
        else:
            self.__newt("wb", b"")
            self.__binary = b""
            self.__created = None
            self.__last_modif = None
            self.__perm = None

    @property
    def created(self) -> float:
        """Returns the creation time of the file."""
        return self.__created

    @property
    def lastmodif(self) -> float:
        """Returns the last modification time of the file."""
        return self.__last_modif

    @property
    def perm(self) -> str:
        """Returns the permissions of the file."""
        return self.__perm

    @property
    def name(self) -> str:
        """Returns name of the file."""
        return self.__name

    @property
    def ext(self) -> str:
        """Returns extention of the file."""
        return self.__ext

    def __str__(self) -> str:
        """Returns the content of the file."""
        return self.__binary.decode(encoding=self.__encoding)

    def __repr__(self) -> str:
        """Returns a string representation of the file."""
        return f"file(path='{self.__name}{self.__ext}', encoding='{self.__encoding}')"

    def split(self, sep: str = "\n", maxsplit: int = -1):
        "Splits the file into lines."
        return self.__str__().split(sep, maxsplit)

    def __bool__(self) -> bool:
        """Returns True if the file is not empty."""
        return bool(self.__binary)

    def __len__(self) -> int:
        """Returns the length of the file."""
        return len(self.__binary)

    def __eq__(self, other: object) -> bool:
        """Compares two files."""
        if isinstance(other, File):
            return self.__path == other.__path and self.__str__() == other.__str__()
        return False

    def __iter__(self) -> callable:
        """Returns an iterator for the file."""
        self.__index = 0
        self.__lines = self.split()
        return self

    def __next__(self) -> Union[str, StopIteration]:
        """Returns the next line in the file."""
        if self.__index < len(self.__lines):
            line = self.__lines[self.__index]
            self.__index += 1
            return line
        else:
            raise StopIteration

    def __sub__(self, index: int) -> None:
        """Removes data from the file by subtracting bytes from the end."""
        if index < self.__len__():
            self.__binary = self.__binary[:-index]
            self.__newt("wb", self.__binary)
        return self

    def __add__(self, value: Union[str, bytes]) -> None:
        """Adds data to the file by appending it."""
        if isinstance(value, str):
            value = value.encode(self.__encoding)
        self.__binary += value
        self.__newt("ab", value)
        return self

    def clear(self) -> None:
        """Clears the content of the file."""
        self.__binary = b""
        self.__newt("wb", b"")

    def rename(self, name: str) -> None:
        """Renames the file to the specified name."""
        if name != self.__name:
            new_path = ospath.join(self.__path, f"{name}{self.__ext}")
            self.__newt("rename", new_path, ospath.join(self.__path, f"{self.__name}{self.__ext}"))
            self.__name = name
            self.__current_path = new_path

    def move(self, new_path: str) -> None:
        """Moves the file to the specified path."""
        if new_path != self.__path:
            target_path = ospath.join(new_path, f"{self.__name}{self.__ext}")
            self.__newt("move", target_path, ospath.join(self.__path, f"{self.__name}{self.__ext}"))
            self.__path = new_path
            self.__current_path = target_path

    def find(self, value: str) -> int:
        """Finds the index of the first occurrence of a value in the file."""
        return self.__str__().find(value)

    def drop(self, value: str) -> None:
        """Removes the first occurrence of a value from the file."""
        content = self.__str__()
        new_content = content.replace(value, "", 1)
        if content != new_content:
            self.__binary = new_content.encode(self.__encoding)
            self.__newt("wb", self.__binary)

    def insert(self, index: int, data: Union[str, bytes]) -> None:
        """Inserts data into the file at the specified index."""
        if isinstance(data, str):
            data = data.encode(self.__encoding)
        if index < 0 or index > len(self.__binary):
            raise IndexError("Index out of range")
        self.__binary = self.__binary[:index] + data + self.__binary[index:]
        self.__newt("wb", self.__binary)

    def __newt(self, methode: callable, args, current_path: str = None) -> None:
        """Schedules a task to be executed in a separate thread."""
        with self.__lock:
            match methode:
                case "rename":
                    if self.__tasks["move"]:
                        self.__tasks["move"] = (args, current_path)
                    else:
                        self.__tasks["rename"] = (args, current_path)
                case "move":
                    self.__tasks["move"] = (args, current_path)
                    self.__tasks["rename"] = None
                case "wb":
                    self.__tasks["wb"] = args
                    self.__tasks["ab"] = None
                case _:
                    if self.__tasks["wb"]:
                        self.__tasks["wb"] = self.__binary
                    elif self.__tasks["ab"]:
                        self.__tasks["ab"] += args
                    else:
                        self.__tasks["ab"] = args

            if not self.__thread or not self.__thread.is_alive():
                self.__thread = Thread(target=self.__run, daemon=True)
                self.__processing = True
                self.__thread.start()

    def __run(self) -> None:
        """Executes all scheduled tasks in a separate thread."""
        while self.__processing and not self.__shutdown:
            sleep(0.05)
            with self.__lock:
                if not any(self.__tasks.values()):
                    continue

                tasks_to_execute = self.__tasks.copy()
                self.__tasks = {
                    "rename": None,
                    "move": None,
                    "wb": None,
                    "ab": None,
                }
            if tasks_to_execute["rename"]:
                new_path, current_path = tasks_to_execute["rename"]
                rename(current_path, new_path)
                self.__current_path = new_path
            elif tasks_to_execute["move"]:
                new_path, current_path = tasks_to_execute["move"]
                move(current_path, new_path)
                self.__current_path = new_path

            current_path = self.__current_path
            if tasks_to_execute["wb"]:
                data, path = tasks_to_execute["wb"]
                with open(path, "wb") as f:
                    f.write(data)
            elif tasks_to_execute["ab"]:
                data, path = tasks_to_execute["ab"]
                with open(path, "ab") as f:
                    f.write(data)

    def __del__(self) -> None:
        """Destructor that ensures proper thread cleanup before object deletion."""
        self.close()

    def close(self) -> None:
        """Ferme proprement le fichier."""
        self.__shutdown = True
        self.__processing = False
        if self.__thread and self.__thread.is_alive():
            self.__thread.join()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatic cleanup in with statement."""
        self.close()

    def copy(self, new_path: str, overwrite: bool = False) -> Union['File', None]:
        """Creates a copy of the file with advanced options."""
        new_dir = ospath.dirname(new_path)
        if not new_path.endswith(self.ext):
            new_path += self.ext
        if not ospath.exists(new_dir):
            raise FileExistsError(f"Destination directory doesn't exist")
        if ospath.exists(new_path) and not overwrite:
            raise FileExistsError(f"Destination file already exists")

        copy2(ospath.join(self.__path, f"{self.__name}{self.__ext}"), new_path)
        return File(new_path, self.__encoding)
