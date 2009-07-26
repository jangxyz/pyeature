#!/usr/bin/python
# coding: utf-8

from env import *
import unittest, pyeature
from argument_test import ArgumentParserTestCase

ko_text = """
    기능: 새 기능

    시나리오: 이런 시나리오가 있습니다

    처음에 조건1이 있고
    그리고 조건2가 있을 때

    만약 내가 어떤 행동1을 하고

    그러면 결과1이 나타나고
    그리고 결과2이 나타나고
    그리고 결과3도 나타난다.
"""

class KeywordDictionaryTestCase(ArgumentParserTestCase):
    def setUp(self):
        ArgumentParserTestCase.setUp(self)


    def test_receiving_keyword_dictionary(self):
        en_keyword_dict = {
            'feature': 'Feature',
            'scenario': 'Scenario',
            'given': 'Given',
            'when': 'When',
            'then': 'Then',
            'and': 'And',
        }

        en_text = """
            Feature: a new feature

            Scenario: testing scenario

            Given precondition1
            And precondition2

            When I do some action

            Then I get some result1
            And another result2
            And another result3
        """

        clauses = pyeature.extract(en_text, en_keyword_dict)
        assert len(clauses) is 8

    def test_setting_up_keywords(self):
        ko_keyword_dict = {
            'feature': '기능',
            'scenario': '시나리오',
            'given': '처음에',
            'when': '만약',
            'then': '그러면',
            'and': '그리고',
        }

        clauses = pyeature.extract(ko_text, ko_keyword_dict)
        assert len(clauses) is 8


    def test_language_option_loads_proper_keyword_dictionary(self):
        # FIXME: should test that keyword_dictionary is being used under the hood
        feature,step,options = pyeature.parse_args(['-l', 'ko'] + self.default_args)
        clauses = pyeature.extract(ko_text, pyeature.lang[options.lang])
        assert len(clauses) is 8



if __name__ == '__main__':
    run_test('test')


