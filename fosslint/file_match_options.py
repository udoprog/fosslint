import difflib
import itertools
import os

from .violation import Violation
from .licenses import load_license_header
from .licenses import load_license_header_path
from .extensions import load_extension

class FileMatchOptions:
    def __init__(self, root, global_opt, relative, path):
        self.root = root
        self.global_opt = global_opt
        self.expect_license_header = None
        self.custom_license_header_path = None
        self.relative = relative
        self.path = path
        self.start_comment = None
        self.end_comment = None

    def absolute_path(self, path):
        """
        Get the absolute path as defined by the root of the project.
        """

        if path.startswith('/'):
            return path

        return os.path.join(self.root, path)

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
                self.absolute_path(custom_license_header_path))

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


