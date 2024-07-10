import click


@click.command(name="say_hello_to", help="Say hello")
@click.argument("name")
def say_hello(name):
    """Say Hello to NAME.

    Args:
        name (string): Name of the person to say hello to.
    """
    click.secho(f"Hello {name}!!")


@click.command(name="say_goodbye_to", help="Say goodbye")
@click.argument("name")
def say_goodbye(name):
    """Say Goodbye to NAME.

    Args:
        name (string): Name of the person to say goodbye to.
    """
    click.secho(f"Goodbye {name}!!")

@click.group(name="hello")
def cli():
    """Hello Commands."""


cli.add_command(say_hello)
cli.add_command(say_goodbye)
