import sys, os
HOMEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir))
FILEDIR = os.path.abspath(os.path.dirname(__file__))
RESOURCEDIR = os.path.join(os.path.dirname(__file__), 'resources')
sys.path += [HOMEDIR, FILEDIR, RESOURCEDIR]
import unittest

value = [1]

class NamespaceSharingTestCase(unittest.TestCase):

    def test_modifing_object_in_this_file_from_different_module_does_not_change(self):
        import modifing_object_from_different_module
        modifing_object_from_different_module.modify_from_different_module()

        assert value == [1]


    def test_modifing_object_in_another_file_from_different_module_changes(self):
        import shared_module
        assert shared_module.value == [1]

        import modifing_object_from_different_module
        modifing_object_from_different_module.modify_from_different_module()

        assert shared_module.value == [1,2]


if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)

