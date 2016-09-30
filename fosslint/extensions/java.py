from .extension import Extension
from .common import CBasedComments

class Java(CBasedComments, Extension):
    def __init__(self, context, path, opt):
        super().__init__(context, path, opt)
        self.path = path
        self.opt = opt

    @classmethod
    def matches(cls, path, opt):
        if opt.language == 'java':
            return True

        if path.endswith('.java'):
            return True

        return False
