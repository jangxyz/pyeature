import pyeature

@pyeature.given("I have some text as given")
def different_name():
    pass

@pyeature.when('another text for additional when')
def some_method_for_when():
    print '1'
    pass

@pyeature.then('something happens')
def then_also_can_register_with_method_name():
    pass

