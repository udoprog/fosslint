from .policy import Policy


class Spotify10(Policy):
    name = "Spotify 1.0"

    def __init__(self, options):
        pass

    def apply(self, config):
        if not config.has_section('global'):
            config.add_section('global')

        config.set('global', 'entity', 'Spotify AB')
        config.set('global', 'expect_license', 'Apache 2.0')
        config.set('global', 'auto_year', 'true')

        if not config.has_section('pattern:/**/*.py'):
            config.add_section('pattern:/**/*.py')

        config.set('pattern:/**/*.py', 'expect_license_header', 'Apache 2.0')

        if not config.has_section('pattern:**/src/main/**/*.java'):
            config.add_section('pattern:**/src/main/**/*.java')

        config.set(
            'pattern:**/src/main/**/*.java', 'expect_license_header',
            'Apache 2.0')
