import sys
from .app import cli


def main() -> None:
    cli.main(args=sys.argv[1:])


if __name__ == "__main__":
    main()
