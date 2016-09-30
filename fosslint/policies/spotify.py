from .policy import Policy

from ..pattern_section import PatternSection


class Spotify10(Policy):
    name = "Spotify 1.0"

    def __init__(self, options):
        pass

    def apply(self, context, global_section, patterns):
        global_section.entity = 'Spotify AB'
        global_section.expect_license = 'Apache 2.0'
        global_section.auto_year = True

        patterns.append(PatternSection.build(
            context,
            '/**/*.py',
            expect_license_header = 'Apache 2.0'
        ))

        patterns.append(PatternSection.build(
            context,
            '**/src/main/**/*.java',
            expect_license_header = 'Apache 2.0'
        ))
