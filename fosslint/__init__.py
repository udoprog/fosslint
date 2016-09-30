import os
import argparse
import configparser
import itertools
import datetime
import difflib
import sys
import contextlib

from .pathglob import pathglob_compile
from .policies import load_policy
from .licenses import load_license
from .licenses import load_license_header
from .licenses import load_license_header_path
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
        self.diff = kw.pop('diff', None)


class GlobalOptions:
    def __init__(self):
        self.expect_license = None
        self.year = None
        self.entity = None
        self.base_year = None
        self.auto_year = False

    def parse_section(self, section):
        expect_license = section.get('expect_license')

        if expect_license:
            self.expect_license = load_license(expect_license)

        entity = section.get('entity')

        if entity:
            self.entity = entity

        year = section.get('year')

        if year:
            self.year = year

        auto_year = section.getboolean('auto_year')

        if auto_year is not None:
            self.auto_year = auto_year

        base_year = section.get('base_year')

        if base_year:
            self.base_year = base_year

    def verify(self):
        if self.entity is None:
            raise Exception('Missing option \'entity\'')

        if self.year is None:
            if self.auto_year:
                self.year = str(datetime.datetime.now().year)
            else:
                raise Exception('Missing global option \'year\'')

        if self.base_year is not None:
            self.year = "{}-{}".format(self.base_year, self.year)


class FileMatchOptions:
    def __init__(self, global_opt, relative, path):
        self.global_opt = global_opt
        self.expect_license_header = None
        self.custom_license_header_path = None
        self.relative = relative
        self.path = path
        self.start_comment = None
        self.end_comment = None

    @property
    def kw(self):
        return {"entity": self.global_opt.entity, "year": self.global_opt.year}

    def parse_section(self, section):
        expect_license_header = section.get('expect_license_header')

        if expect_license_header:
            self.expect_license_header = load_license_header(
                expect_license_header)

        custom_license_header_path = section.get('custom_license_header_path')

        if custom_license_header_path:
            self.custom_license_header_path = load_license_header_path(
                custom_license_header_path)

        start_comment = section.get('start_comment')

        if start_comment:
            self.start_comment = start_comment

        end_comment = section.get('end_comment')

        if end_comment:
            self.end_comment = end_comment

    def evaluate(self):
        _, ext = os.path.splitext(self.path)

        ext = load_extension(ext, self.path, self)

        errors = []

        license_header = None

        if self.expect_license_header is not None:
            license_header = self.expect_license_header

        if self.custom_license_header_path is not None:
            license_header = self.custom_license_header_path

        if license_header is not None:
            errors.append(self.check_expect_line_header(
                self.path, ext, license_header))

        return list(itertools.chain(*errors))

    def render_fixed(self, path, ext, range_index, license_header):
        lines = []

        with open(path) as f:
            for line in f:
                lines.append(line)

        rendered = ext.render_header_comment(license_header.render(**self.kw))

        start_index, end_index = range_index

        for line in lines[:start_index]:
            yield line

        for header_line in rendered:
            yield header_line + u'\n'

        for line in lines[end_index:]:
            yield line

    def fix_expect_line_header(self, path, ext, range_index, license_header):
        fixed = list(self.render_fixed(path, ext, range_index, license_header))

        with open(path, 'w') as f:
            for line in fixed:
                f.write(line)

    def build_diff(self, original_file, path, ext, range_index, license_header):
        def f():
            fixed = list(
                self.render_fixed(path, ext, range_index, license_header)
            )

            return difflib.unified_diff(
                original_file, fixed,
                fromfile=path, tofile=path + '.fix'
            )

        return f

    def check_expect_line_header(self, path, ext, license_header):
        """
        Check that the given license header matches.
        """

        expected_lines = ext.render_header_comment(
            license_header.render(**self.kw)
        )

        original_file = list(open(path))
        file_lines = [l.rstrip() for l in original_file]

        # the last line of the header block
        range_index = ext.find_header_range(file_lines)

        if range_index != (0, 0):
            start_index, end_index = range_index
            file_lines = file_lines[start_index:end_index]

        for i, (line, expect) in enumerate(zip(file_lines, expected_lines)):
            if line != expect:
                yield Violation(
                    path=path,
                    line=i,
                    message="\"{}\" != \"{}\"".format(line, expect),
                    kind="License Header Mismatch",
                    fix=lambda: self.fix_expect_line_header(
                        path, ext, range_index, license_header
                    ),
                    describe_fix=lambda: "Prepend Header",
                    diff=self.build_diff(
                        original_file, path, ext, range_index, license_header
                    )
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
                    global_opt, relative, path)

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
