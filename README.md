# WizardCLI
![Python Version](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-1.5.0-yellow)

A simple and efficient command-line tool written in Python.

## Description

WizardCLI is a command-line utility that provides a powerful framework for creating interactive CLI applications. It features:

- Colored text output support (RGB and HEX)
- Built-in file management utilities
- Memory usage tracking
- Comparisons of method effectiveness
- Execution time measurement
- Gradient text effects
- Image conversion to ASCII

## Key Features

- **Easy Command Creation**: Create new commands with simple decorators
- **Type Safety**: Built-in type checking for command arguments
- **Documentation**: Automatic help generation for commands
- **File Operations**: Integrated file handling with encoding support
- **Development Tools**: Memory tracking, execution time measurement and methode comparaison
- **Text Effects**: Bold, italics, underline, reverse, background color, forground color, and strikethrough text effects

## Quick Exemple Usage
```python
import WizardCLI

# Create a new CLI instance
cli = WizardCLI.CLI(
    prompt="[{}]@[{}]\\>", # Customizable prompt
    user="MyApp", # Username in prompt
    formating="\033[38;2;255;0;0m{}\033[0m" #Customizable text
)

# Create a simple command
@cli.command()
def hello(name: str = "World"):
    """Says hello to someone"""
    WizardCLI.echo(f"Hello {name}!")

# Run the CLI
cli.run()
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.