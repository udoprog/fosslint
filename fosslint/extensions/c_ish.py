from .extension import Extension
from .common import CBasedComments

class CIsh(CBasedComments, Extension):
    """
    C-ish languages (C, C++).
    """

    def __init__(self, context, path, opt):
        super().__init__(context, path, opt)
        self.path = path
        self.opt = opt

    @classmethod
    def matches(cls, path, opt):
        if opt.language == 'c-like':
            return True

        if path.endswith('.h'):
            return True

        if path.endswith('.hpp'):
            return True

        if path.endswith('.c'):
            return True

        if path.endswith('.cpp'):
            return True

        return False
