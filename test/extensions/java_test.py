from fosslint.extensions import java

from unittest import TestCase
from unittest.mock import Mock

class JavaTest(TestCase):
    def test_find_header_end(self):
        path = Mock()

        opt = Mock()
        opt.start_comment = None
        opt.end_comment = None

        ext = java.Java(path, opt)

        self.assertEquals((0, 3), ext.find_header_range([
            '/**',
            ' * DO NOT CARE',
            ' **/'
        ]))

    def test_find_header_range_configured(self):
        path = Mock()

        opt = Mock()
        opt.start_comment = '/*'
        opt.end_comment = '*/'

        ext = java.Java(path, opt)

        self.assertEquals((0, 3), ext.find_header_range([
            '/*',
            ' * DO NOT CARE',
            ' */'
        ]))
