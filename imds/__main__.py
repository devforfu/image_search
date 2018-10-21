"""
Retrieves a bunch of images using Bing API and saves them into specific
folder.

Search queries could be provided via command line, or using txt file with
each query on a separate line. When using command line, each query should
be separated with '|' symbols. By default, maximum 1000 images are retrieved
from each query.

For example, to download images with single query:
    $ python -m imds download human face photo

To use several queries and save into specific folder:
    $ python -m imds download -o /output/dir dog image | cat image

Read queries from txt file:
    $ python -m imds download -f queries.txt

"""
import argparse
import os
from textwrap import dedent

from .search import BingImageSearch
from .package import create_tar


def main():
    args = parse_args()
    command = args['command']

    if command == 'download':
        if 'file' in args:
            queries = [line.strip() for line in open(args['file'])]
        else:
            queries = args.get('queries')
        search = BingImageSearch(api_key=args.get('key'))
        search.download(queries, limit=args['limit'], folder=args['output'])

    elif command == 'package':
        create_tar(args['dir'], args['output'])


def parse_args():
    parser = argparse.ArgumentParser(
        prog='python -m imds',
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)

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
    cmd_download.add_argument(
        '-l', '--limit',
        type=int, default=1000,
        help='Approx. maximal number of downloaded images per query.')
    cmd_download.add_argument(
        '-f', '--file',
        default=None,
        help='File with queries in txt format; one query per line.')

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
