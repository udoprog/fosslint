import os
import argparse
import configparser
import fnmatch
import re

from .licenses import load_license

ETC="/etc/fosslint.conf"
DOTFILE=".fosslint"


class GlobalOptions:
    def __init__(self):
        self.expect_license = None

    def parse(self, key, value):
        if key == "expect_license":
            self.expect_license = load_license(value)
            return

        raise Exception('Unsupported option (' + key + ')')


class MatchOptions:
    def __init__(self):
        self.expect_license_header = None

    def parse(self, key, value):
        if key == "expect_license_header":
            self.expect_license_header = load_license(value)
            return

        raise Exception('Unsupported option (' + key + ')')


def setup_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'root',
        nargs='?',
        metavar="<dir>",
        help="directory to process",
        default=os.getcwd()
    )

    return parser


def iterate_files(root):
    queue = [(root, '')]

    while len(queue) > 0:
        (path, rel) = queue.pop()

        for name in os.listdir(path):
            next_path = os.path.join(path, name)
            next_relative = '/'.join([rel, name])

            if os.path.isdir(next_path):
                queue.append((next_path, next_relative))
            else:
                yield (next_path, next_relative)


def entry():
    parser = setup_parser()
    ns = parser.parse_args()
    home = os.path.join(os.path.expanduser('~'), DOTFILE)
    configs = [ETC, home, os.path.join(ns.root, DOTFILE)]

    config = configparser.RawConfigParser()

    for c in configs:
        if not os.path.isfile(c):
            continue

        config.read(c)

    matchers = []

    global_opt = GlobalOptions()

    for section in config.sections():
        if section == 'global':
            for (key, value) in config.items(section):
                global_opt.parse(key, value)

            continue

        if section.startswith('pattern:'):
            _, rest = section.split(':', 1)

            pat = re.compile(fnmatch.translate(rest))
            opt = MatchOptions()

            for (key, value) in config.items(section):
                opt.parse(key, value)

            matchers.append((pat, opt))
            continue

        raise Exception('Unsupported section (' + section + ')')

    for (path, relative) in iterate_files(ns.root):
        for (pat, opt) in matchers:
            if pat.fullmatch(relative) is not None:
                print("MATCH", path)
                break
