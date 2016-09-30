import re

def pathglob_compile(pattern):
    """
    Implements a strict pattern matching algorithm suitable for file paths.

    Convert the given pattern into a regular expression where:

        `|` - divides the match into multiple sections where any may match.
        `**` - matches any directories.
        `*` - matches anything inside a single directory.
    """

    sections = pattern.split('|')
    expressions = []

    for section in sections:
        parts = section.split('/')
        results = []

        for p in parts:
            if p == '**':
                results.append('.*')
                continue

            results.append('[^/]+'.join(re.escape(s) for s in p.split('*')))

        # only require a full match if pattern is absolute
        if pattern.startswith('/'):
            expressions.append(re.compile('^' + '/'.join(results) + '$'))
        else:
            expressions.append(re.compile('/'.join(results) + '$'))

    def search(string):
        result = any(r.search(string) is not None for r in expressions)
        return result

    return search
