#!/usr/bin/python
# coding: utf-8

import re, types, sys, traceback, os
sys.path.append(os.getcwd())
from optparse import OptionParser

import pyeature

##
## Keyword definitions
##

lang = {
    'en': { 
        'feature': 'Feature', 'scenario': 'Scenario',
        'given': 'Given', 'when': 'When', 'then': 'Then', 'and': 'And', 
    },
    'ko': {
        'given': '처음에',
        'when': '만약',
        'then': '그러면',
        'and': ['그리고', '또'],
    },
}

##
##



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

class World: pass


_FEATURE, _SCENARIO  = 'Feature', 'Scenario'
_GIVEN, _WHEN, _THEN, _AND = 'Given', 'When', 'Then', 'And'
class Patterns:
    """ patterns used to parse sentence of feature file """
    def __init__(self, keyword_dict={}):
        default_dict = { 
            'feature': _FEATURE, 'scenario': _SCENARIO,
            'given': _GIVEN, 'when': _WHEN, 'then': _THEN, 'and': _AND, 
        }
        default_dict.update(keyword_dict)
        keyword_dict = default_dict

        # set base patterns
        FEATURE, SCENARIO, GIVEN, WHEN, THEN, AND = [keyword_dict[k] for k in ['feature', 'scenario', 'given', 'when', 'then', 'and']]
        

        # set rest of patterns
        CLAUSE_NAMES     = [GIVEN, WHEN, THEN]
        ALL_CLAUSE_NAMES = [GIVEN, WHEN, THEN, AND]
        EVERY_KEYWORDS =   [FEATURE, SCENARIO, AND] + CLAUSE_NAMES

        template = r'^\s*(%s)'
        self.feature  = re.compile(template % FEATURE,  re.IGNORECASE)
        self.scenario = re.compile(template % SCENARIO, re.IGNORECASE)
        self.every_keywords = re.compile(template % '|'.join(EVERY_KEYWORDS), re.IGNORECASE)
        self.clauses = re.compile(template % '|'.join(CLAUSE_NAMES), re.IGNORECASE)
        self.and_clause = re.compile(template % AND, re.IGNORECASE)
        self.starts_with_clause_name = re.compile("^(%s)\s+" % '|'.join(CLAUSE_NAMES))

        

    def remove_clause_name_prefix(self, clause):
        """ "Given that I did ..." => "that I did ..." """
        return self.starts_with_clause_name.sub('', clause)

    def change_and_clause_name(self, clause, new_clause_name):
        """ "Given ...\nAnd something" => "Given something" """
        return self.and_clause.sub(new_clause_name, clause)

    def is_scenario(self, line):    return self.scenario.match(line)   != None
    def is_feature(self, line):     return self.feature.match(line)    != None
    def is_any_keyword(self, line): return self.every_keywords.match(line) != None
    def match_clause(self, line):   return self.clauses.match(line)
    def is_and_clause(self, line):  return self.and_clause.match(line) != None


def given(clause): return Loader.step_decoration(_GIVEN, clause)
def when(clause):  return Loader.step_decoration(_WHEN,  clause)
def then(clause):  return Loader.step_decoration(_THEN,  clause)


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
                new_module = __import__(module_name)

            new_module.self = self.global_world
            return new_module
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
            pyeature.Loader.loaded_clauses[clause] = method
            return method
        return working_method



class Matcher:
    re_type = type(re.compile(''))
    """ match each sentence with clauses """
    def __init__(self, clause_methods=[]):
        self.previous_clause_name = None
        self.clause_methods = clause_methods
        self.patterns = Patterns()

    def clause2methodname(self, clause):
        """ convert a clause sentence into a method name
              - ' Given some pre-condition' => 'given_some_pre_condition'
              - 'And another given' => 'given_another_given' (checking previous)
              - 'Then I have then	some sp3c!al,, characters?!'
                  => 'then_i_have_then_some_sp3c_al_characters_'
        """

        def clause_name_of(sentence):
            """  return clause name of sentence, if it is a clause (None if not)
                    Given|When|Then => itself
                    And             => previous clause name
                    anything else   => None
            """
            matched = self.patterns.match_clause(sentence)
            # store as previous clause name when Given|When|Then
            if matched: 
                self.previous_clause_name = matched.group().lstrip()
            # None if it isn't And clause
            elif not self.patterns.is_and_clause(sentence):
                return
            return self.previous_clause_name

        clause_name = clause_name_of(clause)
        if not clause_name: return
    
        # change prefix of clause 
        clause = self.patterns.change_and_clause_name(clause, clause_name)
        convert_space = lambda c: re.sub(r'\W+', '_', c.lstrip()).lower()
        return convert_space(clause)



    def find_method_by_name(self, name, default=None):
        return self.clause_methods.get(name, default)


    def find_method_by_clause(self, clause):
        ''' find and return appropriate method for the given clause 
        
        for every keys registered in loaded_clauses, try matching
            1. the clause itself as string
            2. the clause converted into method name
            3. the clause without clause prefix
            4. the clause as regex
            #5. the clause without clause prefix as regex
        '''
        clause = clause.strip()
        #print clause

        for method_key,method in pyeature.Loader.loaded_clauses.iteritems():
            clause_wo_prefix = self.patterns.remove_clause_name_prefix(clause)
            # string
            if isinstance(method_key, types.StringType):
                any_chances = [clause, self.clause2methodname(clause), clause_wo_prefix]
                if method_key in any_chances:
                    return method
            # re
            elif isinstance(method_key, Matcher.re_type):

                md = method_key.search(clause) or method_key.search(clause_wo_prefix)
                if md:
                    args = [md.group(0)] + list(md.groups())
                    method.func_globals['args'] = args # 
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
    def is_clause_method_name(method_name):
        """ returns true if method name starts with given_, when_, or then_,
                      or if is before or after """
        if method_name in ["before", "after"]:
            return True 

        valid_format = lambda c: method_name.startswith("%s_" % c.lower())
        valids = filter(valid_format, [_GIVEN, _WHEN, _THEN])
        return not not valids # False if []

    def is_feature(self, clause):  return self.patterns.is_feature(clause)
    def is_scenario(self, clause): return self.patterns.is_scenario(clause)


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
        unimplemented, i = [], 0
        for i,clause in enumerate(clauses):
            if i is not 0: self.reporter.write("\n")
    
            # skip feature and scenario
            if self.matcher.is_feature(clause) or self.matcher.is_scenario(clause):
                self.reporter.report(clause)
                continue
    
            # find method for clause
            #print 1
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
            #print 2
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


def extract(text, keyword_dict={}):
    """ extracts a list of clauses from given text """
    extracts = [line.rstrip("\n") for line in text.split("\n")]
    extracts = filter(Patterns(keyword_dict).is_any_keyword, extracts)
    return extracts

def extract_file(filename, keyword_dict={}): 
    text = open(filename).read()
    return extract(text, keyword_dict)


def run(feature_file, step_file_dir, options, output=sys.stdout):
    """ default method for pyeature: run given feature file with given step file(or directory)
    
    returns number of successful steps ran
    """
    # load clauses from feature and methods from step definition
    clauses = extract_file(feature_file)
    clause_methods = Loader().load_steps(step_file_dir)

    # run clauses
    return Runner(clause_methods, output=output).run_clauses(clauses)


def parse_args():
    # set options to parse
    usage = "usage: %prog [options] some.feature [some_step.py]"
    parser = OptionParser(usage=usage)
    parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False, help="be quite, and only return 0 or some other value that indicates whether all test ran successfully or not")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="be more verbose, and print additional information while running")
    parser.add_option("-l", "--language", metavar="LANG", dest="language", default='en', help="target language to parse (default en)")

    (options, args) = parser.parse_args()

    # rest of arguments
    if len(args) < 1:
        parser.error("You must tell me the feature file and step definition file.")

    feature_file = args[0]
    if len(args) >= 2:
        step_definition_directory = args[1]
    else:
        dirname = os.path.dirname(os.path.abspath(feature_file))
        step_definition_directory = os.path.join( dirname, 'step_definitions' )
        if not os.path.isdir(step_definition_directory):
            raise Exception

    return feature_file, step_definition_directory, options



if __name__ == '__main__':
            
#    try:
#        feature_file = sys.argv[1]
#        if len(sys.argv) >= 3:
#            step_definition_directory = sys.argv[2]
#        else:
#            dirname = os.path.dirname(os.path.abspath(feature_file))
#            step_definition_directory = os.path.join( dirname, 'step_definitions' )
#            if not os.path.isdir(step_definition_directory):
#                raise Exception
#    except:
#        prog_name = sys.argv[0].rsplit(os.sep, 1)[-1]
#        sys.exit("""You must tell me the feature file and step definition file.
#
#    Usage: %s some.feature some_step.py
#        """ % prog_name)

    feature_file, step_definition_directory, options = parse_args()
    run(feature_file, step_definition_directory, options)

