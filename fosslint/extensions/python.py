from .extension import Extension
from .common import HashBasedComments

class Python(HashBasedComments, Extension):
    def __init__(self, context, path, opt):
        super().__init__(context, path, opt)
        self.context = context
        self.path = path
        self.opt = opt

    @classmethod
    def matches(cls, path, opt):
        if opt.language == 'python':
            return True

        if path.endswith('.py'):
            return True

        return False
