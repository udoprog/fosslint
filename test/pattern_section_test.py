from fosslint.pattern_section import PatternSection
from fosslint.pattern_section import parse_lines

import configparser

from unittest import TestCase
from unittest.mock import Mock

class PatternSectionTest(TestCase):
    def test_something(self):
        context = Mock()

        config = configparser.RawConfigParser()
        config.add_section('pattern:*')
        config.set('pattern:*', 'expect_license_header', 'Foo 1.0')
        config.set('pattern:*', 'custom_license_header_path', 'hello/world.txt')
        config.set('pattern:*', 'start_comment', '/*')
        config.set('pattern:*', 'end_comment', '*/')

        section = PatternSection.parse(context, 'pattern:*', config['pattern:*'])

        self.assertEquals(context.load_license_header.return_value,
                          section.expect_license_header)
        self.assertEquals(context.load_license_header_path.return_value,
                          section.custom_license_header_path)
        self.assertEquals('/*', section.start_comment)
        self.assertEquals('*/', section.end_comment)

    def test_parse_lines(self):
        m1 = parse_lines('0,1,2')
        m2 = parse_lines('0,2-10')

        self.assertTrue(m1(0))
        self.assertFalse(m1(3))

        self.assertTrue(m2(0))
        self.assertFalse(m2(1))
        self.assertTrue(m2(2))
        self.assertTrue(m2(10))
        self.assertFalse(m2(11))
