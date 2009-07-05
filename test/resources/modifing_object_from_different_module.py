'''
    file to test whether an object(list) is shared through different namespaces

    test/sharing_namespace_test.py imports this file, 
    and this file modifies a list in different module, 
    expecting the change to last.
'''

# not methods but actually just procedures
def modify_from_caller_module():
    file = 'sharing_namespace_test.py'
    strip_ext = lambda x: x.split('.', 2)[0]
    module = __import__(strip_ext(file))
    
    module.value.append(2)



def modify_from_different_module():
    file = 'shared_module.py'
    
    strip_ext = lambda x: x.split('.', 2)[0]
    module = __import__(strip_ext(file))
    
    module.value.append(2)


