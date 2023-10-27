import argparse


def main():
    parser = argparse.ArgumentParser(
        description="The command line tool for PyJoern. Do things like initializing Joern and running queries."
    )
    parser.add_argument(
        "--install", action="store_true", help="Install Joern backend and dependencies."
    )
    args = parser.parse_args()

    if args.install:
        import pyjoern



if __name__ == "__main__":
    main()
