from .java import Java
from .python import Python

EXTENSIONS = {}
EXTENSIONS['.py'] = Python
EXTENSIONS['.java'] = Java

def load_extension(ext, path, opt):
    try:
        ext = EXTENSIONS[ext]
    except KeyError:
        ext = Extension

    return ext(path, opt)
