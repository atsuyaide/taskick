import argparse
import logging
import sys

import yaml

from taskick import TaskRunner, __version__

logger = logging.getLogger("taskick")


def main() -> None:
    """_summary_"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", type=str, default="warning", help="")
    parser.add_argument("--version", "-V", action="store_true", help="")
    parser.add_argument("--file", "-f", type=str, default=None, help="")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.verbose.upper()))

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
