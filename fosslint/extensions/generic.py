from .extension import Extension
from .common import HashBasedComments

class Hash(HashBasedComments, Extension):
    def __init__(self, context, path, opt):
        super().__init__(context, path, opt)
        self.context = context
        self.path = path
        self.opt = opt

    @classmethod
    def matches(cls, path, opt):
        return opt.language == 'hash'
