from __future__ import with_statement; from contextlib import contextmanager
import sys, os
sys.path.append(os.getcwd())

import calculator

def before():
    #global calc
    self.calc = calculator.Calculator()

def given_i_have_entered_50_into_the_calculator():
    #global calc
    self.calc.append(50)

def given_i_have_entered_70_into_the_calculator():
    #global calc
    self.calc.append(70)

def when_i_press_add():
    #global calc, result
    self.result = self.calc.add()

def then_the_result_should_be_120_on_the_screen():
    #global result
    assert self.result == 1200

def then_xxthe_result_should_be_a_number():
    #global result
    assert type(self.result) is int

