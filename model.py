#!/usr/bin/python
# coding: utf-8

import re, types

GIVEN, WHEN, THEN = 'Given', 'When', 'Then'
AND = 'And'
CLAUSE_NAMES     = [GIVEN, WHEN, THEN]
ALL_CLAUSE_NAMES = [GIVEN, WHEN, THEN, AND]

class ClausePatterns:
    template = r'^\s*\b(%s)\b'
    all_clauses = re.compile(template % '|'.join(ALL_CLAUSE_NAMES), re.IGNORECASE)
    clauses     = re.compile(template % '|'.join(CLAUSE_NAMES),     re.IGNORECASE)
    and_c       = re.compile(template % AND, re.IGNORECASE)

def given(regex_str):
    pass

def extract(text):
    extracts = [line.rstrip("\n") for line in text.split("\n")]
    extracts = filter(lambda line: ClausePatterns.all_clauses.match(line), extracts)
    return extracts

def extract_file(filename):
    return extract(open(filename).read())

class Matcher:
    """ match each sentence with clauses """
    def __init__(self):
        self.previous_clause_name = None

    def clause2methodname(self, clause):
        """ convert a clause sentence into a method name
                - ' Given some pre-condition' => 'given_some_pre_condition'
                - 'And another given' => 'given_another_given' (checking previous)
                - 'Then I have then	some sp3c!al,, characters?!'
                    => 'then_i_have_then_some_sp3c_al_characters_'
        """
        clause_name = self.clause_name_of(clause)
        if not clause_name:
            return None
    
        clause = ClausePatterns.and_c.sub(clause_name, clause)
        return re.sub(r'\W+', '_', clause).lower()
    
    def clause_name_of(self, sentence):
        """  return clause name of sentence, if it is a clause
                Given|When|Then => itself
                And             => previous clause name
                anything else   => None
        """
        matched = ClausePatterns.clauses.match(sentence)
        if matched: 
            # store as previous clause name when Given|When|Then
            self.previous_clause_name = matched.group()
        elif not ClausePatterns.and_c.match(sentence):
            # None if it isn't And clause
            return None
        return self.previous_clause_name


    def clause_methods_of(self, namespace):
        """ return list of clause methods """
        methods = dir(namespace)

        # filter functions
        item_type = lambda x: type(vars(namespace)[x])
        methods = filter(lambda x: item_type(x) == types.FunctionType, methods)

        # filter by clause names
        methods = filter(self.has_clause_prefix, methods)

        return methods
        
    def has_clause_prefix(self, method_name):
        """ returns true if method name starts with given_, when_, or then_ """
        for c in CLAUSE_NAMES:
            if method_name.startswith( "%s_" % c.lower() ):
                return True
        else:
            return False

