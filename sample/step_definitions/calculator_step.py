import sys, os
sys.path.append(os.getcwd())

import calculator

def before():
    global calc
    calc = calculator.Calculator()

def given_i_have_entered_50_into_the_calculator():
    global calc
    calc.append(50)

def given_i_have_entered_70_into_the_calculator():
    global calc
    calc.append(70)

def when_i_press_add():
    global calc, result
    result = calc.add()

def then_the_result_should_be_120_on_the_screen():
    global result
    assert result == 1200

def then_the_result_should_be_a_number():
    global result
    assert type(result) is int

