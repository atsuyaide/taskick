import os
import sys
import yaml
import logging
import argparse
from logging import getLogger
from procman import TaskRunner

parser = argparse.ArgumentParser()
parser.add_argument("--init", action="store_true")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--file", "-f", type=str, default="./jobconf.yaml")
args = parser.parse_args()

logger = getLogger("procman")
if args.debug:
    logging.basicConfig(level=logging.DEBUG)

EXAMPLE_JOBCONF = {
    "example_process_1": {
        "status": 1,
        "script_path": "./example.py",
        "execution": {
            "immediate": True,
            "event_type": "time",
            "when": "*/1 * * * *",
        },
        "options": {
            "message": "procman. Run by time event trigger"
        }
    },
    "example_process_2": {
        "status": 1,
        "script_path": "./example.py",
        "execution": {
            "immediate": True,
            "event_type": "time",
            "when": "*/2 * * * *",
        },
        "options": {
            "message": "procman. Run by time event trigger"
        }
    },
    # "example_process_2": {
    #     "status": 1,
    #     "script_path": "./example.py",
    #     "execution": {
    #         "immediate": True,
    #         "event_type": "file",
    #         "detail": {
    #             "when": "create",
    #             "path": "./sandbox/",
    #         }
    #     },
    #     "options": {
    #         "message": "procman. Run by file event trigger"
    #     }
    # }
}

EXAMPLE_SCRIPT = """
import datetime
import argparse
parser = argparse.ArgumentParser(
    description="This is example procman script.")
parser.add_argument("--message", default="world", type=str)
args = parser.parse_args()

print(f"{datetime.datetime.now()}: hello {args.message}!")
"""


def init() -> None:
    def yes_or_no() -> bool:
        while True:
            ans = input("y/n>> ").upper()
            if ans in ["Y", "YES"]:
                return True
            elif ans in ["N", "NO"]:
                return False
            else:
                print("Retype 'Yes' or 'No'")

    INIT_FILES = {
        os.path.join(os.getcwd(), "jobconf.yaml"): EXAMPLE_JOBCONF,
        os.path.join(os.getcwd(), "example.py"): EXAMPLE_SCRIPT
    }

    for file_path, script in INIT_FILES.items():
        if os.path.isfile(file_path):
            print(f"'{file_path}' is already exist. Overwrite?")
            if yes_or_no():
                pass
            else:
                continue

        with open(file_path, "w") as f:
            if ".yaml" in file_path:
                yaml.dump(script, f, encoding="utf-8", allow_unicode=True)
            else:
                f.write(script)
            print(f"=> Saved: {file_path}")

    return 0


def main() -> None:
    if args.init:
        return init()

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
