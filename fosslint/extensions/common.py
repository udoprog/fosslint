from .extension import Extension

class HashBasedComments:
    """
    Comments that are hash-based (#).
    """

    def __init__(self, context, path, opt):
        self.context = context
        self.pad = opt.license_header_pad if opt.license_header_pad else u' '
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
            s = self.context.strip_lineend(line)

            if self.opt.strip_license and len(s) == 0:
                yield u'#'
                continue

            yield u'#' + self.pad + s

class CBasedComments:
    """
    Comments that are based on C.
    """

    def __init__(self, context, path, opt):
        self.context = context
        self.start_comment = opt.start_comment if opt.start_comment else u'/*'
        self.end_comment = opt.end_comment if opt.end_comment else u'*/'
        self.pad = opt.license_header_pad if opt.license_header_pad else u' '
        self.opt = opt

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
            s = self.context.strip_lineend(line)

            if self.opt.strip_license and len(s) == 0:
                yield u' *'
                continue

            yield u' *' + self.pad + s

        yield u' ' + self.end_comment
