class Extension:
    def __init__(self, path, opt):
        pass

    def find_header_end(self, lines):
        """
        Find which line number (zero-based) that the license header ends at.
        """
        return 0

    def render_header_comment(self, lines):
        for line in lines:
            yield line


class Java(Extension):
    def __init__(self, path, opt):
        self.path = path
        self.opt = opt
        self.comment_start = opt.start_comment if opt.start_comment else "/**"
        self.comment_end = opt.end_comment if opt.end_comment else "**/"

    def find_header_end(self, lines):
        for i, line in enumerate(lines):
            if i == 0:
                if not line.lstrip().startswith(self.comment_start):
                    return i

            if line.rstrip().endswith(self.comment_end):
                return i + 1

            if line.lstrip().startswith('*'):
                continue

        return 0

    def render_header_comment(self, lines):
        yield self.comment_start

        for line in lines:
            s = line.rstrip()

            if len(s) == 0:
                yield u' *'
            else:
                yield u' * ' + line.rstrip()

        yield u' ' + self.comment_end


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


EXTENSIONS = {}
EXTENSIONS['.py'] = Python
EXTENSIONS['.java'] = Java

def load_extension(ext, path, opt):
    try:
        ext = EXTENSIONS[ext]
    except KeyError:
        ext = Extension

    return ext(path, opt)
