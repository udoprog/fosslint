import re

def pathglob_compile(pattern):
    """
    Implements a strict pattern matching algorithm suitable for file paths.

    Convert the given pattern into a regular expression where:

        `**` - matches any directories.
        `*` - matches anything inside a single directory.
    """

    parts = pattern.split('/')
    results = []

    for p in parts:
        if p == '**':
            results.append('.*')
            continue

        results.append('[^/]+'.join(re.escape(s) for s in p.split('*')))

    return re.compile('^' + '/'.join(results) + '$')
