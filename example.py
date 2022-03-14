import argparse
import datetime

parser = argparse.ArgumentParser(description="This is example procman script.")
parser.add_argument("--message", default="world!", type=str)
args = parser.parse_args()


def main():
    print(f"{datetime.datetime.now()}: hello {args.message}")


if __name__ == "__main__":
    main()
