'''
    file to test whether an object(list) is shared through different namespaces

    test/sharing_namespace_test.py and 
    resource/modifing_object_from_different_module imports this module,
    where the latter tries to modify a list,
    expecting it will last.
'''

value = [1]
