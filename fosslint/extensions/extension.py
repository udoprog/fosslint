class Extension:
    """
    Base class for extension helpers.
    """

    def __init__(self, path, opt):
        pass

    def find_header_end(self, lines):
        """
        Find which line number (zero-based) that the license header ends at.
        """

        return 0

    def render_header_comment(self, lines):
        """
        Render the header comment given the lines of a license.
        """

        for line in lines:
            yield line


