import argparse
import datetime

parser = argparse.ArgumentParser(description="This is example procman script.")
parser.add_argument("--message", default="world!", type=str)
# Watchdog events
parser.add_argument("--event_type", default=None, type=str)
parser.add_argument("--src_path", default="", type=str)
parser.add_argument("--dest_path", default="", type=str)
parser.add_argument("--is_directory", default=False, action="store_true")
args = parser.parse_args()


def main():
    now = datetime.datetime.now()
    if args.event_type is None:
        print(f"{now}: hello {args.message}")
    else:
        print(
            "{:}: event_type: {:s} src: {:s} dest: {:s} is_dir: {:}".format(
                now, args.event_type, args.src_path, args.dest_path, args.is_directory
            )
        )


if __name__ == "__main__":
    main()
