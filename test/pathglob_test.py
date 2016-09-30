from fosslint.pathglob import pathglob_compile

from unittest import TestCase

class GlobTest(TestCase):
    def test_something(self):
        p = pathglob_compile('/*/**/*.bin')
        self.assertTrue(p('/hello/this/is/the/end.bin'))

        p = pathglob_compile('*.bin')
        self.assertTrue(p('/hello/this/is/the/end.bin'))

        p = pathglob_compile('*.bin|*.baz')
        self.assertTrue(p('/hello/this/is/the/end.bin'))
        self.assertTrue(p('/hello/this/is/the/end.baz'))
