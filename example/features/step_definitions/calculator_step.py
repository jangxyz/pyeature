import sys, os
sys.path.append(os.getcwd())
import pyeature

import re

import calculator

def before():
    self.calc = calculator.Calculator()


#given_clauses = {}
#
#def given(pattern):
#    """ matches pattern """
#    def worker(f):
#        """ register as a GIVEN step """
#        given_clauses[pattern] = f
#        return f
#
#    return worker

#def given_i_have_entered_50_into_the_calculator():
#    self.calc.append(50)

#@given(re.compile("I have entered \([0-9]\+\) into the calculator"))
@pyeature.given("I have entered 50 into the calculator")
def given_calc():
    #num = args[1]
    num = 50
    self.calc.append(num)


def given_i_have_entered_70_into_the_calculator():
    self.calc.append(70)

def when_i_press_add():
    self.result = self.calc.add()

def then_the_result_should_be_120_on_the_screen():
    assert self.result == 1200

def then_xxthe_result_should_be_a_number():
    assert type(self.result) is int

