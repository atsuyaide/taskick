import argparse
import logging
import sys
from logging import getLogger

from procman import TaskRunner

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
parser.add_argument("--file", "-f", type=str, default="./jobconf.yaml")
args = parser.parse_args()

logger = getLogger("procman")
if args.debug:
    logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    """_summary_"""
    TR = TaskRunner(args.file)
    TR.run()


if __name__ == "__main__":
    sys.exit(main())
