from .pathglob import pathglob_compile


def parse_lines(input):
    parts = input.split(',')

    ranges = list()

    for p in parts:
        r = p.split('-', 1)

        if len(r) == 1:
            n = int(r[0])
            ranges.append((n, n))
        else:
            f, t = int(r[0]), int(r[1])
            ranges.append((f, t))

    def m(line):
        for (start, end) in ranges:
            if line >= start and line <= end:
                return True

        return False

    return m


class PatternSection:
    def __init__(self, pattern, **kw):
        self.pattern = pattern
        self.expect_license_header = kw.get('expect_license_header', None)
        self.custom_license_header_path = kw.get('custom_license_header_path', None)
        self.start_comment = kw.get('start_comment', None)
        self.end_comment = kw.get('end_comment', None)
        self.skip_header_lines = kw.get('skip_header_lines', None)

    @classmethod
    def build(cls, context, pattern, **kw):
        pattern = pathglob_compile(pattern)

        expect_license_header = kw.get('expect_license_header', None)

        if expect_license_header:
            kw['expect_license_header'] = context.load_license_header(
                expect_license_header)

        custom_license_header_path = kw.get('custom_license_header_path', None)

        if custom_license_header_path:
            kw['custom_license_header_path'] = context.load_license_header_path(
                context.absolute_path(custom_license_header_path))

        skip_header_lines = kw.get('skip_header_lines', None)

        if skip_header_lines:
            kw['skip_header_lines'] = parse_lines(skip_header_lines)

        return PatternSection(pattern, **kw)

    @classmethod
    def parse(cls, context, name, section):
        if not name.startswith('pattern:'):
            raise Exception('Expected pattern section')

        _, pattern = name.split(':', 1)

        expect_license_header = section.get('expect_license_header')
        custom_license_header_path = section.get('custom_license_header_path')
        start_comment = section.get('start_comment')
        end_comment = section.get('end_comment')
        skip_header_lines = section.get('skip_header_lines')

        return cls.build(context, pattern,
            expect_license_header = expect_license_header,
            custom_license_header_path = custom_license_header_path,
            start_comment = start_comment,
            end_comment = end_comment,
            skip_header_lines = skip_header_lines
        )
