import configparser

BOOLEAN_TRUE = set(['true'])

def unquote(string):
    """
    Unqoute escape sequences in the given string.
    TODO: implement this
    """

    return string

class Config:
    def __init__(self, config):
        self.config = config

    def sections(self):
        return self.config.sections()

    def __getitem__(self, section):
        return Section(self.config[section])

class Section:
    def __init__(self, section):
        self.section = section

    def get(self, key):
        value = self.section.get(key)

        if value is None:
            return None

        if value.startswith('"') and value.endswith('"'):
            return unquote(value[1:-1])

        return value

    def getboolean(self, key):
        value = self.get(key)

        if value is None:
            return None

        return value in BOOLEAN_TRUE
