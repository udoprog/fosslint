from .extension import Extension

class Python(Extension):
    def __init__(self, path, opt):
        self.path = path
        self.opt = opt

    def find_header_end(self, lines):
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                return i

        return 0

    def render_header_comment(self, lines):
        for line in lines:
            s = line.rstrip()

            if len(s) == 0:
                yield u"#"
            else:
                yield u"# " + s
