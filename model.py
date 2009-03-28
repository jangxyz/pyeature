#!/usr/bin/python
# coding: utf-8

import re

all_clause_p  = re.compile(r'^\s*\b(Given|When|Then|And)\b', re.IGNORECASE)
only_clause_p = re.compile(r'^\s*\b(Given|When|Then)\b', re.IGNORECASE)
and_p         = re.compile(r'^\s*\b(And)\b', re.IGNORECASE)

def given(regex_str):
    pass

def extract(text):
    extracts = [line.rstrip("\n") for line in text.split("\n")]
    extracts = filter(lambda line: all_clause_p.match(line), extracts)
    return extracts

def extract_file(filename):
    return extract(open(filename).read())


previous_clause_name = None
def clause2methodname(clause):
    global previous_clause_name
    clause_name = clause_name_of(clause)
    if clause_name:
        previous_clause_name = clause_name
    else:
        if previous_clause_name is None:
            return None 
        clause_name = previous_clause_name
        clause = and_p.sub(clause_name, clause)

    return re.sub(r' +', '_', clause).lower()

def clause_name_of(sentence):
    matched = only_clause_p.match(sentence)
    return matched.group() if matched else None

