"""
Python Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic librairy for create CLI in Python.

:copyright: Copyright (c) 2023-2025 Overdjoker048
:license: MIT, see LICENSE for more details.

Create basic Python CLI:
    >>> import WizardCLI
    >>> cli = WizardCLI.CLI()
    >>> @cli.command()
    >>> def hello_world():
    ...     print("Hello World")
    >>> cli.run()
"""

__encoding__ = "UTF-8"
__title__ = 'WizardCLI'
__author__ = 'Overdjoker048'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2023-2025 Overdjoker048'
__version__ = '1.4.1'
__all__ = [
    'CLI', 'gradiant', 'gram', 'Benchmark',
    'File', 'optional', 'exectime', 'fg', 
    'bg', 'rst', 'itl', 'und', 'rev', 'strk',
    'bld', 'strimg'
]

from os import path as ospath, name, kill, getpid, stat, rename
from typing import Union, Optional
from time import perf_counter_ns
from colorama import init
from inspect import Signature, signature, stack
from shlex import split as splitS
from functools import wraps, lru_cache
from pympler import asizeof
from threading import Thread
from re import compile as recompile, split, sub
from shutil import move, get_terminal_size
from PIL import Image

init()

class CLI:
    home = ospath.dirname(__file__)
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

        self.__cmd: dict = {}
        self.prompt: str = prompt
        self.user: str = user
        self.path: str = CLI.home
        self.format: str = formating.format
        self.command(alias=["?"], doc=self.help.__doc__)(self.help)
        self.command(alias=["cls" if name == 'nt' else "clear"], name="clear-host", doc=self.clear_host.__doc__)(self.clear_host)
        self.command(alias=["exit"], doc=self.leave.__doc__)(self.leave)
        @self.command(alias=["cd"], doc=self.change_directory.__doc__)
        @optional(CLI.home)
        def change_directory(path) -> None:
            self.change_directory(path)

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
        print(self.format("\n".join(lines)))

    def change_directory(self, path: str) -> None:
        "Allows you to change the location of the terminal in your files."
        npath = ospath.join(self.path, path)
        if ospath.isdir(npath):
            path = ospath.normpath(npath)
        else:
            path = ospath.normpath(path)
        if ospath.isdir(path):
            self.path = str(path).title()
        else:
            print(self.format("The path is invalid."))

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
                    print(self.format("Unknown Parameter"))
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
                        print(self.format(cmd["info"]))
                        break
                    else:
                        print(self.format("Unknown Option"))
                        do = True
                        break
            else:
                if arg_i < len(cmd["args"]):
                    kwargs[cmd["args"][arg_i][0].strip("[]")] = self.__decode(cmd["args"][arg_i][1], arg)
                    arg_i += 1
                else:
                    print(self.format("Too many arguments provided."))
                    do = True
                    break
            index += 1
        if not do:
            cmd["function"](**kwargs)

    def run(self) -> None:
        "This method of the CLI object allows you to launch the CLI after you have created all your commands."
        while True:
            try:
                entry = splitS(input(self.prompt.format(self.user, self.path)))
                if not entry:
                    continue
                cmd = self.__cmd.get(entry[0].lower())
                if cmd is None:
                    print(self.format(f"{entry[0]} doesn't exist.\nDo help to get the list of existing commands."))
                    continue
                if isinstance(cmd, str):
                    cmd = self.__cmd[cmd]
                self.exec(cmd, entry)
            except KeyboardInterrupt:
                kill(getpid(), 9)
            except Exception as e:
                print(self.format(f"An unexpected error occurred: {e}"))


def gradiant(
    text: str,
    start: Union[tuple, str, list, int],
    end: Union[tuple, str, list, int],
    sep: Optional[str] = ""
) -> str:
    """Create text with color gradient effect while preserving existing styles.

    Arguments:
        text (str): Text to apply gradient to.
        start (Union[tuple, str, list]): Starting color in RGB tuple or hex format.
        end (Union[tuple, str, list]): Ending color in RGB tuple or hex format.
        sep (str, optional): Separator for splitting text into segments.

    Return:
        str: Text with color gradient applied, preserving styles.
    """
    def parse_color(c):
        if isinstance(c, (list, tuple)) and len(c) == 3:
            return c
        elif isinstance(c, int):
            return ((c >> 16) & 255, (c >> 8) & 255, c & 255)
        elif isinstance(c, str):
            return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
        ValueError(f"Invalid color: {c}")

    ANSI_PATTERN = recompile(r"\x1b\[[0-9;]*m")
    start_rgb = parse_color(start)
    end_rgb = parse_color(end)

    def apply_gradient(segment: str, start_offset: float = 0.0, global_len: Optional[int] = None, global_pos: int = 0) -> str:
        parts = split(r"(\x1b\[[0-9;]*m)", segment)
        clean_len = sum(len(p) for i, p in enumerate(parts) if i % 2 == 0)
        denom = max(1, (global_len if global_len is not None else clean_len) - 1)

        out = []
        visible_idx = 0
        for i, p in enumerate(parts):
            if i % 2 == 1:
                out.append(p)
            else:
                for ch in p:
                    idx = global_pos + visible_idx
                    if idx == denom:
                        out.append(f"\033[38;2;{end_rgb[0]};{end_rgb[1]};{end_rgb[2]}m{ch}")
                    else:
                        f = (idx / denom) + start_offset
                        out.append(f"\033[38;2;{int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * f)};{int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * f)};{int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * f)}m{ch}")
                    visible_idx += 1
        return "".join(out)

    if sep:
        segments = text.split(sep)
        total_len = sum(len(sub(ANSI_PATTERN, "", seg)) for seg in segments)
        pos = 0
        colored_segments = []
        for seg in segments:
            colored_segments.append(apply_gradient(seg, 0.0, global_len=total_len, global_pos=pos))
            pos += len(sub(ANSI_PATTERN, "", seg))
        return sep.join(colored_segments) + "\033[0m"
    else:
        return apply_gradient(text) + "\033[0m"


def gram() -> tuple:
    """
    Display memory usage of the program.

    Return:
        tuple: A tuple containing:
            - dict: A dictionary with variable names as keys and a tuple of (type, size in bytes) as values.
            - int: The total memory usage in bytes.

    Example of use:
        >>> import WizardCLI
        >>> total_memory, memory = WizardCLI.gram()
        >>> print(memory)
        >>> print("Total memory usage:", total_memory, "bytes")
    """
    memory = {}
    gmemory = 0
    frame = stack()[1][0].f_globals
    for index in frame:
        imemory = asizeof.asizeof(frame[index])
        memory[index] = (type(frame[index]), imemory)
        gmemory += imemory
    return gmemory, memory


def exectime(repeat: Optional[int] = 1):
    """Decorator to measure function execution time in nanoseconds.

        Argument:
            repeat (int): Number of times to repeat the function. Defaults to 1.

        Return:
            Callable: Wrapped function that prints execution time.

        Example of use:
            >>> import WizardCLI
            >>> @WizardCLI.exectime(repeat=5)
            >>> def hello_world():
            ...    print("Hello World")
        """
    def decorator(func: callable) -> callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> tuple:
            avg = 0
            for _ in range(repeat):
                start = perf_counter_ns()
                result = func(*args, **kwargs)
                avg += perf_counter_ns() - start
            avg /= repeat
            return avg, result
        return wrapper
    return decorator


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
    def __init__(self, path: str, encoding: str = "UTF-8") -> None:
        """Allows you to manage files from their own type.

        Arguments:
            path (str): The path to the file.
            encoding (str, optional): The encoding of the file. Defaults to "UTF-8".

        Example of use:
            >>> import WizardCLI
            >>> file = WizardCLI.file("test.txt", "UTF-8")
        """
        self.name, self.extention = ospath.splitext(ospath.basename(path))
        self.path = ospath.dirname(path)
        self.__encoding = encoding
        if ospath.exists(self.name+self.extention) and ospath.isfile(path):
            self.__binary = open(path, "rb").read()
        else:
            open(path, "wb").close()
            self.__binary = b""
        self.__created = ospath.getctime(path) if ospath.exists(path) else None
        self.__last_modif = ospath.getmtime(path) if ospath.exists(path) else None
        self.__perm = oct(stat(path).st_mode & 0o777) if ospath.exists(path) else None
        self.__lines = self.split()
        self.__running = False
        self.__tasks = {
            "rename": None,
            "move": None,
            "write": []
        }

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
        "Returns a string representation of the file."
        return f"file(path='{self.name}{self.extention}', encoding='{self.__encoding}')"

    def split(self, sep: str="\n", maxsplit: int = -1):
        "Splits the file into lines."
        return self.__str__().split(sep, maxsplit)

    def __bool__(self) -> bool:
        "Returns True if the file is not empty."
        return bool(self.__binary)

    def __len__(self) -> int:
        "Returns the length of the file."
        return len(self.__binary)

    def __eq__(self, other: object) -> bool:
        "Compares two files."
        if isinstance(other, File):
            return self.path == other.path and self.__data == other.__data
        return False

    def __iter__(self) -> callable:
        "Returns an iterator for the file."
        self.index = 0
        return self

    def __next__(self) -> Union[str, StopIteration]:
        "Returns the next line in the file."
        if self.index < len(self.__lines):
            line = self.__lines[self.index]
            self.index += 1
            return line
        else:
            raise StopIteration

    def __sub__(self, index: int) -> None:
        "Removes data from the file by subtracting bytes from the end."
        if index < self.__len__():
            self.__binary = self.__binary[:-index]
            self.__newt(self.__write, self.__binary, "wb")
        return self

    def __add__(self, value: any) -> None:
        "Adds data to the file by appending it."
        self.append(value)
        return self

    def append(self, data: Union[str, bytes]) -> None:
        "Appends data to the file."
        if isinstance(data, str):
            data = data.encode(self.__encoding)
        elif not isinstance(data, bytes):
            data = str(data).encode(self.__encoding)
        self.__binary += data
        self.__newt(self.__write, data, "ab")

    def clear(self) -> None:
        "Clears the content of the file."
        self.__newt(self.__write, "", "wb")

    def rename(self, name: str) -> None:
        "Renames the file to the specified name."
        self.__newt(rename, self.path+self.name+self.extention, self.path+name+self.extention)
        self.name = name

    def move(self, path: str) -> None:
        "Moves the file to the specified path."
        self.__newt(move, path+self.name+self.extention)
        self.path = path

    def find(self, value: str) -> int:
        "Finds the index of the first occurrence of a value in the file."
        return self.__str__().find(value)

    def drop(self, value: str) -> None:
        "Removes the first occurrence of a value from the file."
        content = self.__str__().replace(value, "", 1)
        self.__binary = content.encode(self.__encoding)
        self.__newt(self.__write, self.__binary, "wb")

    def insert(self, index: int, data: Union[str, bytes]) -> None:
        "Inserts data into the file at the specified index."
        if isinstance(data, str):
            data = data.encode(self.__encoding)
        elif not isinstance(data, bytes):
            data = str(data).encode(self.__encoding)
        if index < 0 or index > len(self.__binary):
            raise IndexError("Index out of range")
        self.__binary = self.__binary[:index] + data + self.__binary[index:]
        self.__newt(self.__write, self.__binary, "wb")

    def __write(self, path: str, data: bytes, method: str = "wb") -> None:
        "Writes binary data to the file at the specified path."
        open(path, method).write(data)

    def __newt(self, func: callable, *args) -> None:
        "Schedules a task to be executed in a separate thread."
        if func == rename:
            self.__tasks["rename"] = (func, args)
        elif func == move:
            self.__tasks["move"] = (func, args)
        elif func == self.__write:
            if args[0] == "wb":
                self.__tasks["write"] = [(func, args)]
            else:
                self.__tasks["write"].append((func, args))
        if not self.__running:
            self.__thread = Thread(target=self.__run).start()

    def __run(self) -> None:
        """Executes all scheduled tasks in a separate thread."""
        self.__running = True
        while self.__tasks["write"] or self.__tasks["rename"] or self.__tasks["move"]:
            for key in ["rename", "move", "write"]:
                if self.__tasks[key]:
                    func, args = self.__tasks[key].pop(0)
                    if key == "rename":
                        func(*args)
                    else:
                        func(self.path+self.name+self.extention, *args)
        self.__running = False


def fg(color: Optional[Union[tuple, str, list, int]] = None) -> str:
    """
    Returns the ANSI escape code for forground text color.

    Arguments:
        color (Union[tuple, str, list, int], optional): Color in RGB tuple, hex string, or integer format. Defaults to None.

    Return:
        str: ANSI fg text string.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.fg("FF0000") + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.fg((255, 0, 0)) + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.fg(0xFF0000) + "Red background" + WizardCLI.rst())
    """
    if color is None:
        return ""
    if isinstance(color, int):
        return f"\033[38;2;{(color >> 16) & 255};{(color >> 8) & 255};{color & 255}m"
    elif isinstance(color, str):
        return f"\033[38;2;{int(color[0:2], 16)};{int(color[2:4], 16)};{int(color[4:6], 16)}m"
    elif isinstance(color, (list, tuple)) and len(color) == 3:
        return f"\033[38;2;{color[0]};{color[1]};{color[2]}m"
    raise TypeError("Invalid color format. Expected tuple, list, string, or int string.")


def bg(color: Optional[Union[tuple, str, list, int]] = None) -> str:
    """
    Returns the ANSI escape code for background text color.

    Parameters:
        color (Union[tuple, str, list, int], optional): RGB color value as tuple, hex string, or integer. Defaults to None.

    Return:
        str: ANSI escape code for background color formatting

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.bg("FF0000") + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.bg((255, 0, 0)) + "Red background" + WizardCLI.rst())
        >>> print(WizardCLI.bg(0xFF0000) + "Red background" + WizardCLI.rst())
    """
    if color is None:
        return ""
    if isinstance(color, int):
        return f"\033[48;2;{(color>>16)&255};{(color>>8)&255};{color&255}m"
    elif isinstance(color, str):
        return f"\033[48;2;{int(color[0:2],16)};{int(color[2:4],16)};{int(color[4:6],16)}m"
    elif isinstance(color, (list, tuple)) and len(color) == 3:
        return f"\033[48;2;{color[0]};{color[1]};{color[2]}m"
    raise TypeError("Invalid color format. Expected tuple, list, string, or int string.")


def rst() -> str:
    """Returns the ANSI escape code to reset text formatting to default.

    This function is used to reset any applied text formatting, such as colors, bold, italic, underline, etc., back to the terminal's default state.

    Return:
        str: ANSI escape code to reset text formatting.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.rst() + "Default text")
    """
    return "\033[0m"


def bld() -> str:
    """Returns the ANSI escape code for bold text formatting.

    This function is used to apply bold styling to text in the terminal.

    Return:
        str: ANSI escape code for bold text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.bld() + "Bold text" + WizardCLI.rst())
    """
    return "\033[1m"


def itl() -> str:
    """Returns the ANSI escape code for italic text formatting.

    This function is used to apply italic styling to text in the terminal. Note that not all terminals support italic text.

    Return:
        str: ANSI escape code for italic text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.itl() + "Italic text" + WizardCLI.rst())
    """
    return "\033[3m"


def und() -> str:
    """Returns the ANSI escape code for underlined text formatting.

    This function is used to underline text in the terminal.

    Return:
        str: ANSI escape code for underlined text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.und() + "Underlined text" + WizardCLI.rst())
    """
    return "\033[4m"


def rev() -> str:
    """Returns the ANSI escape code for reversed text color formatting.

    This function is used to swap the foreground and background colors of text in the terminal.

    Return:
        str: ANSI escape code for reversed text color.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.rev() + "Reversed text" + WizardCLI.rst())
    """
    return "\033[7m"


def strk() -> str:
    """Returns the ANSI escape code for strikethrough text formatting.

    This function is used to apply a strikethrough effect to text in the terminal. Note that not all terminals support strikethrough text.

    Return:
        str: ANSI escape code for strikethrough text.

    Example of use:
        >>> import WizardCLI
        >>> print(WizardCLI.strk() + "Strikethrough text" + WizardCLI.rst())
    """
    return "\033[9m"


class Benchmark:
    def __init__(self, *args, repeat: Optional[int] = 1) -> None:
        """
        This object allows benchmarking of multiple functions.
        It measures execution time (in nanoseconds) and memory usage (in bytes) for each 
        registered function, using the same arguments and comparing them to a reference 
        (the first added function).

        Arguments:
            *args: Positional arguments passed to all tested functions.
            repeat (int, optional): Number of times each function is run to get an average. 
                Defaults to 1.

        Example of use:
            >>> bench = benchmark(1000)
            >>> bench.add(lambda x: [i for i in range(x)], alias="list")
            >>> bench.add(lambda x: list(range(x)), alias="range")
            >>> bench.run()
        """
        self.__funcs = []
        self.__results = []
        self.__threads = []
        self.__repeat = repeat
        self.__args = args

    def add(self, func: callable, alias: Optional[str] = None) -> None:
        name = alias if alias else func.__name__
        self.__funcs.append((func, name))

    def __tests(self, index) -> None:
        avg = 0
        func, _ = self.__funcs[index]
        for _ in range(self.__repeat):
            start = perf_counter_ns()
            out = func(*self.__args)
            avg += perf_counter_ns() - start
        avg /= self.__repeat
        self.__results[index] = (avg, asizeof.asizeof(out))

    def run(self) -> None:
        if not self.__funcs:
            print("Aucune fonction à tester.")
            return

        ansi_escape = recompile(r'\033\[[0-9;]*m')
        def strip_ansi(text: str) -> str:
            return ansi_escape.sub('', text)

        names = [name for _, name in self.__funcs]
        results = [list() for _ in range(3)]

        self.__results = [None] * len(self.__funcs)
        self.__threads = []

        for i in range(len(self.__funcs)):
            t = Thread(target=self.__tests, args=(i,))
            t.start()
            self.__threads.append(t)

        for t in self.__threads:
            t.join()

        times = [res[0] for res in self.__results]
        sizes = [res[1] for res in self.__results]
        ref_time, ref_size = times[0], sizes[0]

        def colorize(values, ref_val, is_time=True):
            best_val = min(values)
            worst_val = max(values)
            line = []
            for i, val in enumerate(values):
                if val == best_val:
                    color = "\033[92m"
                elif val == worst_val:
                    color = "\033[91m"
                else:
                    color = "\033[93m"

                if i == 0:
                    text = f"{val:.0f}" if is_time else f"{val}"
                else:
                    base = f"{val:.0f}" if is_time else f"{val}"
                    diff = ((ref_val - val) / ref_val) * 100 if ref_val else 0
                    sign = "+" if diff > 0 else ""
                    text = f"{base} ({sign}{diff:.2f}%)"
                line.append(f"{color}{text}\033[0m")
            return line

        results[0] = names
        results[1] = colorize(times, ref_time, is_time=True)
        results[2] = colorize(sizes, ref_size, is_time=False)

        col_widths = [max(len(strip_ansi(results[row][col])) for row in range(3)) for col in range(len(self.__funcs))]
        total_width = 20 + 1 + sum(w + 1 for w in col_widths)

        def print_row(label, row_data) -> None:
            row = f"{label:<{20}}|"
            for val, width in zip(row_data, col_widths):
                padding = width - len(strip_ansi(val))
                row += val + " " * padding + "|"
            print(row)

        title = f" Benchmark | Paramètres : {', '.join(map(str, self.__args))} "

        print("-" * total_width)
        print(f"{title:^{total_width}}")
        print("-" * total_width)
        print_row("Metric", results[0])
        print_row("Time (ns)", results[1])
        print_row("Size (bytes)", results[2])
        print("-" * total_width)


@lru_cache(maxsize=256)
def __RGBA(path: str, width: int, height: int) -> str:
    """Converts an image to colored ASCII with alpha channel management."""
    result = []
    last_color = None
    append = result.append
    for r, g, b, a in Image.open(path).resize((width, height), Image.Resampling.BILINEAR).getdata():
        if a < 51:
            append(" ")
        elif a < 102:
            if last_color == (r, g, b):
                append("░")
            else:
                append(f"\033[38;2;{r};{g};{b}m░")
                last_color = (r, g, b)
        elif a < 153:
            if last_color == (r, g, b):
                append("▒")
            else:
                append(f"\033[38;2;{r};{g};{b}m▒")
                last_color = (r, g, b)
        elif a < 204:
            if last_color == (r, g, b):
                append("▓")
            else:
                append(f"\033[38;2;{r};{g};{b}m▓")
                last_color = (r, g, b)
        else:
            if last_color == (r, g, b):
                append("█")
            else:
                append(f"\033[38;2;{r};{g};{b}m█")
                last_color = (r, g, b)
    lines = ["".join(result[i:i+width]).rstrip(" ") for i in range(0, len(result), width)]
    return "".join(("\n".join(lines), "\033[0m"))

@lru_cache(maxsize=128)
def __RGB(path: str, width: int, height: int, mode: bool = True) -> str:
    """Converts an image to colored ASCII without alpha channel management."""
    result = []
    last_color = None
    append = result.append
    if mode:
            pixels = Image.open(path).resize((width, height), Image.Resampling.BILINEAR).getdata()
    else:
        pixels = Image.open(path).convert("RGB").resize((width, height), Image.Resampling.BILINEAR).getdata()
    for r, g, b in pixels:
        if last_color == (r, g, b):
            append(" ")
        else:
            append(f"\033[48;2;{r};{g};{b}m ")
            last_color = (r, g, b)
    lines = ["".join(result[i:i+width]) for i in range(0, len(result), width)]
    return "".join(("\n".join(lines), "\033[0m"))

@lru_cache(maxsize=32)
def __P(path: str, width: int,  height: int) -> str:
    """Converts an image to colored ASCII with transparency handling."""
    result = []
    last_color = None
    append = result.append
    for r, g, b, a in Image.open(path).convert("RGBA").resize((width, height), Image.Resampling.BILINEAR).getdata():
        if not a:
            append(" ")
        if last_color == (r, g, b):
            append("█")
        else:
            append(f"\033[48;2;{r};{g};{b}m█")
            last_color = (r, g, b)
    lines = ["".join(result[i:i+width]).rstrip(" ") for i in range(0, len(result), width)]
    return "".join(("\n".join(lines), "\033[0m"))

def strimg(path: str, width: Optional[int] = None, height: Optional[int] = None, termadj: Optional[bool] = False) -> str:
    """
        Converts an image into a colored text representation faithful to the original image.

        Parameters:
            path (str): Path to the image file.
            width (Optional[int]): Desired output width. If None, calculated automatically.
            height (Optional[int]): Desired output height. If None, calculated automatically.
            termadj (Optional[bool]): If True, constrains output size to terminal dimensions.

        Returns:
            str: Colored text representation of the image.

        Example of use:
            result = strimg("image.png", width=80, termadj=True)
    """
    try:
        img = Image.open(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file '{path}' not found.")
    term_width, term_height = get_terminal_size(fallback=(80, 24))
    img_ratio = (img.width / img.height) * 1.8

    if width is None and height is None:
        if img_ratio < 1:
            width = term_width
            height = width / img_ratio
        elif img_ratio > 1:
            height = term_height
            width = height * img_ratio
        else:
            width = term_width
            height = term_height * 1.8
    elif width is None:
        width = height * img_ratio
    elif height is None:
        height = width / img_ratio
    else:
        if width / height > img_ratio:
            height = width / img_ratio
        else:
            width = height * img_ratio

    if termadj:
        if width > term_width:
            if img_ratio < 1:
                width = term_width
                height = width / img_ratio
            else:
                height = term_height
                width = height * img_ratio
        if height > term_height:
            if img_ratio < 1:
                height = term_height
                width = height * img_ratio
            else:
                width = term_width
                height = width / img_ratio
    width = round(width)
    height = round(height)
    if img.mode == "RGBA":
        return __RGBA(path, width, height)
    elif img.mode == "P":
        return __P(path, width, height)
    elif img.mode == "RGB":
        return __RGB(path, width, height, True)
    else:
        return __RGB(path, width, height, False)
