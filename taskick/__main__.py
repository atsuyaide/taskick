import glob
import logging
import logging.config
import os
import sys
import time
from argparse import ArgumentParser

import yaml
from taskick import TaskRunner, __version__

logger = logging.getLogger("taskick")


def main() -> None:
    """_summary_"""

    parser = ArgumentParser()
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
        help="select task configuration files (YAML)",
    )
    parser.add_argument(
        "--log-config",
        "-l",
        type=str,
        dest="log_config",
        default=None,
        help="select a logging configuration file (YAML or other)",
    )
    args = parser.parse_args()

    # Default logging level: WARNING(30), -vv -> INFO(20)
    args.verbose = 40 - 10 * args.verbose if args.verbose > 0 else 30
    logging.basicConfig(level=args.verbose)

    if args.log_config is not None:
        file_extention = os.path.splitext(args.log_config)[-1]
        if file_extention == ".yaml":
            with open(args.log_config, "r") as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        else:  # *.(conf|ini|...)
            logging.config.fileConfig(args.log_config)

    if args.version:
        print(f"Taskick {__version__}")
        sys.exit(0)

    if args.file is None:
        print(f"Taskick {__version__}")
        parser.print_help()
        sys.exit(0)

    job_configuration_file_names = []
    for file in args.file:
        # Extracts only file paths
        job_configuration_file_names.extend(
            [x for x in glob.glob(file) if os.path.isfile(x)]
        )

    if len(job_configuration_file_names) == 0:
        print("Check configuration file name, path or pattern.")
        sys.exit(0)

    TR = TaskRunner()

    for file_name in job_configuration_file_names:
        logger.info(f"Loading: {file_name}")
        with open(file_name, "r", encoding="utf-8") as f:
            job_config = yaml.safe_load(f)
        TR.register(job_config)

    TR.run()

    if len(TR.scheduling_tasks) == 0 and len(TR.observing_tasks) == 0:
        logger.info("Scheduling/Observing task does not registered.")
        return 0

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("Ctrl-C detected.")
    except Exception as e:
        import traceback

        logger.error(e)
        traceback.print_exc(e)
    finally:
        TR.stop()
        TR.join()


if __name__ == "__main__":
    sys.exit(main())
