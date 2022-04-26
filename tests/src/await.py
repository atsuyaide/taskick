import time


def main():
    print("Waiting 100 seconds...")
    time.sleep(100)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Detected: Ctrl-c")
