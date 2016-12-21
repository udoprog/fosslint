import os
import argparse
import configparser
import sys

from .config import Config
from .pathglob import pathglob_compile
from .policies import load_policy

from .context import Context
from .global_section import GlobalSection
from .file_match_options import FileMatchOptions
from .pattern_section import PatternSection

ETC="/etc/fosslint.conf"
DOTFILE=".fosslint"

def init_action(ns):
    dotfile = os.path.join(ns.root, DOTFILE)

    if os.path.isfile(dotfile):
        print('Config file already exists: ' + dotfile)
        return 1

    print('Setting up default configuration: ' + dotfile)

    with open(dotfile, 'w') as f:
        print('[global]', file=f)


def check_action(ns):
    home = os.path.join(os.path.expanduser('~'), DOTFILE)
    configs = [ETC, home, os.path.join(ns.root, DOTFILE)]

    config_parser = configparser.RawConfigParser()

    for c in configs:
        if not os.path.isfile(c):
            continue

        config_parser.read(c)

    config = Config(config_parser)

    # patterns to ignore
    ignored = []
    # patterns to evalute
    patterns = []
    # context for local configurations
    context = Context(ns.root)
    # global configuration
    global_section = GlobalSection(context)

    for section in config.sections():
        if section.startswith('policy:'):
            _, name = section.split(':', 1)
            section = config[section]
            policy = load_policy(name, section)
            print('Applying Policy: ' + policy.name)
            policy.apply(context, global_section, patterns)
            continue

    for section in config.sections():
        if section.startswith('policy:'):
            # already applied
            continue

        if section == 'global':
            global_section.parse_section(config[section])
            continue

        if section.startswith('ignore:'):
            _, rest = section.split(':', 1)
            ignored.append(pathglob_compile(rest))
            continue

        if section.startswith('pattern:'):
            patterns.append(
                PatternSection.parse(context, section, config[section]))
            continue

        raise Exception('Unsupported section (' + section + ')')

    global_section.verify()

    checks_by_file = dict()

    checks = []

    for (path, relative) in iterate_files(ns.root):
        # is the file ignored
        if any(ign(relative) for ign in ignored):
            continue

        for s in patterns:
            if not s.pattern(relative):
                continue

            try:
                opt = checks_by_file[relative]
            except KeyError:
                opt = checks_by_file[relative] = FileMatchOptions(
                    global_section, relative, path)

            opt.load_section(s)

    for relative, opt in sorted(checks_by_file.items(), key=lambda e: e[0]):
        if ns.verbose:
            print('Checking: ' + relative)

        checks.append((opt, opt.evaluate(context)))

    if all(len(e) == 0 for p, e in checks):
        print("Performed {} check(s), no issues found :)".format(len(checks)))
        return 0

    for (opt, errors) in checks:
        for e in errors:
            print("{}:{} - {}:".format(e.path, e.line, e.kind))
            print("  {}".format(e.message))

            if ns.fix:
                if e.diff:
                    for line in e.diff():
                        sys.stdout.write(line)

                if ns.yes or wait_for_yes(e.describe_fix()):
                    print("Fixing: {}".format(e.path))
                    e.fix()
                else:
                    print("NOT fixing: {}".format(e.path))

    return 1


def setup_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--root',
        metavar="<dir>",
        help="Directory to process",
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

    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        help="Increase verbosity",
        action="store_const",
        const=True,
        default=False
    )

    parser.set_defaults(action=check_action)

    subparsers = parser.add_subparsers(
        title='Action to take (default: check)',
        help="Action to take"
    )

    check = subparsers.add_parser(
        'check', help="Check for violations in a project")
    check.set_defaults(action=check_action)

    init = subparsers.add_parser(
        'init', help="Initialize a project with a default configuration")
    init.set_defaults(action=init_action)

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


def main():
    parser = setup_parser()
    ns = parser.parse_args()

    return ns.action(ns)

def entry():
    sys.exit(main())
