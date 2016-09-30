from .extension import Extension

class Java(Extension):
    def __init__(self, path, opt):
        self.path = path
        self.opt = opt
        self.start_comment = opt.start_comment if opt.start_comment else "/**"
        self.end_comment = opt.end_comment if opt.end_comment else "**/"

    def find_header_range(self, lines):
        for i, line in enumerate(lines):
            if i == 0:
                if not line.lstrip().startswith(self.start_comment):
                    break

            if line.rstrip().endswith(self.end_comment):
                return (0, i + 1)

            if line.lstrip().startswith('*'):
                continue

        return (0, 0)

    def render_header_comment(self, lines):
        yield self.start_comment

        for line in lines:
            s = line.rstrip()

            if len(s) == 0:
                yield u' *'
            else:
                yield u' * ' + line.rstrip()

        yield u' ' + self.end_comment
