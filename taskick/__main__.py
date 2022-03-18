import argparse
import logging
import sys

from taskick import TaskRunner


def main() -> None:
    """_summary_"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--info", action="store_true")
    parser.add_argument("--file", "-f", type=str, default="./jobconf.yaml")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.info:
        logging.basicConfig(level=logging.INFO)

    TR = TaskRunner(args.file)
    TR.run()


if __name__ == "__main__":
    sys.exit(main())
