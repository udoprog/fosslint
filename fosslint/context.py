import os

from .licenses import load_license_header
from .licenses import load_license_header_path
from .utils import strip_lineend

class Context:
    def __init__(self, root):
        self.root = root

    def absolute_path(self, path):
        """
        Get the absolute path as defined by the root of the project.
        """

        if path.startswith('/'):
            return path

        return os.path.join(self.root, path)

    def load_license_header(self, name):
        return load_license_header(name)

    def load_license_header_path(self, path):
        return load_license_header_path(path)

    def strip_lineend(self, line):
        return strip_lineend(line)
