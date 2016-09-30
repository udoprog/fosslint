from .policy import Policy

from ..pattern_section import PatternSection


class Spotify10(Policy):
    name = "Spotify 1.0"

    def __init__(self, section):
        pass

    def apply(self, context, global_section, patterns):
        global_section.entity = 'Spotify AB'
        global_section.expect_license = 'Apache 2.0'
        global_section.auto_year = True

        patterns.append(PatternSection.build(
            context, '/**/*.py',
            license_header = 'Apache 2.0'
        ))

        patterns.append(PatternSection.build(
            context, '*.java',
            start_comment = '/*',
            end_comment = '*/'
        ))

        patterns.append(PatternSection.build(
            context, '/**/src/main/**/*.java',
            license_header = 'Apache 2.0'
        ))
