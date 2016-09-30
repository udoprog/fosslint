import pkg_resources

class License:
    def __init__(self, full, header):
        self.full = full
        self.header = header


class LicenseText:
    def __init__(self, lines):
        self.lines = lines

    def render(self, **kw):
        for line in self.lines:
            yield line.format(**kw)


LICENSES = {}

LICENSES['Apache 2.0'] = License('apache_2.0.txt', 'apache_2.0_header.txt')


def read_license(path):
    content = pkg_resources.resource_string(__name__, path).decode('utf-8')
    content = content.split(u'\n')
    return LicenseText(content)


def load_license_header_path(path):
    content = list(open(path))
    return LicenseText(content)


def load_license_header(key):
    try:
        license = LICENSES[key]
    except KeyError:
        raise Exception('Unsupported license (' + key + ')')

    return read_license(license.header)


def load_license(key):
    try:
        license = LICENSES[key]
    except KeyError:
        raise Exception('Unsupported license (' + key + ')')

    return read_license(license.full)
