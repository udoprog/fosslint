from .extension import Extension
from .java import Java
from .python import Python
from .c_style import CStyle
from .generic import Hash

EXTENSIONS = []
EXTENSIONS.append(Python)
EXTENSIONS.append(Java)
EXTENSIONS.append(CStyle)
EXTENSIONS.append(Hash)

def load_extension(context, path, opt):
    for ext in EXTENSIONS:
        if ext.matches(path, opt):
            return ext(context, path, opt)

    raise Exception('Cannot determine language of file: ' + path)
