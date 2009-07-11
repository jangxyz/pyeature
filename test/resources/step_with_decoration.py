import pyeature, re

@pyeature.given("I have some text \"123\"")
#@pyeature.given(re.compile("I have some text \"[0-9]\+\""))
def different_name():
    self.text = "123"

@pyeature.given(re.compile("some another text \"([0-9]+)\""))
def another_given():
    self.another_text = args[1]

@pyeature.when('another text for additional when')
def some_method_for_when():
    print '1'
    pass

@pyeature.then('something happens')
def then_also_can_register_with_method_name():
    pass

