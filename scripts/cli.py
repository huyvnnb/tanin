import typer
from .manage import database


app = typer.Typer(
    name="tanin",
    help="A CLI for the Tanin application.",
    add_completion=False
)


@app.command(help="Get Tanin CLI information")
def info():
    typer.echo("Tanin Application CLI v0.1.0")


app.add_typer(database)


if __name__ == '__main__':
    app()
