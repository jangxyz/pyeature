#!/usr/bin/env python
# 
# This script is based on the one found at http://vim.wikia.com/wiki/VimTip280
# but has been generalised. It searches the current working directory for
# t_*.py or test_*.py files and runs each of the unit-tests found within.
#
# When run from within Vim as its 'makeprg' with the correct 'errorformat' set,
# any failure will deliver your cursor to the first line that breaks the unit
# tests.
#
# Place this file somewhere where it can be run, such as ${HOME}/bin/alltests.py
# 

import unittest, sys, os, re


def find_all_test_files():
    """ finds files that end with '_test.py', recursively """
    #test_file_pattern = re.compile('^t(est)?_.*\.py$')
    test_file_pattern = re.compile('.*_test\.py$')
    is_test_file = lambda filename: test_file_pattern.match(filename)
    drop_dot_py = lambda filename: filename[:-3]
    join_module = lambda *names: '/'.join(names)

    modules = []
    for root, dirs, files in os.walk(os.curdir):
        root_name = os.path.split(root)[-1]
        for test_file in filter(is_test_file, files):
            module = join_module(root_name, drop_dot_py(test_file))
            modules.append(module)
        #modules += ['.'.join([root_name, drop_dot_py(test_file)]) for test_file in filter(is_test, files)]
    return modules


def suite():
    modules_to_test = find_all_test_files()
    print 'Testing', ', '.join(modules_to_test)

    # add to path
    paths = list(set(map(lambda x: x.rsplit("/", 2)[0], modules_to_test)))
    sys.path += map(lambda p: os.path.abspath(p), paths)

    loader = unittest.TestLoader()
    alltests = unittest.TestSuite()
    #for module in map(__import__, modules_to_test):
    #    alltests.addTest(unittest.findTestCases(module))
    alltests.addTests(loader.loadTestsFromNames(modules_to_test))

    return alltests

if __name__ == '__main__':
    try:
        import testoob
        testoob.main(defaultTest='suite')
    except ImportError:
        unittest.main(defaultTest='suite')


