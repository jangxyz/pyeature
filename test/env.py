import sys, os
HOMEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILEDIR = os.path.abspath(os.path.dirname(__file__))
RESOURCEDIR = os.path.join(os.path.dirname(__file__), 'resources')
sys.path += [HOMEDIR, FILEDIR, RESOURCEDIR]

import unittest, types
import pyeature

class NotImplemented(Exception): pass
def pending(method):
    method_name = method.__class__.__name__
    if '_testMethodName' in dir(method):
        method_name += method.__class__.__name__
    else:
        method_name += method._TestCase__testMethodName
    raise NotImplemented("implement [%s]!" % method_name)

class LoaderTestCase(unittest.TestCase):
    def setUp(self):    
        pyeature.Loader.loaded_clauses = {}
        pyeature.Loader.global_world = pyeature.World()
    def tearDown(self): 
        pyeature.Loader.loaded_clauses = {}


def run_test(prefix='test'):
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = prefix
        unittest.main(testLoader = loader)

