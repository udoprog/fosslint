import os
import argparse
import configparser
import itertools
import datetime

from .pathglob import pathglob_compile
from .policies import load_policy
from .licenses import load_license
from .extensions import load_extension

ETC="/etc/fosslint.conf"
DOTFILE=".fosslint"


class Violation:
    def __init__(self, path, line, **kw):
        self.path = path
        self.line = line
        self.message = kw.pop('message', 'No Error')
        self.kind = kw.pop('kind', 'UNKNOWN')
        self.fix = kw.pop('fix', lambda: ())
        self.describe_fix = kw.pop('describe_fix', lambda: "No Description")


class GlobalOptions:
    def __init__(self):
        self.expect_license = None
        self.year = None
        self.entity = None
        self.base_year = None
        self.auto_year = False

    def parse(self, key, value):
        if key == 'expect_license':
            self.expect_license = load_license(value)
            return

        if key == 'entity':
            self.entity = value
            return

        if key == 'year':
            self.year = value
            return

        if key == 'auto_year':
            self.auto_year = value
            return

        if key == 'base_year':
            self.base_year = value
            return

        raise Exception('Unsupported option (' + key + ')')

    def verify(self):
        if self.entity is None:
            raise Exception('Missing option \'entity\'')

        if self.year is None:
            if self.auto_year:
                self.year = str(datetime.datetime.now().year)
                return

            raise Exception('Missing global option \'year\'')

        if self.base_year is not None:
            self.year = "{}-{}".format(self.base_year, self.year)


class FileMatchOptions:
    def __init__(self, global_opt):
        self.global_opt = global_opt
        self.expect_license_header = None

    @property
    def kw(self):
        return {"entity": self.global_opt.entity, "year": self.global_opt.year}

    def parse(self, key, value):
        if key == "expect_license_header":
            self.expect_license_header = load_license(value)
            return

        raise Exception('Unsupported option (' + key + ')')

    def evaluate(self, path):
        _, ext = os.path.splitext(path)

        ext = load_extension(ext, path, self)

        errors = []

        if self.expect_license_header is not None:
            errors.append(self.check_expect_line_header(path, ext))

        return itertools.chain(*errors)

    def fix_expect_line_header(self, path, ext, end_index):
        lines = []

        with open(path) as f:
            for line in f:
                lines.append(line)

        rendered = ext.render_header_comment(
            self.expect_license_header.render_header(**self.kw)
        )

        with open(path, 'w') as f:
            for header_line in rendered:
                f.write(header_line + u'\n')

            for line in lines[end_index:]:
                f.write(line)


    def check_expect_line_header(self, path, ext):
        lines = ext.render_header_comment(
            self.expect_license_header.render_header(**self.kw)
        )

        file_lines = list(l[:-1] for l in open(path))

        # the last line of the header block
        end_index = ext.find_header_end(file_lines)

        for i, (line, expect) in enumerate(zip(file_lines, lines)):
            if line != expect:
                yield Violation(
                    path=path,
                    line=i,
                    message="\"{}\" != \"{}\"".format(line, expect),
                    kind="License Header Mismatch",
                    fix=lambda: self.fix_expect_line_header(
                        path, ext, end_index
                    ),
                    describe_fix=lambda: "Prepend Header"
                )

                break


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
            for (key, value) in config.items(section):
                global_opt.parse(key, value)

            continue

        if section.startswith('pattern:'):
            _, rest = section.split(':', 1)

            pat = pathglob_compile(rest)
            opt = FileMatchOptions(global_opt)

            for (key, value) in config.items(section):
                opt.parse(key, value)

            matchers.append((pat, opt))
            continue

        raise Exception('Unsupported section (' + section + ')')

    global_opt.verify()

    issues = []

    for (path, relative) in iterate_files(ns.root):
        for (pat, opt) in matchers:
            if pat.fullmatch(relative) is not None:
                issues.append((opt, opt.evaluate(path)))
                break

    for (opt, errors) in issues:
        for e in errors:
            print("{}:{} - {} ({})".format(e.path, e.line, e.kind, e.message))

            if ns.fix:
                if wait_for_yes(e.describe_fix()):
                    print("Fixing: {}".format(e.path))
                    e.fix()
                else:
                    print("NOT fixing: {}".format(e.path))
