#!/usr/bin/python
# coding: utf-8
import sys, os
HOMEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILEDIR = os.path.abspath(os.path.dirname(__file__))
RESOURCEDIR = os.path.join(os.path.dirname(__file__), 'resources')
sys.path += [HOMEDIR, FILEDIR, RESOURCEDIR]

import unittest
import pyeature
import types

class NotImplemented(Exception): pass
def pending(method):
    method_name = method.__class__.__name__
    if '_testMethodName' in dir(method):
        method_name += method.__class__.__name__
    else:
        method_name += method._TestCase__testMethodName
    raise NotImplemented("implement [%s]!" % method_name)


class LoaderTestCase(unittest.TestCase):
    def setUp(self):    pyeature.Loader.loaded_clauses = {}
    def tearDown(self): pyeature.Loader.loaded_clauses = {}

class BasicLoadTestCase(LoaderTestCase):
    ''' 모듈 로딩 '''
    def setUp(self):
        LoaderTestCase.setUp(self)
        self.step_filename = os.path.join(FILEDIR, 'sample_step.py')

    def test_load_methods_from_module(self):
        ''' [로딩] 모듈로부터 메소드를 로드한다 '''
        methods = pyeature.Loader().load_steps(self.step_filename)
        for m in methods.values():
            assert isinstance(m, types.FunctionType)


    def test_loaded_methods_saved_somewhere(self):
        ''' [로딩] 모듈에서 읽어들인 clause 메소드는 따로 저장된다 '''
        methods = pyeature.Loader().load_steps(self.step_filename)
        assert methods == pyeature.Loader.loaded_clauses


class LoadStepWithSelfTestCase(LoaderTestCase):
    ''' 로드하는 step 파일 내부에서 self를 쓸 수 있다 '''
    def setUp(self):
        LoaderTestCase.setUp(self)
        # step file containing 'self.value = 3'
        self.step_filename = os.path.join(FILEDIR, 'step_with_self.py')

    def test_loaded_modules_have_self(self):
        ''' [로딩] 로드된 모듈은 self를 알고 있다 '''
        try:
            pyeature.Loader().load_steps(self.step_filename)
        except:
            assert False, "exception should not be raised"


    def test_loaded_modules_have_self_which_directs_to_global_world(self):
        ''' [로딩] 로드된 모듈의 self는 global world를 가리킨다 '''
        #loader = pyeature.Loader()
        #loader.load_steps(self.step_filename)
        #assert loader.global_world.value == 3
        pending(self)


class LoadDecoratedStepTestCase(LoaderTestCase):
    ''' 로드하는 step에서 decorator 쓸 수 있다 '''
    def setUp(self):
        LoaderTestCase.setUp(self)
        self.step_filename = os.path.join(FILEDIR, 'step_with_decoration.py')

    def test_recognizes_given_when_then_decorators(self):
        ''' [로드] @given, @when, @then decorator를 읽어들인다 '''
        clauses = pyeature.Loader().load_steps(self.step_filename)
        assert len(clauses) >= 3

    def test_adds_appropriate_prefix_for_decorated_methods(self):
        ''' [로드] 메소드 이름 앞에 given을 알릴 수 있는 접두사가 붙는다 '''
        clauses = pyeature.Loader().load_steps(self.step_filename)

        f = lambda name: pyeature.GIVEN in name and 'I have some text as given' in name
        assert filter(f, clauses.keys()) != []
        #assert 'I have some text as given' in clauses.keys()



if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)

