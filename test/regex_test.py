#!/usr/bin/python
# coding: utf-8

from env import *
import unittest, pyeature

step_filename = os.path.join(FILEDIR, 'step_with_decoration.py')

class RegexTestCase(LoaderTestCase):
    def test_accepts_regex_as_key_for_clause(self):
        ''' [로드] 메소드 이름에 해당하는 정규표현식을 받을 수도 있다 '''
        methods = pyeature.Loader().load_steps(step_filename)

        f = lambda name: not isinstance(name, types.StringType)
        leftovers = filter(f, methods.keys())
        assert leftovers != []

    def test_finds_clause_with_regex(self):
        ''' [매칭] 정규표현식으로 clause를 찾을 수 있다 '''
        methods = pyeature.Loader().load_steps(step_filename)
        clause = 'And some another text "123"'
        method = pyeature.Matcher(methods).find_method_by_clause(clause)
        assert method.__name__ == 'another_given'

    def test_matched_group_is_recognized_as_args(self):
        ''' 매치된 그룹은 args로 인식된다 '''
        methods = pyeature.Loader().load_steps(step_filename)
        clause = 'And some another text "123"'
        method = pyeature.Matcher(methods).find_method_by_clause(clause)
        method()
        assert pyeature.Loader.global_world.another_text == "123"


if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)

