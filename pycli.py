"""
Python Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic librairy for create CLI in Python.

:copyright: Copyright (c) 2023-2024 Overdjoker048
:license: MIT, see LICENSE for more details.

Create basic Python CLI:

    >>> import pycli
    >>> cli = pycli.CLI()
    >>> @cli.command()
    >>> def hello_world():
    >>>     print("Hello World")
    >>> cli.run()
"""

__encoding__ = "UTF-8"
__title__ = 'pycli'
__author__ = 'Overdjoker048'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2023-2024 Overdjoker048'
__version__ = '1.3.0'
__all__ = ['CLI', 'echo', 'prompt', 'write_logs', 'colored', 'gradiant', 'gram', 'exectime', 'file', 'optional']

import colorama
import inspect
import datetime
import os
import time
import sys
import shlex
import functools
import typing
from pympler import asizeof

colorama.init()

class CLI:
    home = os.path.dirname(__file__)
    def __init__(self,
                 prompt: str = "[{}]@[{}]\\>",
                 user: str = "Python-Cli",
                 title: str = None,
                 logs: bool = True,
                 anim: bool = True,
                 cool: float = 0.1,
                 color: typing.Union[tuple, str] = None
                 ) -> None:
        """This object allows the creation of the CLI.

        Args:
            prompt (str): Text displayed in terminal when entering commands. Defaults to "[{}]@[{}]\\>".
            user (str): Username displayed in prompt. Defaults to "Python-Cli".
            title (str, optional): Window title. Defaults to None.
            logs (bool): Enable/disable action logging. Defaults to True.
            anim (bool): Enable/disable progressive text display. Defaults to True.
            cool (float): Delay between characters for animation. Defaults to 0.1.
            color (Union[tuple, str], optional): Text color in RGB or hex. Defaults to None.

        Returns:
            None

        Example of use:
            >>> import pycli
            >>> cli = pycli.CLI()
            >>> @cli.command()
            >>> def hello_world():
            >>>     print("Hello World")
            >>> cli.run()
        """
        if title is not None:
            os.system("title {}".format(title) if os.name == 'nt' else "echo -n '\033]0;{}\007'".format(title))

        self.__cmd = {}
        self.prompt = prompt
        self.user = user
        self.path = CLI.home
        self.logs = logs
        self.anim = anim
        self.cool = cool
        self.color = color
        self.__clear_cmd = "cls" if os.name == 'nt' else "clear"
        self.command(alias=["?"], doc=self.help.__doc__)(self.help)
        self.command(alias=[self.__clear_cmd], name="clear-host", doc=self.clear_host.__doc__)(self.clear_host)
        self.command(alias=["exit"], doc=self.leave.__doc__)(self.leave)

        @self.command(alias=["cd"], doc=self.change_directory.__doc__)
        @optional(CLI.home)
        def change_directory(path) -> None:
            self.change_directory(path)

    def command(self,
                name: str = None,
                doc: str = None,
                alias : list = []
                ) -> typing.Callable:
        """The command decorator allows you to define a function as a command for the CLI.

        Args:
            name (str, optional): Name of the command. Defaults to function name.
            doc (str, optional): Documentation for the command. Defaults to function docstring.
            alias (list): List of alternative names for the command. Defaults to [].

        Returns:
            Callable: Decorated function that becomes a CLI command.

        Example of use:
            >>> import pycli
            >>> cli = pycli.CLI()
            >>> @cli.command()
            >>> def hello_world():
            >>>     print("Hello World")
            >>> cli.run()
        """
        def decorator(func: callable) -> typing.Callable:
            def wrapper(name: str, doc: str, alias: list) -> None:
                if doc is None:
                    doc = ""
                data = {"function": func}
                args_info = inspect.signature(func).parameters.items()
                args, options, params = [], [], {}
                for arg_name, arg_info in args_info:
                    if arg_info.default == inspect.Signature.empty:
                        args.append(("[{}]".format(arg_name), arg_info.annotation))
                    elif arg_info.default is True:
                        options.append("-{}".format(arg_name))
                    else:
                        params["--{}".format(arg_name)] = (arg_info.annotation, arg_info.default)
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
        os.kill(os.getpid(), 9)

    def clear_host(self) -> None:
        "Reset the display of the terminal."
        os.system(self.__clear_cmd)

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
            lines = ["Alias  {} -> {} {}".format(cmds[cmd]['la'][0]+(la-cmds[cmd]['la'][1])*' ', cmds[cmd]['lap'][0]+(lap-cmds[cmd]['lap'][1])*' ',cmds[cmd]['doc']) for cmd in sorted(cmds)]
        else:
            lines = ["{} - {}".format(cmd, cmds[cmd]['doc']) for cmd in sorted(cmds)]
        max_length = max(len(line.split(" - ")[0]) for line in lines) if not m else 0
        if not m:
            lines = ["{} {}".format(cmd.ljust(max_length), cmds[cmd]['doc']) for cmd in sorted(cmds)]
        text = "\n".join(lines)
        echo(text, anim=self.anim, cool=self.cool, color=self.color)

    def change_directory(self, path : str) -> None:
        "Allows you to change the location of the terminal in your files."
        npath = os.path.join(self.path, path)
        if os.path.isdir(npath):
            path = os.path.normpath(npath)
        else:
            path = os.path.normpath(path)
        if os.path.isdir(path):
            self.path = str(path).title()
        else:
            echo("The path is invalid.", anim=self.anim, cool=self.cool, color=self.color)

    def __decode(self, tpe: object, value: any) -> object:
        "Format arguments in the types chosen when creating commands."
        if tpe is inspect.Signature.empty:
            return value
        elif hasattr(tpe, '__args__'):
            for member in tpe.__args__:
                return member(value)
        return tpe(value)

    def __info(self, name: str, data: dict) -> str:
        "Creates the information message for the commands to add in the cli."
        usage = "\nUsage: {}".format(name)
        txt = ""
        for i in data:
            if i == "doc":
                txt += "\nDocumentation: {}".format(data[i])
            elif i == "args":
                txt += "\nArgument(s):"
                for j in data["args"]:
                    usage += " {}".format(j[0])
                    txt += "\n    {}: {}".format(j[0].replace("[", "").replace("]", ""), str(j[1]).replace("<class '", "").replace("'>", ""))
            elif i == "params":
                txt += "\nParameter(s):"
                for j in data["params"]:
                    usage += " {}".format(j)
                    tpe = str(data['params'][j][0]).replace("<class '", "").replace("'>", "")
                    if tpe == "None":
                        tpe = ""
                    else:
                        tpe = ": " + tpe
                    txt += "\n    {}{} = {}".format(j, tpe, data['params'][j][1])
            elif i == "options":
                txt += "\nOption(s):"
                for j in data["options"]:
                    usage += " {}".format(j)
                txt += " {}".format(j)
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
                    echo("Unknown Parameter", anim=self.anim, cool=self.cool, logs=self.logs, color=self.color)
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
                        echo(cmd["info"], anim=self.anim, cool=self.cool, logs=self.logs, color=self.color)
                        break
                    else:
                        echo("Unknown Option", anim=self.anim, cool=self.cool, logs=self.logs, color=self.color)
                        do = True
                        break
            else:
                if arg_i < len(cmd["args"]):
                    kwargs[cmd["args"][arg_i][0].strip("[]")] = self.__decode(cmd["args"][arg_i][1], arg)
                    arg_i += 1
                else:
                    echo("Too many arguments provided.", anim=self.anim, cool=self.cool, logs=self.logs, color=self.color)
                    do = True
                    break
            index += 1
        if not do:
            cmd["function"](**kwargs)

    def run(self) -> None:
        "This method of the CLI object allows you to launch the CLI after you have created all your commands."
        if self.logs:
            write_logs(self.__cmd)
        while True:
            try:
                entry = shlex.split(prompt(self.prompt.format(self.user, self.path), anim=self.anim, cool=self.cool, color=self.color, logs=self.logs))
                if not entry:
                    continue
                cmd = self.__cmd.get(entry[0].lower())
                if cmd is None:
                    echo("{} doesn't exist.\nDo help to get the list of existing commands.".format(entry[0]), anim=self.anim, cool=self.cool, logs=self.logs, color=self.color)
                    continue
                if isinstance(cmd, str):
                    cmd = self.__cmd[cmd]
                self.exec(cmd, entry)
            except KeyboardInterrupt:
                os.kill(os.getpid(), 9)
            except Exception as e:
                echo("An unexpected error occurred: {}".format(e), anim=self.anim, cool=self.cool, logs=self.logs, color=self.color)


def echo(*values: object,
         sep: str = " ",
         end: str = "\n",
         anim: bool = True,
         cool: float = 0.1,
         color: typing.Union[tuple, str] = None,
         logs: bool = False,
         flush: bool = False,
         file: None = None,
         ) -> None:
    """Print message with animation and logging capabilities.

    Args:
        values (object): Values to print.
        sep (str): Separator between values. Defaults to " ".
        end (str): String appended after the last value. Defaults to "\\n".
        anim (bool): Enable/disable progressive display. Defaults to True.
        cool (float): Delay between characters for animation. Defaults to 0.1.
        color (Union[tuple, str], optional): Text color in RGB or hex. Defaults to None.
        logs (bool): Enable/disable logging. Defaults to False.
        flush (bool): Force flush the output. Defaults to False.
        file (TextIO, optional): File-like object to write to. Defaults to None.

    Returns:
        None

    Example of use:
        >>> import pycli
        >>> pycli.echo("Hello World", anim=True, cool=15, logs=True)
    """
    output = sep.join(map(str, values))
    if len(output) != 0:
        times =  cool / len(output)
    if anim:
        for char in output:
            print(colored(char, color), end="", flush=True, file=file)
            time.sleep(times)
        print(end=end)
    else:
        print(colored(output, color), end=end, flush=flush, file=file)
    if logs:
        write_logs(output)


def prompt(__prompt: object = "",
           anim: bool = True,
           cool: float = 0.1,
           color: typing.Union[tuple, str] = None,
           logs: bool = False,
           flush: bool = False
           ) -> str:
    """
    The prompt method works like the input method which is already implemented in python but has a progressive display 
    system if the value of the anim parameter is set to True and also includes a logging system that writes the 
    text that the user will respond to in the daily logs. The logging system is enabled by default. The cool 
    parameter corresponds to the exposure time before displaying the next character (in MS) of the text you have entered
    if the anim parameter is set to True.

    Example of use::

        >>> import pycli
        >>> pycli.prompt("What's your name ?", anim=True, cool=15, logs=True, end="\n", sep=" ")
    """
    if len(__prompt) != 0:
        times =  cool / len(__prompt)
    if anim:
        for i in str(__prompt):
            print(colored(i, color), end="", flush=flush)
            time.sleep(times)
    else:
        print(colored(str(__prompt), color), end="", flush=flush)
    returned = input()
    if logs:
        write_logs(returned)
    return returned


def write_logs(*values: object,
               sep: str = " ",
               end: str = "\n",
               ) -> None:
    """
    The write_logs method allows to write in the daily logs. This method works like the print method which is already 
    implemented in python for the sep and end parameters.

    Example of use:

        >>> import pycli
        >>> pycli.write_logs("CLI was starting.")
    """
    text = sep.join(map(str, values)) + end
    if not os.path.exists("latest"):
        os.mkdir("latest")
    with open(os.path.join("latest", "{}.log".format(datetime.datetime.today().date())), "a", encoding="UTF-8") as file:
        file.write("{} {}".format(datetime.datetime.now().strftime('%H:%M:%S'), text))


def __to_rgb(color: typing.Union[tuple, str] = None) -> tuple:
    "Format le code couleur entré vers un code RGB."
    if isinstance(color, str):
        return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in color)


def colored(text: str,
            color: typing.Union[tuple, str, list] = None
            ) -> str:
    """Convert text to colored text using ANSI escape codes.

    Args:
        text (str): Text to be colored.
        color (Union[tuple, str, list], optional): Color in RGB tuple or hex string format. Defaults to None.

    Returns:
        str: ANSI colored text string.

    Examples of use:
        >>> import pycli
        >>> print(pycli.colored("Hello World", "FF0000"))
        >>> print(pycli.colored("Hello World", (255, 0, 0)))
    """
    if color:
        color = __to_rgb(color)
        return "\033[38;2;{};{};{}m{}\033[0m".format(int(color[0]), int(color[1]), int(color[2]), text)
    return text


def gradiant(
    text: str,
    start: typing.Union[tuple, str],
    end: typing.Union[tuple, str],
    sep: str = ""
    ) -> str:
    """Create text with color gradient effect.

    Args:
        text (str): Text to apply gradient to.
        start (Union[tuple, str]): Starting color in RGB tuple or hex format.
        end (Union[tuple, str]): Ending color in RGB tuple or hex format.
        sep (str, optional): Separator for splitting text into segments. Defaults to "".

    Returns:
        str: Text with color gradient applied.

    Example of use:
        >>> import pycli
        >>> print(pycli.gradiant("Hello World", (255,0,0), (0,0,255)))
    """
    txt = ""
    start = list(__to_rgb(start))
    end = __to_rgb(end)
    if sep == "":
        text = [caractere for caractere in str(text)]
    else:
        text = str(text).split(sep)
    steps = max(len(text) - 1, 1)
    diff = [(end[i] - start[i]) / steps for i in range(3)]
    for index, item in enumerate(text):
        current = [int(start[j] + diff[j] * index) for j in range(3)]
        if index > len(text)-2:
            txt += colored(text=item, color=current)
        else:
            txt += colored(text=item + sep, color=current)
    return txt


def gram(debug=False) -> None:
    """Display memory usage of the program.

    Args:
        debug (bool, optional): Show detailed memory usage per variable. Defaults to False.

    Returns:
        None

    Example of use:
        >>> import pycli
        >>> gram(debug=True)
    """
    memory = 0
    frame = inspect.stack()[1][0].f_globals
    for index in frame:
        imemory = sys.getsizeof(frame[index])
        imemory = asizeof.asizeof(frame[index])
        if debug:
            tpe = str(type(frame[index])).replace("<class '", "").replace("'>", "")
            print("[{}] {}: {} bytes".format(index, tpe, imemory))
        memory += imemory
    print("Total: {} bytes".format(memory))


def exectime(func: callable) -> typing.Callable:
    """Decorator to measure function execution time.

    Args:
        func (callable): Function to measure.

    Returns:
        Callable: Wrapped function that prints execution time.

    Example of use:
        >>> import pycli
        >>> @pycli.exectime
        >>> def hello_world():
        >>>     print("Hello World")
    """
    @functools.wraps(func)
    def wrapper(**kwargs) -> any:
        """
        Shows the execution time of the associated function.

        Example of use:

            >>> import pycli
            >>> @pycli.exectime
            >>> def hello_world():
            >>>     print("Hello World")
        """
        start = time.perf_counter()
        result = func(**kwargs)
        end = time.perf_counter()
        print("{:.2f} ms".format((end - start) * 1000))
        return result
    return wrapper


def optional(*defaults):
    """
    Set the value None to arguments that are not entered if the user has not defined a default value in the decorator.

    Examples of use:

        >>> import pycli
        >>> @pycli.optional("World")
        >>> def hello_world(name):
        >>>     print("Hello", name)
    """
    def decorator(func: callable) -> typing.Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> any:
            for i, (param_name, param) in enumerate(inspect.signature(func).parameters.items()):
                if param_name not in kwargs or kwargs[param_name] is inspect.Signature.empty:
                    if i < len(defaults):
                        kwargs[param_name] = defaults[i]
                    else:
                        kwargs[param_name] = None
            return func(*args, **kwargs)
        return wrapper
    return decorator


class file:
    def __init__(self, path: str, encoding: str = "UTF-8") -> None:
        """Allows you to manage files from their own type.

        Args:
            path (str): The path to the file.
            encoding (str, optional): The encoding of the file. Defaults to "UTF-8".

        Examples of use:

        >>> import pycli
        >>> file = pycli.file("test.txt", "UTF-8")
        """
        self.name, self.extention = os.path.splitext(path)
        self.__encoding = encoding
        if os.path.exists(self.name+self.extention) and os.path.isfile(path):
            self.__binary = open(path, "rb").read()
        else:
            open(path, "wb").close()
            self.__binary = b""
        self.__created = os.path.getctime(path) if os.path.exists(path) else None
        self.__last_modif = os.path.getmtime(path) if os.path.exists(path) else None
        self.__perm = oct(os.stat(path).st_mode & 0o777) if os.path.exists(path) else None
        self.__lines = self.split()

    @property
    def created(self) -> float:
        """Returns the creation time of the file."""
        return self.__created

    @property
    def lastmodif(self) -> float:
        """Returns the last modification time of the file."""
        return self.__last_modif

    @property
    def perm(self) -> float:
        """Returns the permissions of the file."""
        return self.__perm

    def __str__(self) -> str:
        """Returns the content of the file."""
        return str(self.__binary.decode(encoding=self.__encoding))

    def __bytes__(self) -> bytes:
        """Returns the binary data of the file."""
        return self.__binary

    def __repr__(self) -> str:
        """Returns a string representation of the file."""
        return "file(path='{}', encoding='{}')".format(self.name+self.extention, self.__encoding)

    def split(self, sep: str="\n", maxsplit: int = -1):
        """Splits the file into lines."""
        return self.__str__().split(sep, maxsplit)

    def __bool__(self) -> bool:
        """Returns True if the file is not empty."""
        return bool(self.__binary)

    def __len__(self) -> int:
        """Returns the length of the file."""
        return len(self.__binary)

    def __eq__(self, other: object) -> bool:
        """Compares two files."""
        if isinstance(other, file):
            return self.path == other.path and self.__data == other.__data
        return False

    def __iter__(self) -> typing.Callable:
        """Returns an iterator for the file."""
        self.index = 0
        return self

    def __next__(self) -> typing.Union[str, StopIteration]:
        """Returns the next line in the file."""
        if self.index < len(self.__lines):
            line = self.__lines[self.index]
            self.index += 1
            return line
        else:
            raise StopIteration

    def append(self, data: typing.Union[str, bytes]) -> None:
        """Appends data to the file."""
        if isinstance(data, str):
            data = data.encode(self.__encoding)
        elif not isinstance(data, bytes):
            raise ValueError("data must be bytes or str")
        self.__binary += data

    def save(self) -> None:
        """Saves the file."""
        open(self.name + self.extention, "wb").write(self.__binary)

    def __add__(self, value: object) -> None:
        """Adds data to the file."""
        self.append(str(value))
        return self

class strloading:
    def __init__(self) -> str:
        """Creates a rotating loading animation with characters | / - \

        Returns:
            str: One of the characters in the sequence | / - \

        Example:
            >>> import pycli
            >>> from time import sleep
            >>> for _ in range(4):
            ...     print(pycli.strloading(), end='\r')
            ...     sleep(0.25)
            # Output will show: | → / → - → \ → |
        """
        self.__cached = 0
        self.__running = True

    def next(self) -> str:
        self.__cached = (self.__cached + 1) % 4
        return ["|", "/", "-", "\\"][self.__cached]

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.__running:
            return self.next()
        raise StopIteration

    def stop(self, condition: bool = False) -> None:
        self.__running = condition

class strwait:
    def __init__(self) -> str:
        """Creates a "dots" waiting animation (. .. ...)

        Returns:
            str: String containing 1-3 dots, right-padded with spaces to maintain width

        Example:
            >>> import pycli
            >>> from time import sleep
            >>> for _ in range(3):
            ...     print(f"Loading{pycli.strwait()}", end='\r')
            ...     sleep(0.5)
            # Output will show: Loading. → Loading.. → Loading...
        """
        self.__points = 1
        self.__running = True

    def next(self) -> str:
        if self.__points > 2:
            self.__points = 1
        else:
            self.__points = (self.__points % 3) + 1
        return "." * self.__points + " " * (3 - self.__points)

    def __iter__(self):
        return self

    def __next__(self) -> str:
        if self.__running:
            return self.next()
        raise StopIteration

    def stop(self, condition: bool = False) -> None:
        self.__running = condition

def strpercent(value: float, total: float, size: int = 10, char: str = "█") -> str:
    """Creates a progress bar visualization

    Args:
        value (float): Current progress value
        total (float): Maximum progress value
        size (int, optional): Width of the progress bar in characters. Defaults to 10.
        char (str, optional): Character to use for filled portion. Defaults to "█".

    Returns:
        str: A progress bar string like "██████    " representing the progress

    Example:
        >>> import pycli
        >>> print(pycli.strpercent(7, 10, size=10))
        # Output: "███████   "
        >>> print(pycli.strpercent(5, 10, size=5, char="#"))
        # Output: "##   "
    """
    assert total >= value > 0 and size > 0
    percent = int((value / total) * size)
    return "{}{}".format(percent*char, (size-percent)*" ")
