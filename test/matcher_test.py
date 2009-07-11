#!/usr/bin/python
# coding: utf-8

from env import *
import unittest, pyeature

class MatchingClausesWithStepDefinitionsTestCase(LoaderTestCase):
    ''' 모듈의 메소드와 clause를 매칭한다 '''
    def setUp(self):
        LoaderTestCase.setUp(self)
        self.step_filename = 'sample_step.py'
        self.module = __import__(self.step_filename.rsplit('.', 2)[0])
        self.clauses = [
                        'Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then	some sp3c!al,, characters?!',
                        'And  another then',
                        ]
        self.matcher = pyeature.Matcher

    def test_finding_clause_methods_from_module(self):
        ''' [매칭] 모듈에서 적합한 clause 메소드를 찾는다 '''
        #methods = self.matcher.clause_methods_of(self.module)
        methods = pyeature.Loader().load_steps(self.step_filename)

        for method in methods.values():
            assert isinstance(method, types.FunctionType)

        clause_method_names = methods.keys()
        for method_name in [
         'given_i_have_some_text_as_given',
         'when_another_text_for_additional_when', 
        ]:
            assert method_name in clause_method_names

    def test_loaded_methods_saved_somewhere(self):
        ''' [매칭] 모듈에서 읽어들인 clause 메소드는 따로 저장된다 '''
        #methods = self.matcher.clause_methods_of(self.module)
        methods = pyeature.Loader().load_steps(self.step_filename)

        loaded_clause_methods = pyeature.Loader.loaded_clauses
        assert methods == loaded_clause_methods

    def test_finding_clause_methods_from_list_of_modules(self):
        ''' [매칭] 모듈 리스트에서 적합한 clause 메소드를 찾는다 '''
        #methods_from_a_module = self.matcher.clause_methods_of(self.module)
        methods_from_a_module = pyeature.Loader().load_steps(self.step_filename)

        modules = [self.module, __import__('another_sample_step')]
        methods_from_modules = self.matcher.clause_methods_of(modules)

        assert len(methods_from_a_module) < len(methods_from_modules)
        for m in methods_from_a_module.values():
            assert m in methods_from_modules

    def test_before_and_after_methods(self):
        ''' [매칭] before, after hook 메소드도 인식한다 '''
        method_names = pyeature.Loader().load_steps(self.step_filename).keys()

        assert "after" in method_names


    def test_finding_before_hook_from_another_module(self):
        ''' [매칭] 다른 모듈에서 before를 찾는다 '''
        #methods_from_a_module = self.matcher.clause_methods_of(self.module)
        methods_from_a_module = pyeature.Loader().load_steps(self.step_filename)

        modules = [self.module, __import__('hook')]
        methods = self.matcher.clause_methods_of(modules)
        clause_method_names = [m.__name__ for m in methods]

        assert "before" in clause_method_names
        assert "after" in clause_method_names




if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)



