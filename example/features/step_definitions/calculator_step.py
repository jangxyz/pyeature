import sys, os
sys.path.append(os.getcwd())
import pyeature

import re

import calculator

def before():
    self.calc = calculator.Calculator()


@pyeature.given(re.compile("I have entered ([0-9]+) into the calculator"))
def enter_number():
    num = args[1]
    self.calc.append(int(num))

def when_i_press_add():
    self.result = self.calc.add()

@pyeature.then("the result should be 120 on the screen")
#def then_the_result_should_be_120_on_the_screen():
def check_result():
    assert self.result == 1200

def then_xxthe_result_should_be_a_number():
    assert type(self.result) is int

