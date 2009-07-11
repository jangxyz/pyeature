#!/usr/bin/python
# coding: utf-8

from env import *
import unittest, pyeature


class ExtractingClausesTestCase(unittest.TestCase):
    ''' 추출: feature 파일에서 clause들을 추출한다 '''
    def setUp(self):
        self.filename = os.path.join(RESOURCEDIR, 'sample.feature')
        self.text = open(self.filename).read()
        """
            Given I have some text as given
            And   another text for additional given
            
            When I write when
            And  another text for additional when
            
            Then I have then
            And  another then
        """

    def test_extracting_clauses_from_string(self):
        ''' [추출] 텍스트에서 6개의 clause를 추출한다 '''
        extracts = pyeature.extract(self.text)
        assert len(extracts) == 6

    def test_extracting_clauses_from_a_feature_file(self):
        ''' [추출] 파일에서 6개의 clause를 추출한다 '''
        extracts = pyeature.extract_file(self.filename) 
        assert len(extracts) == 6

    def test_extracting_clauses_that_starts_with_given_when_and_then(self):
        ''' [추출] given, when, then으로 시작하는 문장만 clause로 추출한다 '''
        self.text += """Some other words
            And another word
        Tada"""
        extracts = pyeature.extract(self.text)
        assert len(extracts) == 7

    def test_extracts_every_keywords(self):
        ''' [추출] Feature, Scenario라는 키워드도 인식한다 '''
        self.text = """Feature: some feature

        Scenario: some scenario

        %s """ % self.text
        extracts = pyeature.extract(self.text) 
        assert len(extracts) == 8


class ExtractingScenariosTestCase(unittest.TestCase):
    pass


class ConvertingStringIntoMethodNameTestCase(unittest.TestCase):
    ''' 메소드 이름 변환 '''
    def setUp(self):
        self.clauses = ['Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then	some sp3c!al,, characters?!',
                        'And  another then',
                        ]
        self.matcher = pyeature.Matcher()

    def test_that_continuous_spaces_are_turned_into_an_underscores(self):
        ''' [이름변환] 연속된 공백은 _로 '''
        methodname = self.matcher.clause2methodname(self.clauses[0])
        assert ' ' not in methodname
        assert '_' in methodname
        assert methodname.count('_') == 6

    def test_that_uppercase_turned_into_lowercase(self):
        ''' [이름변환] 대문자는 소문자로 '''
        methodname = self.matcher.clause2methodname(self.clauses[0])
        assert 'I' not in methodname
        assert 'G' not in methodname
        assert 'i' in methodname
        assert 'g' in methodname

    def test_that_and_becomes_previous_clause_name(self):
        ''' [이름변환] and는 이전 clause를 따른다 '''
        converted = [self.matcher.clause2methodname(c) for c in self.clauses]
        assert converted[1].startswith('given_')
        assert converted[3].startswith('when_')
        assert converted[5].startswith('then_')

    def test_that_non_alphanumeric_characters_change_into_underscore(self):
        ''' [이름변환] 알파벳+숫자가 아닌 글자는 _로 '''
        methodname = self.matcher.clause2methodname(self.clauses[4])
        assert methodname == 'then_i_have_then_some_sp3c_al_characters_'

    def test_converting_clause_sentence_to_method_name(self):
        ''' [이름변환] 문장을 메소드 이름으로 '''
        converted = [self.matcher.clause2methodname(c) for c in self.clauses]
        assert converted == ['given_i_have_some_text_as_given',
                             'given_another_text_for_additional_given',
                             'when_i_write_when',
                             'when_another_text_for_additional_when',
                             'then_i_have_then_some_sp3c_al_characters_',
                             'then_another_then'
                            ]
        

class RunSampleFeatureTestCase(unittest.TestCase):
    ''' sample.feature 파일 실행 '''
    def setUp(self):
        # load clauses from a sample feature file
        self.sample_filename = os.path.join(RESOURCEDIR, 'sample.feature')
        self.clauses = [
                        'Given  I have some text as given',
                        'And   another text for additional given',
                        'When I write when',
                        'And  another text for additional when',
                        'Then I have then some result',
                        'And  another then',
                       ]

        # load clause methods from a sample step definition file
        self.step_filename = os.path.join(RESOURCEDIR, 'sample_step.py')
        #filename_part = os.path.basename(self.step_filename).rsplit('.', 1)[0]
        #module = __import__(filename_part)
        #self.clause_methods = pyeature.Matcher().clause_methods_of(module)
        self.clause_methods = pyeature.Loader().load_steps(self.step_filename)

        from StringIO import StringIO
        self.output = StringIO()
        self.runner = pyeature.Runner(self.clause_methods, output=self.output)

    def tearDown(self):
        self.output.close()

    def test_running_clauses(self):
        ''' [실행] 불러들인 clause와 메소드를 가지고 실행한다 '''
        self.runner.run_clauses(self.clauses)

        # clauses are printed out
        for clause in self.clauses:
            assert clause in self.output.getvalue()


    def append_clause_method(self, method, name):
        ''' add a new method to clause methods, removing if already existed '''
        method.func_name = name
        pyeature.Loader.loaded_clauses[name] = method
        #for m in self.runner.matcher.clause_methods:
        #    if m.__name__ == name:
        #        self.runner.matcher.clause_methods.remove(m)
        #self.runner.matcher.clause_methods.append(method)
        #clause_methods.append( method )


    def test_running_clauses_making_exception_does_not_raise_exception(self):
        ''' [실행] 실행 중 익셉션이 나도 예외를 출력만 할 뿐 직접 발생시키진 않는다 '''
        # method should raise NameError
        self.append_clause_method(lambda: y, 'given_another_text_for_additional_given')

        self.runner.run_clauses(self.clauses)

        # but exception is printed, not raised
        assert "Traceback (most recent call last):" in self.output.getvalue()


    def test_that_multiple__exceptions_skip_rest_at_first_occurence(self):
        ''' [실행] 예외가 여러 군데에서 나도 첫번째 예외에서 멈춘다 '''
        # methods should raise NameError
        self.append_clause_method(lambda: y, 'given_another_text_for_additional_given')
        self.append_clause_method(lambda: y, 'when_i_write_when')
        
        self.runner.run_clauses(self.clauses)

        # exception is printed once, and then the running stops
        assert self.output.getvalue().count('Traceback (most recent call last):') == 1


    def test_non_successive_clause_method_should_not_run(self):
        ''' [실행] 정의되지 않은 메소드를 만나면 실행이 멈춘다 '''
        # method should raise NameError
        self.append_clause_method(lambda: y, 'then_another_then')

        self.runner.run_clauses(self.clauses)

        assert "Traceback (most recent call last):" not in self.output.getvalue()


    def test_that_running_before_methods_should_raise_exception_when_wrong(self):
        ''' [실행] before hook은 실행이 된다 '''
        clause_methods = []
        self.append_clause_method(lambda: y, 'before')
        self.assertRaises(NameError, self.runner.run_clauses, self.clauses)


    def test_running_after_methods_should_raise_exception_when_wrong(self):
        ''' [실행] after hook은 실행이 된다 '''
        clause_methods = []
        self.append_clause_method(lambda: y, 'after')
        self.append_clause_method(lambda: y, 'after2')
        self.assertRaises(NameError, self.runner.run_clauses, self.clauses)


    def test_run_with_a_step_definition_file(self):
        ''' [실행] step 정의 파일이 주어지면 실행한다 '''
        pyeature.run(self.sample_filename, self.step_filename, self.output)


    def test_run_returns_successful_steps(self):
        ''' [실행] 성공적으로 실행한 step의 수를 리턴한다 '''
        num = pyeature.run(self.sample_filename, self.step_filename, self.output)
        assert num == 1

    def test_run_with_step_definition_directory(self):
        ''' [실행] step 정의 파일이 있는 디렉토리를 주면 실행한다 '''
        file_run  = pyeature.run(self.sample_filename, self.step_filename, self.output)
        directory = os.path.dirname(os.path.abspath(self.step_filename))
        directory_run = pyeature.run(self.sample_filename, directory, self.output)
        assert file_run == directory_run



if __name__ == '__main__':
    try:
        import testoob
        testoob.main()
    except ImportError:
        loader = unittest.defaultTestLoader
        loader.testMethodPrefix = 'test'
        unittest.main(testLoader = loader)

