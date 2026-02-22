from pympler import asizeof
from functools import wraps
from typing import Optional
from inspect import stack
from re import compile as recompile
from time import perf_counter_ns, process_time_ns
from sys import stdout, getsizeof
from typing import Optional
from gc import disable as gc_disable, enable as gc_enable

class Benchmark:
    __slots__ = ('__funcs', '__results', '__repeat', '__args')
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
        self.__repeat = repeat
        self.__args = args

    def add(self, func: callable, alias: Optional[str] = None) -> None:
        """Add a function to the benchmark comparison."""
        name = alias if alias else func.__name__
        self.__funcs.append((func, name))

    def __tests(self, func) -> None:
        avg = 0
        for i in range(self.__repeat):
            if self.__repeat - i == 1:
                gc_disable()
                start = process_time_ns()
                out = func(*self.__args)
                end = process_time_ns()
                gc_enable()
            else:
                gc_disable()
                start = perf_counter_ns()
                func(*self.__args)
                end = perf_counter_ns()
                gc_enable()
            avg += end - start
        return avg/self.__repeat, getsizeof(out)

    def run(self) -> None:
        """Execute the benchmark comparison and display optimized results."""
        if not self.__funcs:
            print("Aucune fonction à tester.")
            return

        ansi_escape = recompile(r'\033\[[0-9;]*m')
        def strip_ansi(text: str) -> str:
            return ansi_escape.sub('', text)
        
        results = [self.__tests(func) for func, _ in self.__funcs]
        names = [name for _, name in self.__funcs]
        times = [res[0] for res in results]
        sizes = [res[1] for res in results]
        ref_time, ref_size = times[0], sizes[0]

        def colorize(values: list, ref_val: float, is_time: bool = True) -> list:
            if not values:
                return []
                
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
                    if ref_val != 0:
                        diff = ((ref_val - val) / ref_val) * 100
                        sign = "+" if diff > 0 else ""
                        text = f"{base} ({sign}{diff:.2f}%)"
                    else:
                        text = base
                line.append(f"{color}{text}\033[0m")
            return line
        colored_times = colorize(times, ref_time, True)
        colored_sizes = colorize(sizes, ref_size, False)
        col_widths = []
        for col_idx in range(len(self.__funcs)):
            max_width = max(
                len(strip_ansi(names[col_idx])),
                len(strip_ansi(colored_times[col_idx])),
                len(strip_ansi(colored_sizes[col_idx]))
            )
            col_widths.append(max_width)

        total_width = 20 + 1 + sum(w + 1 for w in col_widths)
        separator = "-" * total_width

        def print_row(label: str, row_data: list) -> None:
            row_parts = [f"{label:<20}|"]
            for val, width in zip(row_data, col_widths):
                clean_val = strip_ansi(val)
                padding = width - len(clean_val)
                row_parts.append(f"{val}{' ' * padding}|")
            stdout.write(''.join(row_parts) + '\n')
        title_parts = [" Benchmark"]
        if self.__args:
            title_parts.append(f"| Paramètres : {', '.join(map(str, self.__args))}")
        if self.__repeat > 1:
            title_parts.append(f"| Répétitions : {self.__repeat}")
        
        title = ' '.join(title_parts)

        output_lines = [
            separator,
            f"{title:^{total_width}}",
            separator
        ]
        
        stdout.write(f"{'\n'.join(output_lines)}\n")
        print_row("Metric", names)
        print_row("Time (ns)", colored_times)
        print_row("Size (bytes)", colored_sizes)
        stdout.write(f"{separator}\n")


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
