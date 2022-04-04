import glob
import logging
import logging.config
import os
import sys
import time
from argparse import ArgumentParser
from typing import List

import yaml
from taskick import TaskRunner, __version__

logger = logging.getLogger("taskick")


class NoRegisteredTaskException(Exception):
    pass


class Taskicker:
    def __init__(self, parser: ArgumentParser) -> None:
        self._parser = parser
        self._setup_logger()
        self._TR = TaskRunner()

    def _setup_logger(self) -> None:
        args = self._parser.parse_args()

        # Default logging level: WARNING(30), -vv -> INFO(20)
        level = 40 - 10 * args.verbose if args.verbose > 0 else 30
        logging.basicConfig(level=level)

        if args.log_config is not None:
            file_extention = os.path.splitext(args.log_config)[-1]
            if file_extention == ".yaml":
                with open(args.log_config, "r") as f:
                    config = yaml.safe_load(f.read())
                    logging.config.dictConfig(config)
            else:  # *.(conf|ini|...)
                logging.config.fileConfig(args.log_config)

    def _show_version(self) -> None:
        print(f"Taskick {__version__}")

    def _show_help(self) -> None:
        self._show_version()
        self._parser.print_help()

    def _register(self, config_file: List[str]) -> None:
        extended_config_file_list = []
        for file in config_file:
            # Extract only files matching the pattern
            extended_config_file_list.extend(
                [x for x in glob.glob(file) if os.path.isfile(x)]
            )

        for file_name in extended_config_file_list:
            logger.info(f"Loading: {file_name}")
            with open(file_name, "r", encoding="utf-8") as f:
                job_config = yaml.safe_load(f)
            self._TR.register(job_config)

    def run(self) -> None:
        args = self._parser.parse_args()
        if args.version:
            self._show_version()
            return 0

        if args.file is None:
            self._show_help()
            return 0

        try:
            self._register(args.file)
            self._TR.run()

            if len(self._TR.scheduling_tasks) + len(self._TR.observing_tasks) == 0:
                logger.info("Scheduling/Observing task does not registered.")
                self._TR.join_startup_task()
                raise NoRegisteredTaskException

            while True:
                time.sleep(1)
        except NoRegisteredTaskException:
            pass
        except KeyboardInterrupt:
            logger.debug("Ctrl-C detected.")
        except Exception as e:
            import traceback

            logger.error(e)
            traceback.print_exc(e)
        finally:
            self._TR.stop()
            self._TR.join()


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
