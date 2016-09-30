import datetime

from .licenses import load_license

class GlobalSection:
    def __init__(self, context):
        self._expect_license = None
        self._context = context
        self.year = None
        self.entity = 'Entity'
        self.start_year = None
        self.auto_year = True
        self.year_range_format = "{start} - {end}"
        self.strip_license = False
        self.license_header = None
        self.license_header_path = None
        self.license_header_pad = None

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

        start_year = section.get('start_year')

        if start_year:
            self.start_year = start_year

        year_range_format = section.get('year_range_format')

        if year_range_format:
            self.year_range_format = year_range_format

        strip_license = section.getboolean('strip_license')

        if strip_license is not None:
            self.strip_license = strip_license

        license_header = section.get('license_header')

        if license_header:
            self.license_header = self._context.load_license_header(
                license_header)

        license_header_path = section.get('license_header_path')

        if license_header_path:
            self.license_header_path = self._context.load_license_header_path(
                self._context.absolute_path(license_header_path))

        license_header_pad = section.get('license_header_pad')

        if license_header_pad:
            self.license_header_pad = license_header_pad

    def verify(self):
        if self.entity is None:
            raise Exception('Missing option \'entity\'')

        if self.year is None:
            if self.auto_year:
                self.year = str(datetime.datetime.now().year)
            else:
                raise Exception('Missing global option \'year\'')

        if self.start_year is not None:
            self.year = self.year_range_format.format(
                start=self.start_year, end=self.year
            )
