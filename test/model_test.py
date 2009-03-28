#!/usr/bin/python
# coding: utf-8

import sys, os
HOMEDIR=os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
sys.path.append(HOMEDIR)

import unittest
import model

class GivenTestCase(unittest.TestCase):
    def test_there_is_a_method_given(self):
        model.given("something")

class ExtractFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = 'sample.feature'
        self.text = open(self.filename).read()

    def test_extracting_clauses_from_a_feature_file(self):
        extracts = model.extract_file(self.filename) 
        assert len(extracts) == 6

    def test_extracting_clauses_from_string(self):
        extracts = model.extract(self.text)
        assert len(extracts) == 6

    def test_extracting_clauses_that_starts_with_given_when_and_then(self):
        self.text += """Some other words
            And another word
        Tada"""
        extracts = model.extract(self.text)
        assert len(extracts) == 7

class MatchingClausesWithStepDefinitionsTestCase(unittest.TestCase):
    def setUp(self):
        step_filename = 'sample_step.py'
        import os
        self.sample_step_namespace = __import__(step_filename.rsplit(os.extsep, 2)[0])
        self.clauses = ['Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then	some sp3c!al,, characters?!',
                        'And  another then',
                        ]
        self.matcher = model.Matcher()

    def test_find_clause_methods(self):
        methods = self.matcher.clause_methods_of(self.sample_step_namespace)
        assert sorted(methods) == ['given_another_text_for_additional_when', 
                                   'given_i_have_some_text_as_given']

class ConvertingStringIntoMethodNameTestCase(unittest.TestCase):
    def setUp(self):
        self.clauses = ['Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then	some sp3c!al,, characters?!',
                        'And  another then',
                        ]
        self.matcher = model.Matcher()

    def test_that_continuous_spaces_are_turned_into_an_underscores(self):
        methodname = self.matcher.clause2methodname(self.clauses[0])
        assert ' ' not in methodname
        assert '_' in methodname
        assert methodname.count('_') == 6

    def test_that_uppercase_turned_into_lowercase(self):
        methodname = self.matcher.clause2methodname(self.clauses[0])
        assert 'I' not in methodname
        assert 'G' not in methodname
        assert 'i' in methodname
        assert 'g' in methodname

    def test_that_and_becomes_previous_clause_name(self):
        converted = [self.matcher.clause2methodname(c) for c in self.clauses]
        assert converted[1].startswith('given_')
        assert converted[3].startswith('when_')
        assert converted[5].startswith('then_')

    def test_that_non_alphanumeric_characters_change_into_underscore(self):
        methodname = self.matcher.clause2methodname(self.clauses[4])
        assert methodname == 'then_i_have_then_some_sp3c_al_characters_'

    def test_converting_clause_sentence_to_method_name(self):
        converted = [self.matcher.clause2methodname(c) for c in self.clauses]
        assert converted == ['given_i_have_some_text_as_given',
                             'given_another_text_for_additional_given',
                             'when_i_write_when',
                             'when_another_text_for_additional_when',
                             'then_i_have_then_some_sp3c_al_characters_',
                             'then_another_then'
                            ]
        


if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)


