import argparse
import os

from .search import BingImageSearch
from .package import create_tar


def main():
    args = parse_args()
    command = args['command']

    if command == 'download':
        queries = args.get('queries')
        search = BingImageSearch(api_key=args.get('key'))
        search.download(queries, folder=args['output'])

    elif command == 'package':
        create_tar(args['dir'], args['output'])


def parse_args():
    parser = argparse.ArgumentParser()

    commands = parser.add_subparsers(dest='command')

    cmd_download = commands.add_parser('download')
    cmd_download.add_argument(
        '-k', '--key',
        default=None,
        help=f'Explicit Bing API key; '
             f'otherwise use env variable {BingImageSearch.env_var}.')
    cmd_download.add_argument(
        '-o', '--output',
        default=os.getcwd(),
        help=f'Folder to save the output.')

    cmd_package = commands.add_parser('package')
    cmd_package.add_argument(
        '-d', '--dir',
        default=os.getcwd(),
        help='Folder with images')
    cmd_package.add_argument(
        '-o', '--output',
        default=os.path.join(os.getcwd(), 'output'))

    args, queries = parser.parse_known_args()
    args.queries = [q.strip() for q in ' '.join(queries).split('|')]
    return vars(args)


if __name__ == '__main__':
    main()
