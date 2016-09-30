import os
import argparse
import configparser
import sys

from .pathglob import pathglob_compile
from .policies import load_policy

from .global_options import GlobalOptions
from .file_match_options import FileMatchOptions

ETC="/etc/fosslint.conf"
DOTFILE=".fosslint"


def setup_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'root',
        nargs='?',
        metavar="<dir>",
        help="directory to process",
        default=os.getcwd()
    )

    parser.add_argument(
        '--fix',
        help="Fix found problems",
        action="store_const",
        const=True,
        default=False
    )

    parser.add_argument(
        '--yes',
        help="Automatically answer yes when asked to apply a fix",
        action="store_const",
        const=True,
        default=False
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


def wait_for_yes(message):
    while True:
        line = input(message + ' [y/n]? ')
        line = line.strip()

        if line == 'y':
            return True

        if line == 'n':
            return False

        print('Expected \'y\' or \'n\'')


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

    policies = []

    # find policies
    for section in config.sections():
        if section.startswith('policy:'):
            _, name = section.split(':', 1)
            options = config.options(section)
            policies.append(load_policy(name, options))
            continue

    # apply policies
    for policy in policies:
        print("Applying Policy: {}".format(policy.name))
        policy.apply(config)

    matchers = []
    global_opt = GlobalOptions()

    for section in config.sections():
        if section.startswith('policy:'):
            continue

        if section == 'global':
            global_opt.parse_section(config[section])
            continue

        if section.startswith('pattern:'):
            _, rest = section.split(':', 1)
            matchers.append((pathglob_compile(rest), config[section]))
            continue

        raise Exception('Unsupported section (' + section + ')')

    global_opt.verify()

    checkers = dict()

    checks = []

    for (path, relative) in iterate_files(ns.root):
        for (pat, section) in matchers:
            if pat.fullmatch(relative) is None:
                continue

            try:
                opt = checkers[relative]
            except KeyError:
                opt = checkers[relative] = FileMatchOptions(
                    ns.root, global_opt, relative, path)

            opt.parse_section(section)

    for relative, opt in sorted(checkers.items(), key=lambda e: e[0]):
        checks.append((opt, opt.evaluate()))

    if all(len(e) == 0 for p, e in checks):
        print("Performed {} check(s), no issues found :)".format(len(checks)))
        return

    for (opt, errors) in checks:
        for e in errors:
            print("{}:{} - {} ({})".format(e.path, e.line, e.kind, e.message))

            if ns.fix:
                if e.diff:
                    for line in e.diff():
                        sys.stdout.write(line)

                if ns.yes or wait_for_yes(e.describe_fix()):
                    print("Fixing: {}".format(e.path))
                    e.fix()
                else:
                    print("NOT fixing: {}".format(e.path))
