import sys
import logging
import argparse
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
    """_summary_
    """
    TR = TaskRunner(args.file)

    try:
        TR.run()
    except KeyboardInterrupt:
        logger.debug("Ctrl-C detected.")
    except Exception as e:
        logger.error(e)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    sys.exit(main())
