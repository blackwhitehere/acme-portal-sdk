import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog="aps",
        description="SDK to customize behaviour of acme-portal VSCode extension",
    )
    return parser.parse_args()


def main_logic(args):
    print("Hello World!")


def main():
    args = parse_args()
    main_logic(args)


if __name__ == "__main__":
    main()
