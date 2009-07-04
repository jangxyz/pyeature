print '\nglobals:', globals().keys()
print 'locals:',  locals().keys()
import pyeature

@pyeature.given("I have some text as given")
def different_name():
    pass

def when_another_text_for_additional_when():
    print '1'
    pass

