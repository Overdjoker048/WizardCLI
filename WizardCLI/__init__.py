"""
Python Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic librairy for create CLI in Python.

:copyright: Copyright (c) 2023-2026 Overdjoker048
:license: MIT, see LICENSE for more details.

Create basic Python CLI:
    >>> import WizardCLI
    >>> cli = WizardCLI.CLI()
    >>> @cli.command()
    >>> def hello_world():
    ...     print("Hello World")
    >>> cli.run()
"""
from .tools import exectime, gram, Benchmark
from .core import  CLI, File, optional
from colorama import init
from .styles import (
    fg, rst, bld, itl, und, rev, 
    strk, bg, gradiant, strimg
)
init()
del init
__encoding__ = 'UTF-8'
__author__ = 'Overdjoker048'
__version__ = '1.5.1'
__all__ = (
    "CLI", "File", "optional",
    "exectime", "gram", "Benchmark",
    "fg", "bg", "rst", "bld", "itl", "und", "rev", "strk",
    "gradiant", "strimg"
)