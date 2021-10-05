import argparse

from utils import get_logger


def main(args):

    _LOGGER = get_logger('main', debug=args.debug)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=f'main.py is the entrypoint for the Docker container, it calls the appropriate script, and it handles passing arguments to the appropriate functions'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Set logger to debug level'
    )
    args = parser.parse_args()
    main(args)
