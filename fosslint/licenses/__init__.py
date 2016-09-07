import pkg_resources

class License:
    def __init__(self, full, header):
        self.full = full
        self.header = header


class LicenseInstance:
    def __init__(self, full, header):
        self.full = full
        self.header = header

    def render_full(self, **kw):
        for line in self.full:
            yield line.format(**kw)

    def render_header(self, **kw):
        for line in self.header:
            yield line.format(**kw)


LICENSES = {}

LICENSES['Apache 2.0'] = License('apache_2.0.txt', 'apache_2.0_header.txt')


def read_license(path):
    content = pkg_resources.resource_string(__name__, path).decode('utf-8')
    content = content.split(u'\n')
    return content


def load_license(key):
    try:
        license = LICENSES[key]
    except KeyError:
        raise Exception('Unsupported license (' + key + ')')

    full = read_license(license.full)
    header = read_license(license.header)

    return LicenseInstance(full, header)
