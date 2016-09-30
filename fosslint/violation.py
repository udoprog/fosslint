class Violation:
    def __init__(self, path, line, **kw):
        self.path = path
        self.line = line
        self.message = kw.pop('message', 'No Error')
        self.kind = kw.pop('kind', 'UNKNOWN')
        self.fix = kw.pop('fix', lambda: ())
        self.describe_fix = kw.pop('describe_fix', lambda: "No Description")
        self.diff = kw.pop('diff', None)
