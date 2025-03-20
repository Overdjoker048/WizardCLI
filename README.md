# WizardCLI
![Python Version](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-1.3.2-yellow)

A simple and efficient command-line tool written in Python.

## Description

WizardCLI is a command-line utility that provides a powerful framework for creating interactive CLI applications. It features:

- Progressive text display with customizable animation speed
- Colored text output support (RGB and HEX)
- Command history and logging capabilities
- Built-in file management utilities
- Loading animations and progress bars
- Memory usage tracking
- Execution time measurement
- Gradient text effects

## Key Features

- **Easy Command Creation**: Create new commands with simple decorators
- **Type Safety**: Built-in type checking for command arguments
- **Documentation**: Automatic help generation for commands
- **Customization**: Configurable prompt, colors, and animations
- **File Operations**: Integrated file handling with encoding support
- **Visual Feedback**: Progress indicators and loading animations
- **Development Tools**: Memory tracking and execution time measurement
- **Text Effects**: Bold, italics, underline, reverse, and strikethrough text effects
- **Escape Sequences**: Handling and iterating over ANSI escape sequences

## Example Usage
```python
import WizardCLI

# Create a new CLI instance
cli = WizardCLI.CLI(
    prompt="[{}]@[{}]\\>", # Customizable prompt
    user="MyApp", # Username in prompt
    title="My CLI App", # Window title
    logs=True, # Enable logging
    anim=True, # Enable text animation
    cool=0.1, # Animation speed
    color=(255,0,0) # Text color (RGB)
)

# Create a simple command
@cli.command()
def hello(name: str = "World"):
    """Says hello to someone"""
    WizardCLI.echo(f"Hello {name}!")

# Run the CLI
cli.run()
```
