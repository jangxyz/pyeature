# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.getcwd())
import pyeature

import re

import calculator

def before():
    self.calc = calculator.Calculator()

@pyeature.given(re.compile("계산기에 ([0-9]+)(을|를) 입력하"))
def enter_number():
    num = args[1]
    self.calc.append(int(num))

@pyeature.when("더하기를 누르면")
def when_i_press_add():
    self.result = self.calc.add()

@pyeature.then("화면에 답인 120이 나와야 하고")
#def then_the_result_should_be_120_on_the_screen():
def check_result():
    assert self.result == 1200

def then_xxthe_result_should_be_a_number():
    assert type(self.result) is int


