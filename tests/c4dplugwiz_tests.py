# encoding: utf-8
# pylint: disable-msg=W0212
'''
Created on 01.05.2011

@author: andre
'''
import codecs
import os
import re
import shutil
import unittest

from c4dplugwiz import TextFX, PluginWizard, CLIError, PLUGIN_TYPE_TAG


CURDIR = os.path.abspath(os.curdir)
DATADIR = 'data'
SOURCESDIR = os.path.join(DATADIR, 'sources')
RULESFILENAME_DEFAULT = 'rules.py'
RULESFILE_DEFAULT = os.path.join(DATADIR, RULESFILENAME_DEFAULT)

CONFIG_DEFAULT = {
    'pluginId': 1000003,
    'pluginName': "Make Awesome Button",
    'author': "Andre Berg",
    'org': "Berg Media",
    'rulesFile': RULESFILE_DEFAULT,
    'srcdataPath': SOURCESDIR
}

CONFIG_ALT = { 
    'pluginId': 1000001, 
    'pluginName': 'My Greatest Plugin', 
    'author': u'André Berg', 
    'org': 'Sera Media VFX',
    'rulesFile': RULESFILE_DEFAULT,
    'srcdataPath': SOURCESDIR
}

CONFIG_BOGUS = {
    'pluginId': -9999999,
    'pluginName': "",
    'author': u"André Berg",
    'org': '',
    'rulesFile': '../..',
    'srcdataPath': './data/doesnexist'
}

class TestTextFX(unittest.TestCase):


    def testToCamelCase(self):
        data = ['hot flaming cats',
                'HotFlamingCats',
                'hotFlamingCats',
                'hot_flaming_cats',
                'Hot Flaming _ Cats',
                'Hot_Flaming __ Cats']
        expected = ['HotFlamingCats',
                    'HotFlamingCats',
                    'HotFlamingCats',
                    'HotFlamingCats',
                    'HotFlamingCats',
                    'HotFlamingCats']
        for i, sample in enumerate(data):
            result = TextFX.to_camelcase(sample)
            self.assertEqual(result, expected[i])
            
    def testToCamelCaseUnicode(self):
        data = [u'höt fläming cäts',
                u'HötFlämingCäts',
                u'hötFlämingCäts',
                u'höt_fläming_cäts',
                u'Höt Fläming _ Cäts']
        expected = [u'HötFlämingCäts',
                    u'HötFlämingCäts',
                    u'HötFlämingCäts',
                    u'HötFlämingCäts',
                    u'HötFlämingCäts']
        for i, sample in enumerate(data):
            result = TextFX.to_camelcase(sample)
            self.assertEqual(result, expected[i])
            
        self.assertEqual(u'hôtFlâmíngCåts', TextFX.to_camelcase(u'hôt_Flâmíng __ Cåts', capitalized=False))

    def testSplitCamelCase(self):
        data = ['My Plugin Extraordinaire!',
                'Super Duper Plugin',
                'RSS Generator',
                '    ',
                '_',
                'AndreSSuperPLUGIN',
                'AndisSSuper_PluginSTOP !']
        expected = [['My', 'Plugin', 'Extraordinaire'], 
                    ['Super', 'Duper', 'Plugin'],
                    ['RSS', 'Generator'], 
                    [],
                    [],
                    ['Andre', 'SSuper', 'PLUGIN'],
                    ['Andis', 'SSuper', 'Plugin', 'STOP']]
        for i, sample in enumerate(data):
            result = TextFX.split_camelcase(sample)
            self.assertEqual(result, expected[i])
        
    
    def testAbbreviate(self):
        data = ['My Plugin Extraordinaire!',
                'Super Duper Plugin',
                'RSS Generator',
                '    ',
                '_',
                'AndreSSuperPLUGIN',
                'AndisSSuper_PluginSTOP !']
        expected = ['MPE', 
                    'SDP', 
                    'RG',
                    '',
                    '',
                    'ASP',
                    'ASPS']
        for i, sample in enumerate(data):
            result = TextFX.abbreviate(sample)
            self.assertEqual(result, expected[i])
            
    def testSanitize(self):
        '''Test sanitize with default arguments'''
        data = ['Really',
                'Super Duper Plugin',
                'RSS Generator',
                '    ',
                '_',
                'AndreSSuperPLUGIN',
                'AndisSSuper_PluginSTOP !']
        expected = ['Really', 
                    'Super_Duper_Plugin', 
                    'RSS_Generator',
                    '____',
                    '_',
                    'AndreSSuperPLUGIN',
                    'AndisSSuper_PluginSTOP__']
        for i, sample in enumerate(data):
            result = TextFX.sanitize(sample)
            self.assertEqual(result, expected[i])

    def testSanitize1(self):
        '''Test sanitize with argument set 1'''
        data = [u'Äsbëst-Shop',
                u'Süper Düper Plugin',
                u'__RiemannΖ',
                '    ',
                '\\_',
                'Andre\'sSSuperPLUGIN',
                'AndisSSuper_PluginSTOP !',
                u'"Gauß"',
                u'André']
        expected = ['AesbestShop', 
                    'SueperDueperPlugin', 
                    'RiemannZeta',
                    '',
                    '',
                    'AndresSSuperPLUGIN',
                    'AndisSSuperPluginSTOP',
                    'Gauss', 
                    'Andre']
        for i, sample in enumerate(data):
            result = TextFX.sanitize(sample, safechar='', 
                                     replace_diacritics=True, 
                                     replace_umlauts=True, 
                                     replace_greek=True, 
                                     allowed_chars='')
            self.assertEqual(result, expected[i])
            
    def testSanitizeWithDifferentEncoding(self):
        '''Test sanitize with a different encoding than the default.'''
        encoding = 'latin-1'
        data = [u'Äsbëst-Shop'.decode("utf-8").encode(encoding),
                u'Süper Düper Plugin'.encode(encoding),
                '    '.encode(encoding),
                '\\_'.encode(encoding),
                'Andre\'sSSuperPLUGIN'.encode(encoding),
                'AndisSSuper_PluginSTOP !'.encode(encoding),
                u'"Gauß"'.encode(encoding),
                u'André'.encode(encoding)]
        expected = ['AesbestShop', 
                    'SueperDueperPlugin', 
                    '',
                    '',
                    'AndresSSuperPLUGIN',
                    'AndisSSuperPluginSTOP',
                    'Gauss', 
                    'Andre']
        for i, sample in enumerate(data):
            result = TextFX.sanitize(sample, safechar='', 
                                     replace_diacritics=True, 
                                     replace_umlauts=True, 
                                     replace_greek=True, 
                                     allowed_chars='', encoding=encoding)
            self.assertEqual(result, expected[i])
        
    def testSanitize2(self):
        '''Test sanitize with argument set 2'''
        data = [u'Äsbëst-Shop',
                u'Süper Düper Plugin',
                u'__RiemannΖ',
                '    ',
                '\\_',
                'Andre\'sSSuperPLUGIN',
                'AndisSSuper_PluginSTOP !',
                u'"Gauß"']
        expected = ['Asbest-Shop', 
                    'Super-Duper-Plugin', 
                    '--RiemannZeta',
                    '----',
                    '\\-',
                    'Andre-sSSuperPLUGIN',
                    'AndisSSuper-PluginSTOP--',
                    '-Gau--']
        for i, sample in enumerate(data):
            result = TextFX.sanitize(sample, safechar='-', 
                                     replace_diacritics=True, 
                                     replace_umlauts=False, 
                                     replace_greek=True, 
                                     allowed_chars=r'\\')
            self.assertEqual(result, expected[i])
            

class TestFolderStructure(unittest.TestCase):

    def assertFilesEqual(self, actual, expected, rules=None):            
        text_actual = codecs.open(actual, 'rU', 'utf-8').read()
        text_expected = codecs.open(expected, 'rU', 'utf-8').read()
        
        # Since rules can include dates, user names and other data
        # that's tied to the individual developer we keep files from
        # the 'expected' group free of filling in the actual text 
        # replacements for any rules variable and instead mimick what
        # PluginWizard does when processing the rules file.
        #
        # In other words, we are checking magic token based replacements
        # as usual per 'expected -> actual' system but we are replacing
        # rules in file from the 'actual' group first and then we do the
        # same replacements in files from 'expected' and check if they 
        # both match. Admittedly this is a weaker test than in the first
        # case but it's still better than not being able to verify individual
        # data at all since that is precisely the point of this wizard. 
        if rules is not None:
            pw = PluginWizard(CONFIG_DEFAULT)
            ruleslist = pw._rules_list
            for search, replace in ruleslist:
                text_expected = re.sub(search, replace, text_expected)
        
        return self.assertMultiLineEqual(text_actual, text_expected)
      
    def testInitialization(self):        
        bogusrootdir = './data/doesnexist'
                
        self.assertRaises(CLIError, PluginWizard, config=CONFIG_BOGUS)
        self.assertRaises(CLIError, PluginWizard(CONFIG_DEFAULT).set_destdir, somepath=bogusrootdir)
        
        rootdir = os.path.abspath('./data/output/filenametests')
        
        pw = PluginWizard(CONFIG_DEFAULT, plugin_type=PLUGIN_TYPE_TAG)
        pw.set_destdir(rootdir)
        
        self.assertEqual(os.path.join(CURDIR, 'data', 'sources'), pw.srcdir)
        self.assertEqual(os.path.join(CURDIR, 'data', 'output', 'filenametests'), pw.destdir)
        self.assertEqual(os.path.join(CURDIR, 'data', 'rules.py'), pw._rules_filepath)
        self.assertTrue(len(pw._rules_list) > 0)
        
    def testFileNameProcessing(self):
        rootdir = os.path.abspath('./data/output/filenametests')
        sourcedir = os.path.abspath('./data/sources/filenametests')
        for dirpath, dirnames, filenames in os.walk(rootdir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                filepath = os.path.join(dirpath, somefile)
                os.remove(filepath)
        n = 0
        for dirpath, dirnames, filenames in os.walk(sourcedir): #@UnusedVariable
            for somefile in filenames:
                filepath = os.path.join(dirpath, somefile)
                destpath = os.path.join(rootdir, somefile)
                shutil.copy2(filepath, destpath)
                n += 1
        pw = PluginWizard(CONFIG_ALT)
        pw.set_destdir(rootdir)
        self.assertTrue(len(pw._token_table) > 0)
        pw.process_names(overwrite=True)
        m = 0
        for dirpath, dirnames, filenames in os.walk(rootdir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                # assert that there are no magic token chars left in any one file name
                self.assertTrue(pw.tokenchar_start not in somefile)
                self.assertTrue(pw.tokenchar_end not in somefile)
                self.assertTrue('${' not in somefile)
                m += 1
        self.assertEqual(n, m, 'number of input files should equal number expected output files')
        
    def testFileContentsProcessing(self):
        destdir = os.path.abspath('./data/output/contenttests')
        sourcedir = os.path.abspath('./data/sources/contenttests')
        expectdir = os.path.abspath('./data/expected/contenttests')
        rulesfile = RULESFILE_DEFAULT
        n = 0
        for dirpath, dirnames, filenames in os.walk(sourcedir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                filepath = os.path.join(dirpath, somefile)
                destpath = os.path.join(destdir, somefile)
                shutil.copy2(filepath, destpath)
                n += 1
        config = CONFIG_DEFAULT
        pw = PluginWizard(config)
        pw.set_destdir(destdir)
        pw.process_contents()
        m = 0
        for dirpath, dirnames, filenames in os.walk(destdir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                actual = os.path.join(dirpath, somefile)
                expected = os.path.join(expectdir, somefile)
                self.assertFilesEqual(actual, expected, rulesfile)
                m += 1
        self.assertEqual(n, m, 'number of input files should equal number expected output files')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()