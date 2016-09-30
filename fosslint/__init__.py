import os
import argparse
import configparser
import sys

from .pathglob import pathglob_compile
from .policies import load_policy

from .context import Context
from .global_section import GlobalSection
from .file_match_options import FileMatchOptions
from .pattern_section import PatternSection

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

    # patterns to ignore
    ignored = []
    # patterns to evalute
    patterns = []
    # global configuration
    global_section = GlobalSection()
    # context for local configurations
    context = Context(ns.root)

    for section in config.sections():
        if section.startswith('policy:'):
            _, name = section.split(':', 1)
            options = config.options(section)
            policy = load_policy(name, options)
            print('Applying Policy: ' + policy.name)
            policy.apply(context, global_section, patterns)
            continue

        if section == 'global':
            global_section.parse_section(config[section])
            continue

        if section.startswith('ignore:'):
            _, rest = section.split(':', 1)
            ignored.append(pathglob_compile(rest))
            continue

        p = PatternSection.parse(context, section, config[section])

        if p:
            patterns.append(p)
            continue

        raise Exception('Unsupported section (' + section + ')')

    global_section.verify()

    checks_by_file = dict()

    checks = []

    for (path, relative) in iterate_files(ns.root):
        # is the file ignored
        if any(ign.match(relative) for ign in ignored):
            continue

        for s in patterns:
            if s.pattern.search(relative) is None:
                continue

            try:
                opt = checks_by_file[relative]
            except KeyError:
                opt = checks_by_file[relative] = FileMatchOptions(
                    global_section, relative, path)

            opt.load_section(s)

    for relative, opt in sorted(checks_by_file.items(), key=lambda e: e[0]):
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
