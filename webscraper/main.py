#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

import argparse
import sys

from webscraper import metadata
from webscraper.webscrapper import WebScrapper


def main(argv):
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = '''
{project} {version}

{authors}
URL: <{url}>
'''.format(
        project=metadata.project,
        version=metadata.version,
        authors='\n'.join(author_strings),
        url=metadata.url)

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        description=metadata.description,
        epilog=epilog)
    arg_parser.add_argument("-url", "--url", dest="url_to_scrap",
                        help="URL to scrap", metavar="STRING")

    if len(argv) > 2:
        if argv[1] == '-url' or argv[1] == '--url':
            scrapper = WebScrapper("https://www.lonelyplanet.com/africa/attractions/a/poi-sig/355064")
            # scrapper = WebScrapper(argv[2])

    arg_parser.parse_args(args=argv[1:])

    print(epilog)

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
