#!/usr/bin/python
# coding: utf-8

import re, types, sys, traceback, os

##
## Keyword definitions
##
FEATURE  = 'Feature'
SCENARIO = 'Scenario'

# These are called clauses. 'And' is an additional clause that continues the previous clause
GIVEN, WHEN, THEN = 'Given', 'When', 'Then'
AND = 'And'

CLAUSE_NAMES     = [GIVEN, WHEN, THEN]
ALL_CLAUSE_NAMES = [GIVEN, WHEN, THEN, AND]
EVERY_KEYWORDS = [FEATURE, SCENARIO, AND] + CLAUSE_NAMES
##
##

class Patterns:
    """ patterns used to parse sentence of feature file """
    template = r'^\s*\b(%s)\b'
    feature  = re.compile(template % FEATURE,  re.IGNORECASE)
    scenario = re.compile(template % SCENARIO, re.IGNORECASE)
    all_clauses = re.compile(template % '|'.join(ALL_CLAUSE_NAMES), re.IGNORECASE)
    every_keywords = re.compile(template % '|'.join(EVERY_KEYWORDS), re.IGNORECASE)
    clauses    = re.compile(template % '|'.join(CLAUSE_NAMES), re.IGNORECASE)
    and_clause = re.compile(template % AND, re.IGNORECASE)


def extract(text):
    """ extracts a list of clauses from given text """
    extracts = [line.rstrip("\n") for line in text.split("\n")]
    #extracts = filter(lambda line: Patterns.all_clauses.match(line), extracts)
    extracts = filter(lambda line: Patterns.every_keywords.match(line), extracts)
    return extracts

def extract_file(filename):
    """ same as extract(), but opens a given filename """
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
        return re.sub(r'\W+', '_', clause.lstrip()).lower()
    
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
        item = lambda x: vars(module)[x]
        #item_type = lambda x: type(vars(module)[x])
        methods = filter(lambda x: type(item(x)) == types.FunctionType, methods)

        # filter by clause names
        methods = filter(self.is_clause_method_name, methods)

        return [item(m) for m in methods]
        
    def is_clause_method_name(self, method_name):
        """ returns true if method name starts with given_, when_, or then_,
                      or if is before or after """
        if method_name in ["before", "after"]:
            return True 
        for c in CLAUSE_NAMES:
            if method_name.startswith( "%s_" % c.lower() ):
                return True
        else:
            return False


class Runner:
    @staticmethod
    def is_feature(line):  return Patterns.feature.match(line) != None

    @staticmethod
    def is_scenario(line): return Patterns.scenario.match(line) != None


    def run_clauses(self, clauses, methods, output=sys.stdout):
        """ with clauses and set of method candidates, 
            run each clause in order and
            write result in output.
            Exceptions will not be raised, but just written to output """
        #print 'running clauses:', clauses
        #print 'with methods:', methods
    
        # run before method
        self.find_and_call_method('before', methods)
    
        matcher = Matcher()
        for i,clause in enumerate(clauses):
            output.write("\n" if i is not 0 else "")
    
            # skip 
            if Runner.is_feature(clause) or Runner.is_scenario(clause):
                self.report(clause, "skip", output)
                continue
    
            # find method
            method_name = matcher.clause2methodname(clause)
            clause_method = filter(lambda x: x.__name__ == method_name, methods)
    
            # stop if no method found
            if len(clause_method) == 0:
                self.report(clause, "stop", output)
                break
    
            # run method
            success = self.run_method(clause_method[0], clause, output)
            if not success:
                break
    
        # skip remaining methods after stop or fail
        output.write("\n" if i is not 0 else "")
        for rest_clause in clauses[i+1:]:
            self.report(rest_clause+"\n", "skip", output)
        output.write("\n")
    
        # run after method
        self.find_and_call_method('after', methods)


    def report(self, content, status, output):
        # skip stop fail sucess
        status_key = {
            "skip": '-',
            "stop": "X",
            "fail": "F",
            "success": ".",
        }
        try:
            output.write("("+ status_key[status] +") ")
        except KeyError:
            pass

        output.write(content)
        if status == "fail":
            output.write("\n")
            output.write('-'*60 + "\n")
            traceback.print_exc(file=output)
            output.write('-'*60)


    def run_method(self, method, clause, output):
        """ run a clause with method given, and report result to output """
        try:
            method()
        except:
            self.report(clause, "fail", output)
            return False
        else:
            self.report(clause, "success", output)
            return True


    def find_and_call_method(self, name, methods):
        for m in methods:
            if m.__name__ == name:
                m()
                return True
        return False


def load_step(filename):
    """ load methods from step definition file """
    sys.path.append(os.path.dirname(filename))

    filename_part = os.path.basename(filename).rsplit('.', 2)[0]
    module = __import__(filename_part)

    sys.path.pop()
    return module


def run(feature_file, step_file, output=sys.stdout):
    """ default method for pyeature: run given feature file with given step file """
    # load clauses from feature and methods from step definition
    clauses = extract(open(feature_file).read())
    module = load_step(step_file)
    clause_methods = Matcher().clause_methods_of(module)

    # run clauses
    Runner().run_clauses(clauses, clause_methods, output)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        prog_name = sys.argv[0].rsplit(os.sep, 2)[-1]
        sys.exit("""You must tell me the feature file and step definition file.

    Usage: %s some.feature some_step.py
        """ % prog_name)

    # run
    run(sys.argv[1], sys.argv[2])
    

