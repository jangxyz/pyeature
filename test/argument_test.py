#!/usr/bin/python
# coding: utf-8

from env import *
import unittest, pyeature

class ArgumentParserTestCase(unittest.TestCase):
    def setUp(self):
        self.feature_file = 'file.feature'
        self.step_definition_directory = 'resources/'
        self.default_args = [self.feature_file, self.step_definition_directory]

    def test_feature_file_and_step_definition_directory(self):
        feature_file, step_definition_directory, options = pyeature.parse_args(self.default_args)
        assert feature_file == self.feature_file
        assert step_definition_directory == self.step_definition_directory


class LanguageOptionTestCase(ArgumentParserTestCase):

    def test_default_language_is_en(self):
        a,b, options = pyeature.parse_args(self.default_args)
        assert options.lang == "en"

    def test_set_language_option_with_l(self):
        a,b, options = pyeature.parse_args(['-l', 'ko'] + self.default_args)
        assert options.lang == "ko"


if __name__ == '__main__':
    run_test()


