import sys
from argparse import ArgumentParser

from .runner import Taskicker


def main() -> None:
    parser = ArgumentParser(prog="python -m taskick")
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        dest="verbose",
        default=0,
        help=(
            "increase the verbosity of messages: '-v' for normal output, '-vv' for more"
            " verbose output and '-vvv' for debug"
        ),
    )
    parser.add_argument(
        "--version",
        "-V",
        action="store_true",
        dest="version",
        help="display this application version and exit",
    )
    parser.add_argument(
        "--batch-load",
        "-b",
        type=str,
        dest="batch_load",
        default=None,
        help="configuration files can be load in batches",
    )
    parser.add_argument(
        "--file",
        "-f",
        nargs="+",
        type=str,
        dest="file",
        default=None,
        help="specify configuration files (YAML) for the task to be executed",
    )
    parser.add_argument(
        "--log-config",
        "-l",
        type=str,
        dest="log_config",
        default=None,
        help="specify a logging configuration file",
    )

    taskicker = Taskicker(parser)
    taskicker.run()


if __name__ == "__main__":
    sys.exit(main())
