class Extension:
    """
    Base class for extension helpers.
    """

    def __init__(self, context, path, opt):
        pass

    def find_header_range(self, lines):
        """
        Find the range in lines (zero-based) that the header occupies.
        """

        return (0, 0)

    def render_header_comment(self, lines):
        """
        Render the header comment given the lines of a license.
        """

        for line in lines:
            yield line

    @classmethod
    def matches(cls, path):
        """
        Check if this extension matches the given path.
        """
        return False
