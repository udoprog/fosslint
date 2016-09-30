from fosslint.extensions import python

from unittest import TestCase
from unittest.mock import Mock

class PythonTest(TestCase):
    def test_find_header_range(self):
        context = Mock()
        path = Mock()
        opt = Mock()

        ext = python.Python(context, path, opt)

        self.assertEquals((0, 3), ext.find_header_range([
            '#',
            '# DO NOT CARE',
            '#'
        ]))

        # skip shebang
        self.assertEquals((1, 4), ext.find_header_range([
            '#!foo',
            '#',
            '# DO NOT CARE',
            '#'
        ]))

        self.assertEquals((0, 0), ext.find_header_range([]))
        self.assertEquals((0, 0), ext.find_header_range([
            'import sys'
        ]))
