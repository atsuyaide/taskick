import argparse
import logging
import logging.config
import os
import sys

import yaml

from taskick import TaskRunner, __version__

logger = logging.getLogger("taskick")


def main() -> None:
    """_summary_"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help='increase the verbosity of messages: "-v" for normal output, "-vv" for more verbose output and "-vvv" for debug',
    )
    parser.add_argument("--version", "-V", action="store_true", help="display this application version and exit")
    parser.add_argument("--file", "-f", type=str, default=None, help="choose task configuration file (YAML)")
    parser.add_argument(
        "--logging_config", "-l", type=str, default=None, help="choose logging configuration file (YAML or other)"
    )
    args = parser.parse_args()

    # Default logging level: WARNING(30), -vv -> INFO(20)
    args.verbose = 40 - 10 * args.verbose if args.verbose > 0 else 30
    logging.basicConfig(level=args.verbose)

    if args.logging_config is not None:
        file_extention = os.path.splitext(args.logging_config)[-1]
        if file_extention == ".yaml":
            with open(args.logging_config, "r") as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        else:  # .conf, .ini, ...
            logging.config.fileConfig(args.logging_config)

    if args.version:
        print(f"Taskick {__version__}")
        sys.exit(0)

    if args.file is None:
        parser.print_help()
        sys.exit(0)

    with open(args.file, "r", encoding="utf-8") as f:
        job_config = yaml.safe_load(f)

    logger.info("Loading tasks...")
    TR = TaskRunner(job_config)
    logger.info("Done.")
    TR.run()


if __name__ == "__main__":
    sys.exit(main())
