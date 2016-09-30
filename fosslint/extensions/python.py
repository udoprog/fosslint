from .extension import Extension

class Python(Extension):
    def __init__(self, path, opt):
        self.path = path
        self.opt = opt

    def find_header_range(self, lines):
        if len(lines) == 0:
            return (0, 0)

        start = 0

        for i, line in enumerate(lines):
            if i == 0 and line.startswith('#!'):
                start = 1
                continue

            if not line.rstrip().startswith('#'):
                return (start, i)

        return (start, i + 1)

    def render_header_comment(self, lines):
        for line in lines:
            s = line.rstrip()

            if len(s) == 0:
                yield u"#"
            else:
                yield u"# " + s
