#!/usr/bin/python
# coding: utf-8

import sys, os
HOMEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILEDIR = os.path.dirname(__file__)
sys.path += [HOMEDIR, FILEDIR]

import unittest
import pyeature


class ExtractingClausesTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(FILEDIR, 'sample.feature')
        self.text = open(self.filename).read()

    def test_extracting_clauses_from_string(self):
        extracts = pyeature.extract(self.text)
        assert len(extracts) == 6
    def test_extracting_clauses_from_a_feature_file(self):
        extracts = pyeature.extract_file(self.filename) 
        assert len(extracts) == 6

    def test_extracting_clauses_that_starts_with_given_when_and_then(self):
        self.text += """Some other words
            And another word
        Tada"""
        extracts = pyeature.extract(self.text)
        assert len(extracts) == 7

    def test_extracts_every_keywords(self):
        self.text = """Feature: some feature

        Scenario: some scenario

        %s """ % self.text
        extracts = pyeature.extract(self.text) 
        assert len(extracts) == 8


class ExtractingScenariosTestCase(unittest.TestCase):
    pass


class ConvertingStringIntoMethodNameTestCase(unittest.TestCase):
    def setUp(self):
        self.clauses = ['Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then	some sp3c!al,, characters?!',
                        'And  another then',
                        ]
        self.matcher = pyeature.Matcher()

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
        

class MatchingClausesWithStepDefinitionsTestCase(unittest.TestCase):
    def setUp(self):
        step_filename = 'sample_step.py'
        self.module = __import__(step_filename.rsplit('.', 2)[0])
        self.clauses = [
                        'Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then	some sp3c!al,, characters?!',
                        'And  another then',
                        ]
        self.matcher = pyeature.Matcher()

    def test_finding_clause_methods_from_module(self):
        methods = self.matcher.clause_methods_of(self.module)
        clause_method_names = [m.__name__ for m in methods]

        for method_name in [
         'given_i_have_some_text_as_given',
         'when_another_text_for_additional_when', 
        ]:
            assert method_name in clause_method_names

    def test_before_and_after_methods(self):
        methods = self.matcher.clause_methods_of(self.module)
        clause_method_names = [m.__name__ for m in methods]

        assert "before" in clause_method_names
        assert "after" in clause_method_names

class RunFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.sample_filename = os.path.join(FILEDIR, 'sample.feature')
        self.clauses = [
                        'Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then some result',
                        'And  another then',
                       ]

        self.step_filename = 'sample_step.py'
        module = __import__(self.step_filename.rsplit('.', 2)[0])
        self.clause_methods = pyeature.Matcher().clause_methods_of(module)
        
        from StringIO import StringIO
        self.output = StringIO()

    def tearDown(self):
        self.output.close()

    def test_running_clauses(self):
        pyeature.run_clauses(self.clauses, self.clause_methods, self.output)

        for clause in self.clauses:
            assert clause in self.output.getvalue()

    def append_clause_method(self, method, name, clause_methods):
        method.func_name = name
        clause_methods.append( method )

    def test_running_clauses_making_exception_does_not_raise_exception(self):
        self.append_clause_method(lambda: y, 'given_another_text_for_additional_given', self.clause_methods)

        pyeature.run_clauses(self.clauses, self.clause_methods, self.output)

        assert "Traceback (most recent call last):" in self.output.getvalue()

    def test_that_multiple__exceptions_skip_rest_at_first_occurence(self):
        self.append_clause_method(lambda: y, 'given_another_text_for_additional_given', self.clause_methods)
        self.append_clause_method(lambda: y, 'when_i_write_when', self.clause_methods)
        
        pyeature.run_clauses(self.clauses, self.clause_methods, self.output)

        assert self.output.getvalue().count('Traceback (most recent call last):') == 1

    def test_non_successive_clause_method_should_not_run(self):
        self.append_clause_method(lambda: y, 'then_another_then', self.clause_methods)

        pyeature.run_clauses(self.clauses, self.clause_methods, self.output)

        assert "Traceback (most recent call last):" not in self.output.getvalue()

    def test_that_running_before_methods_should_raise_exception_when_wrong(self):
        clause_methods = []
        self.append_clause_method(lambda: y, 'before', clause_methods)
        self.assertRaises(NameError, pyeature.run_clauses, self.clauses, clause_methods, self.output)

    def test_running_after_methods_should_raise_exception_when_wrong(self):
        clause_methods = []
        self.append_clause_method(lambda: y, 'after', clause_methods)
        self.assertRaises(NameError, pyeature.run_clauses, self.clauses, clause_methods, self.output)

    def test_run(self):
        pyeature.run(self.sample_filename, self.step_filename, self.output)


if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)

