import datetime

from .licenses import load_license

class GlobalSection:
    def __init__(self):
        self._expect_license = None
        self.year = None
        self.entity = None
        self.base_year = None
        self.auto_year = False

    def set_expect_license(self, name):
        self._expect_license = load_license(name)

    def get_expect_license(self):
        return self._expect_license

    expect_license = property(get_expect_license, set_expect_license)

    def parse_section(self, section):
        expect_license = section.get('expect_license')

        if expect_license:
            self.expect_license = expect_license

        entity = section.get('entity')

        if entity:
            self.entity = entity

        year = section.get('year')

        if year:
            self.year = year

        auto_year = section.getboolean('auto_year')

        if auto_year is not None:
            self.auto_year = auto_year

        base_year = section.get('base_year')

        if base_year:
            self.base_year = base_year

    def verify(self):
        if self.entity is None:
            raise Exception('Missing option \'entity\'')

        if self.year is None:
            if self.auto_year:
                self.year = str(datetime.datetime.now().year)
            else:
                raise Exception('Missing global option \'year\'')

        if self.base_year is not None:
            self.year = "{} - {}".format(self.base_year, self.year)
