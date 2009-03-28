#!/usr/bin/python
# coding: utf-8

import re, types

FEATURE = 'Feature'
SCENARIO = 'Scenario'
GIVEN, WHEN, THEN = 'Given', 'When', 'Then'
AND = 'And'
CLAUSE_NAMES     = [GIVEN, WHEN, THEN]
#ALL_CLAUSE_NAMES = [GIVEN, WHEN, THEN, AND]
EVERY_KEYWORDS = [FEATURE, SCENARIO, AND] + CLAUSE_NAMES

class Patterns:
    template = r'^\s*\b(%s)\b'
    feature  = re.compile(template % FEATURE,  re.IGNORECASE)
    scenario = re.compile(template % SCENARIO, re.IGNORECASE)
    #all_clauses = re.compile(template % '|'.join(ALL_CLAUSE_NAMES), re.IGNORECASE)
    every_keywords = re.compile(template % '|'.join(EVERY_KEYWORDS), re.IGNORECASE)
    clauses    = re.compile(template % '|'.join(CLAUSE_NAMES), re.IGNORECASE)
    and_clause = re.compile(template % AND, re.IGNORECASE)


def extract(text):
    extracts = [line.rstrip("\n") for line in text.split("\n")]
    #extracts = filter(lambda line: Patterns.all_clauses.match(line), extracts)
    extracts = filter(lambda line: Patterns.every_keywords.match(line), extracts)
    return extracts

    #extracted_d = {}
    #last_feature, last_scenario = None, None
    #for line in extracts:
    #    if is_feature(line):
    #        last_feature = line
    #        extracted_d[last_feature] = {}
    #    elif is_scenario(line):
    #        last_scenario = line
    #        extracted_d[last_feature][last_scenario] = []
    #    else:
    #        extracted_d[last_feature][last_scenario].append( line )

    #return extracted_d

def is_feature(line):  return Patterns.feature.match(line) != None
def is_scenario(line): return Patterns.scenario.match(line) != None


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
    
        clause = Patterns.and_clause.sub(clause_name, clause)
        return re.sub(r'\W+', '_', clause).lower()
    
    def clause_name_of(self, sentence):
        """  return clause name of sentence, if it is a clause
                Given|When|Then => itself
                And             => previous clause name
                anything else   => None
        """
        matched = Patterns.clauses.match(sentence)
        if matched: 
            # store as previous clause name when Given|When|Then
            self.previous_clause_name = matched.group()
        elif not Patterns.and_clause.match(sentence):
            # None if it isn't And clause
            return None
        return self.previous_clause_name


    def clause_methods_of(self, module):
        """ return list of clause methods """
        methods = dir(module)

        # filter functions
        item_type = lambda x: type(vars(module)[x])
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

    #def methods_to_implement(self, module, clauses):
    #    """ given a module and a list of clauses,
    #        find out which clauses is missing an implementation
    #        and return list of methods for such clauses """

    #    every_methods = filter(None, [self.clause2methodname(c) for c in clauses])
    #    existing_methods = self.clause_methods_of(module)

    #    not_implemented_methods = every_methods[:]
    #    for existing_m in existing_methods:
    #        if existing_m in every_methods:
    #            not_implemented_methods.remove(existing_m)
    #    return not_implemented_methods


