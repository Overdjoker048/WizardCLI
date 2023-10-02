import PyCLI
import os
import socket

cli = PyCLI.CLI(animation=False)

@cli.command(alias=["hw"])
def hello_world():
    PyCLI.echo("Hello World", animation=False)

@cli.command(name="cls")
def cls():
    "Reset l affichage de la console."
    os.system("cls")

@cli.command(alias=["co", "connection"])
def connect(ip: str, port: int=80):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    PyCLI.echo(f"[{ip}:{port}] Connection Réussite !!", animation=False)
    msg = PyCLI.prompt(f"Entrez le message que vous voulez envoyer à {ip}:{port}.", animation=False)
    s.send(msg.encode())
    s.close()
    PyCLI.echo(f"Le message a bien été envoyer à {ip}:{port}.", animation=False)

def cls():
    "Reset l affichage de la console."
    os.system("cls")

cli.cmd.append({
    "name": cls.__name__,
    "description": cls.__doc__,
    "function": cls,
    "args": [],
    "types": [],
    "alias": [],
})

cli.run()