import logging
import os

import click
import cseo_python_framework

from stuco_app.__init__ import __version__

CMD_FOLDER = os.path.join(os.path.dirname(__file__), "commands")
CMD_PREFIX = "cmd_"

LOGGER = logging.getLogger(__name__)


class CLI(click.MultiCommand):
    """Main Command Class."""

    def list_commands(self, ctx):
        """Obtain a list of all available commands.

        Args:
            ctx (dictionary): Click context object

        Returns:
            list: a list of sorted commands
        """

        commands = []

        for filename in os.listdir(CMD_FOLDER):
            if filename.endswith(".py") and filename.startswith(CMD_PREFIX):
                commands.append(filename[4:-3])

        return commands

    def get_command(self, ctx, name):  # pylint: disable=arguments-differ
        """Get a specific command by looking up the module.

        Args:
            ctx (dictionary): Click context object
            name (string): Command name

        Returns:
            function: Module's cli function
        """

        namespace = {}

        filename = os.path.join(CMD_FOLDER, CMD_PREFIX + name + ".py")

        try:
            with open(filename) as opened_file:
                code = compile(opened_file.read(), filename, "exec")  # noqa: WPS421
                eval(  # nosec  # noqa  # pylint: disable=eval-used
                    code,
                    namespace,
                    namespace,
                )

            return namespace["cli"]
        except OSError as ignore:  # pylint: disable=W0612  # noqa
            return None


@click.command(cls=CLI, name="stuco_app")
@click.version_option(__version__)
@click.option(
    "--config_file",
    help='location of configuration file"',
)
@click.option("-d", "--debug", is_flag=True, help="turn debug logging on")
@click.option("--nocolor", is_flag=True, help="turn OFF colorized logging")
@click.option("--dark_theme", is_flag=True, help="use color scheme for Dark console")
def cli(config_file=None, debug=False, nocolor=False, dark_theme=False):
    """Training Manager Command Line Tool.

    Args:
        config_file (string): Path to configuration file
        debug (bool): Set this to True to turn on Debug
        nocolor (bool): Set this to True to turn off Colorized Logging
        dark_theme (bool): Set this to True to use Dark Theme Colors

    """

    ctx = click.get_current_context()
    ctx.obj = {}

    # Set up Colorized Logging
    use_color = not nocolor
    use_light_theme = not dark_theme

    config_file_warning_message = None
    # If no config file actually present, then look for a file named
    # 'local.config'. If that doesn't exist, assume all is coming from environment.
    # Validation of appropriate config will be handled by sub-command.
    config_files = []
    if not config_file:
        config_file = "local.config"

    if os.path.exists(config_file):
        config_files = [config_file]
    else:
        config_file_warning_message = (
            f"A config file '{config_file}' was specified, but cannot be located - "
            "skipping config file use . . ."
        )

    log_level = logging.DEBUG if debug else logging.INFO
    my_config = cseo_python_framework.initialize_framework(
        "stuco_app",
        log_level=log_level,
        light_theme_logging=not dark_theme,
        colorized_logging=not nocolor,
        config_files=config_files,
        display_initialization_messages=debug,
    )

    if config_file_warning_message:
        LOGGER.warning(config_file_warning_message)

    ctx.obj["config"] = my_config
    ctx.obj["config_file_path"] = config_file


if __name__ == "__main__":
    cli()  # pylint: disable=E1120

# End of SPG controlled content - anything after this line will be maintained
