#!/usr/bin/python
# coding: utf-8

import re, types, sys, traceback, os
sys.path.append(os.getcwd())
import pyeature

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


def given(clause): return Loader.step_decoration(GIVEN, clause)
def when(clause):  return Loader.step_decoration(WHEN,  clause)
def then(clause):  return Loader.step_decoration(THEN,  clause)
    

def extract(text):
    """ extracts a list of clauses from given text """
    extracts = [line.rstrip("\n") for line in text.split("\n")]
    #extracts = filter(lambda line: Patterns.all_clauses.match(line), extracts)
    extracts = filter(lambda line: Patterns.every_keywords.match(line), extracts)
    return extracts

def extract_file(filename):
    """ same as extract(), but opens a given filename """
    return extract(open(filename).read())


class Helper:
    @staticmethod
    def directory_name(filename):
        """ returns directory of the filename(or directory, if that's what you give me) """
        full_filename = os.path.abspath(filename)
        if os.path.isdir(full_filename):
            return full_filename
        else:
            return os.path.dirname(full_filename)

    @staticmethod
    def error(msg):
        sys.stderr.write(msg+"\n")


class World:
    pass

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
    global_world = World()
    loaded_clauses = {}

    def load_steps(self, filename):
        """ load methods from step definition file (or directory) 
        
        it first finds module names from file or directory,
        imports the modules,
        returning the methods from it
        """
        sys.path.append(Helper.directory_name(filename))

        # find module names
        full_filename  = os.path.abspath(filename)
        filename_parts = self.find_module_names(full_filename)

        # import modules and methods from it
        modules = self.import_modules(filename_parts)
        clause_methods = Matcher.clause_methods_of(modules)

        for method in clause_methods:
            pyeature.Loader.loaded_clauses[method.__name__] = method

        sys.path.pop()

        return pyeature.Loader.loaded_clauses


    def import_modules(self, module_names):
        """ import every modules possible given their names (not files) """
        imported_modules = [self.try_importing_module(name) for name in module_names]
        imported_modules = filter(None, imported_modules)
        return imported_modules


    def try_importing_module(self, module_name):
        """ try importing a module, catching all exceptions """
        try:
            if module_name in sys.modules:
                new_module = __import__(module_name)
                new_module = reload(new_module)
            else:
                #print '- globals:', globals().keys()
                #print '- locals:',  locals().keys()
                new_module = __import__(module_name)

            new_module.self = self.global_world
            return new_module
        #except SyntaxError, e:
        #    Helper.error("%s:%s: %s" % (e.filename, e.lineno, e.msg))
        #    raise e
        except ImportError, e:
            Helper.error("%s: failed to load %s" % (str(e), module_name) )
        except ValueError, e:
            pass
    

    def find_module_names(self, full_filename):
        """ find module names, either from filename or directory """
        filename_part = lambda x: os.path.basename(x).rsplit('.', 1)[0]
        if os.path.isdir(full_filename):
            files = os.listdir(full_filename)
            files = filter(lambda x: x.endswith('.py') or x.endswith('.pyc'), files)
            names = map(filename_part, files)
        else:
            names = [filename_part(full_filename)]
        # uniq
        names = list(set(names))

        return names

    @staticmethod
    def step_decoration(step_name, clause):
        def working_method(method):
            #pyeature.Loader.loaded_clauses[step_name +" "+ clause] = method
            pyeature.Loader.loaded_clauses[clause] = method
            return method
        return working_method



class Matcher:
    re_type = type(re.compile(''))
    """ match each sentence with clauses """
    def __init__(self, clause_methods=[]):
        self.previous_clause_name = None
        self.clause_methods = clause_methods

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
        """  return clause name of sentence, if it is a clause (None if not)
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
            return
        return self.previous_clause_name


    def find_method_by_name(self, name, default=None):
        return self.clause_methods.get(name, default)


    def find_method_by_clause(self, clause):
        ''' find and return apropriate method for the given clause 
        
        try 
            1. clause itself in string
            2. converted method name of the clause in string
        from loaded clauses methods to match the given clause, or
            3. clause 
        '''
        clause = clause.strip()

        #for c in [clause, self.clause2methodname(clause)]:
        #    method = pyeature.Loader.loaded_clauses.get(c, None)
        #    if method:
        #        return method

        for method_key,method in pyeature.Loader.loaded_clauses.iteritems():
            if isinstance(method_key, types.StringType):
                if method_key == clause:
                    return method
                if method_key == self.clause2methodname(clause):
                    return method
            elif isinstance(method_key, Matcher.re_type):
                if method_key.search(clause):
                    return method
                

            

    @staticmethod
    def clause_methods_of(modules):
        """ return list of clause methods from given modules """
        if not isinstance(modules, types.ListType): 
            modules = [modules]

        # search each modules for functions
        methods = []
        for module in modules:
            name2item   = lambda x: vars(module)[x]
            new_methods = [name2item(x) for x in dir(module)]
            # filter functions from module
            new_methods = filter(lambda x: type(x) == types.FunctionType, new_methods)
            methods.extend(new_methods)

        # filter by clause names
        methods = filter(lambda x: Matcher.is_clause_method_name(x.__name__), methods)

        return methods


    @staticmethod
    def matches_clause_name(method_name):
        """ method name can be regex as well as string """

        # string
        if isinstance(method_name, types.StringType):
            if method_name in ["before", "after"]:
                return True 
            
            starts_with_clause = lambda c: method_name.startswith("%s_" % c.lower())
            return not not filter(starts_with_clause, CLAUSE_NAMES)
        # re
        elif isinstance(method_name, re_type):
            if method_name.match("^(before|after)$"):
                return True

            md = method_name.search(clause)
            return not not md
            

    @staticmethod
    def is_clause_method_name(method_name):
        """ returns true if method name starts with given_, when_, or then_,
                      or if is before or after """
        if method_name in ["before", "after"]:
            return True 
        for c in CLAUSE_NAMES:
            if method_name.startswith( "%s_" % c.lower() ):
                return True
        else:
            return False


    @staticmethod
    def is_feature(line):  return Patterns.feature.match(line) != None

    @staticmethod
    def is_scenario(line): return Patterns.scenario.match(line) != None


class Reporter:
    def __init__(self, output=sys.stdout):
        self.output = output

    def report(self, content, status=None):
        # skip stop fail sucess
        status_key = {
            "skip":    "-",
            "stop":    "X",
            "fail":    "F",
            "success": ".",
        }
        try:
            self.write("("+ status_key[status] +") ")
        except KeyError:
            pass
    
        self.write(content)
        if status == "fail":
            self.write("\n")
            self.write('-'*60 + "\n")
            traceback.print_exc(file=self.output)
            self.write('-'*60)

    def write(self, msg, code=None):
        self.output.write(msg)


class ColorReporter(Reporter):
    ANSI_CODES = {
        "reset"     : "\x1b[0m",
        "bold"      : "\x1b[01m",
        "boldcyan"  : "\x1b[36;01m",
        "cyan"      : "\x1b[36;06m",
        "fuscia"    : "\x1b[35;01m",
        "purple"    : "\x1b[35;06m",
        "boldblue"  : "\x1b[34;01m",
        "blue"      : "\x1b[34;06m",
        "boldgreen" : "\x1b[32;01m",
        "green"     : "\x1b[32;06m",
        "boldyellow": "\x1b[33;01m",
        "yellow"    : "\x1b[33;06m",
        "boldred"   : "\x1b[31;01m",
        "red"       : "\x1b[31;06m",
    }

    def report(self, content, status=None):
        # skip stop fail sucess
        color_key = {
            "skip":    "cyan",
            "stop":    "yellow",
            "fail":    "red",
            "success": "green",
        }
        try:
            code = color_key[status]
        except KeyError:
            code = None
    
        self.write(content, code)
        if status == "fail":
            self.write("\n")
            self.write('-'*60 + "\n")
            traceback.print_exc(file=self.output)
            self.write('-'*60)

    def write(self, msg, code=None):
        if code and code in self.ANSI_CODES:
            self.output.write(self.ANSI_CODES[code])
        self.output.write(msg)
        if code:
            self.output.write(self.ANSI_CODES["reset"])



class Runner:
    def __init__(self, clause_methods=[], output=sys.stdout):
        self.matcher = Matcher(clause_methods)
        self.reporter = ColorReporter(output)

    def run_clauses(self, clauses):
        """ given clauses and set of method candidates, 
            run each clause in order and
            write result in output.
            Exceptions will not be raised, but just written to output """
        # run before method
        self.matcher.find_method_by_name('before', default=lambda:None)()
    
        # run until finish or error
        unimplemented = []
        for i,clause in enumerate(clauses):
            if i is not 0: self.reporter.write("\n")
    
            # skip feature and scenario
            if Matcher.is_feature(clause) or Matcher.is_scenario(clause):
                self.reporter.report(clause)
                continue
    
            # find method for clause
            clause_method = self.matcher.find_method_by_clause(clause)
    
            # stop if no method found
            if not clause_method:
                self.reporter.report(clause, "stop")
                unimplemented.append(clause)
                break
    
            # run method
            success = self.run_method(clause_method, clause)
            if not success:
                break
        success_count = i
        if i is not 0: self.reporter.write("\n")
    
        # run after method
        self.matcher.find_method_by_name('after', default=lambda: None)()

        unimplemented = self.report_remaining_methods(clauses[i+1:], unimplemented)
        self.report_suggesting_unimplemented_methods(unimplemented)

        return success_count


    def report_remaining_methods(self, remaining_clauses, unimplemented):
        for clause in remaining_clauses:
            if self.matcher.find_method_by_clause(clause):
                self.reporter.report(clause+"\n", "skip")
            else:
                self.reporter.report(clause+"\n", "stop")
                unimplemented.append(clause)
        self.reporter.write("\n")
        return unimplemented


    def report_suggesting_unimplemented_methods(self, unimplemented):
        if unimplemented:
            methods_to_suggest = [self.matcher.clause2methodname(c) for c in unimplemented]
            method_definitions = ["""def %s():\n\tassert False, "Implement me!"\n""" % m for m in methods_to_suggest]
            suggesting_method_doc = """\nCreate the following method: \n\n%s\n""" % "\n".join(method_definitions)
            self.reporter.report(suggesting_method_doc, "stop")


    #def find_method_by_name(self, name, methods):
    #    for m in methods:
    #        if m.__name__ == name:
    #            return m
    #    else:
    #        return None


    #def find_method_by_clause(self, clause, methods):
    #    ''' find and return apropriate method for the given clause '''
    #    #method_name = self.matcher.clause2methodname(clause)
    #    #return self.find_method_by_name(method_name, methods)
    #    for c in [clause, self.matcher.clause2methodname(clause)]:
    #        method = pyeature.Loader.loaded_clauses.get(c, None)
    #        if method:
    #            return method


    #def find_and_call_method_by_name(self, name, methods):
    #    ''' run a method that matches the exact name '''
    #    m = self.matcher.find_method_by_name(name)
    #    if m: 
    #        m()
    #    return not not m


    def run_method(self, method, clause):
        """ run a clause with method given, and report result to output """
        try:
            method()
        except:
            self.reporter.report(clause, "fail")
            return False
        else:
            self.reporter.report(clause, "success")
            return True




def run(feature_file, step_file_dir, output=sys.stdout):
    """ default method for pyeature: run given feature file with given step file(or directory)
    
    returns number of successful steps ran
    """
    # load clauses from feature and methods from step definition
    #clauses = extract(open(feature_file).read())
    clauses = extract_file(feature_file)
    clause_methods = Loader().load_steps(step_file_dir)

    # run clauses
    return Runner(clause_methods, output=output).run_clauses(clauses)


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

