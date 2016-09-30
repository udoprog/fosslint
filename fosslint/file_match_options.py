import difflib
import itertools
import os

from .violation import Violation
from .licenses import load_license_header
from .licenses import load_license_header_path
from .extensions import load_extension
from .utils import strip_lineend

class FileMatchOptions:
    def __init__(self, global_section, relative, path):
        self.global_section = global_section
        self.relative = relative
        self.path = path
        self.license_header = global_section.license_header
        self.license_header_path = global_section.license_header_path
        self.license_header_pad = global_section.license_header_pad
        self.start_comment = None
        self.end_comment = None
        self.skip_header_lines = None
        self.skip_header_on_stanza = None
        self.strip_license = global_section.strip_license
        self.language = None

    @property
    def kw(self):
        return {
            "entity": self.global_section.entity,
            "year": self.global_section.year
        }

    def load_section(self, section):
        if section.license_header is not None:
            self.license_header = section.license_header

        if section.license_header_path is not None:
            self.license_header_path = section.license_header_path

        if section.start_comment is not None:
            self.start_comment = section.start_comment

        if section.end_comment is not None:
            self.end_comment = section.end_comment

        if section.skip_header_lines is not None:
            self.skip_header_lines = section.skip_header_lines

        if section.skip_header_on_stanza is not None:
            self.skip_header_on_stanza = section.skip_header_on_stanza

        if section.strip_license is not None:
            self.strip_license = section.strip_license

        if section.language is not None:
            self.language = section.language

        if section.license_header_pad is not None:
            self.license_header_pad = section.license_header_pad

    def evaluate(self, context):
        ext = load_extension(context, self.path, self)

        errors = []

        license_header = None

        if self.license_header is not None:
            license_header = self.license_header

        if self.license_header_path is not None:
            license_header = self.license_header_path

        if license_header is not None:
            errors.append(self.check_expect_line_header(
                self.path, ext, license_header))

        return list(itertools.chain(*errors))

    def render_fixed(self, path, ext, range_index, license_header):
        lines = []

        with open(path) as f:
            for line in f:
                lines.append(line)

        rendered = ext.render_header_comment(
            license_header.render(**self.kw)
        )

        start_index, end_index = range_index

        for line in lines[:start_index]:
            yield line

        for line, header_line in enumerate(rendered):
            if self.skip_header_lines and self.skip_header_lines(line):
                yield lines[line]
            else:
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

        try:
            original_file = list(open(path))
        except:
            raise Exception("Failed to read original file: " + path)

        file_lines = list(map(strip_lineend, original_file))

        # the last line of the header block
        range_index = ext.find_header_range(file_lines)

        if range_index != (0, 0):
            start_index, end_index = range_index
            file_lines = file_lines[start_index:end_index]

            stanza = self.skip_header_on_stanza

            # skip header stanza is defined and matches a header line.
            if stanza and any(stanza in line for line in file_lines):
                return

        for i, (line, expect) in enumerate(zip(file_lines, expected_lines)):
            if self.skip_header_lines and self.skip_header_lines(i):
                continue

            if line != expect:
                yield Violation(
                    path=path,
                    line=i,
                    message="\"{}\" != \"{}\"".format(line, expect),
                    kind="License Header Mismatch",
                    fix=lambda: self.fix_expect_line_header(
                        path, ext, range_index, license_header
                    ),
                    describe_fix=lambda: "Fix Header",
                    diff=self.build_diff(
                        original_file, path, ext, range_index, license_header
                    )
                )

                break


