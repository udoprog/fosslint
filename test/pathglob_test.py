from fosslint.pathglob import pathglob_compile

from unittest import TestCase

class GlobTest(TestCase):
    def test_something(self):
        p = pathglob_compile('/*/**/*.bin')
        self.assertIsNotNone(p.match('/hello/this/is/the/end.bin'))
