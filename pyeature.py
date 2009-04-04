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

class World: 
    pass
global_world = World()


class Patterns:
    """ patterns used to parse sentence of feature file """
    template = r'^\s*\b(%s)\b'
    feature  = re.compile(template % FEATURE,  re.IGNORECASE)
    scenario = re.compile(template % SCENARIO, re.IGNORECASE)
    all_clauses = re.compile(template % '|'.join(ALL_CLAUSE_NAMES), re.IGNORECASE)
    every_keywords = re.compile(template % '|'.join(EVERY_KEYWORDS), re.IGNORECASE)
    clauses    = re.compile(template % '|'.join(CLAUSE_NAMES), re.IGNORECASE)
    and_clause = re.compile(template % AND, re.IGNORECASE)


class Loader:
    """ loads methods from step definitions """
    @staticmethod
    def load_step(filename):
        """ load methods from step definition file 
        also supports directory name """
        # add directory to sys path
        full_filename = os.path.abspath(filename)
        directory = full_filename if os.path.isdir(full_filename) else os.path.dirname(full_filename)
        sys.path.append(directory)
    
        # find module names, either from filename or directory
        filename_part = lambda x: os.path.basename(x).rsplit('.', 1)[0]
        if os.path.isdir(full_filename):
            filename_parts = map(filename_part, os.listdir(full_filename))
        else:
            filename_parts = [filename_part(full_filename)]
    
        # import every possible modules you can
        modules = []
        for filename_part in filename_parts:
            try:
                new_module = __import__(filename_part)
                new_module.self = global_world
                modules.append( new_module )
            except SyntaxError, e:
                pass
            except ImportError, e:
                pass
            except ValueError, e:
                pass
    
        # remove last added sys path directory
        sys.path.pop()
    
        return modules



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


    def clause_methods_of(self, modules):
        """ return list of clause methods from given modules """
        modules = [modules] if not isinstance(modules, types.ListType) else modules

        # search each modules for functions
        methods = []
        for module in modules:
            name2item   = lambda x: vars(module)[x]
            new_methods = [name2item(x) for x in dir(module)]
            # filter functions from module
            new_methods = filter(lambda x: type(x) == types.FunctionType, new_methods)
            methods.extend(new_methods)

        # filter by clause names
        #methods = filter(self.is_clause_method_name, methods)
        methods = filter(lambda x: self.is_clause_method_name(x.__name__), methods)
        #methods = filter(self.is_clause_method_name, [m.__name__ for m in methods])

        #return [item(m) for m in methods]
        return methods
        
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
        # run before method
        self.find_and_call_method('before', methods)
    
        success_count = 0
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
            success_count += 1
    
        # skip remaining methods after stop or fail
        output.write("\n" if i is not 0 else "")
        for rest_clause in clauses[i+1:]:
            self.report(rest_clause+"\n", "skip", output)
        output.write("\n")
    
        # run after method
        self.find_and_call_method('after', methods)

        return success_count


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



def run(feature_file, step_file, output=sys.stdout):
    """ default method for pyeature: run given feature file with given step file(or directory)
    
    returns number of successful steps ran
    """
    # load clauses from feature and methods from step definition
    clauses = extract(open(feature_file).read())
    modules = Loader.load_step(step_file)
    clause_methods = Matcher().clause_methods_of(modules)

    # run clauses
    return Runner().run_clauses(clauses, clause_methods, output)


if __name__ == '__main__':
    try:
        feature_file = sys.argv[1]
        if len(sys.argv) >= 3:
            step_definition_directory = sys.argv[2]
        else:
            dirname = os.path.dirname(os.path.abspath(feature_file))
            step_definition_directory = os.path.join( dirname, 'step_definitions' )
            if not os.path.isdir(step_definition_directory):
                raise Exception
    except:
        prog_name = sys.argv[0].rsplit(os.sep, 1)[-1]
        sys.exit("""You must tell me the feature file and step definition file.

    Usage: %s some.feature some_step.py
        """ % prog_name)

    # run
    run(sys.argv[1], step_definition_directory)


