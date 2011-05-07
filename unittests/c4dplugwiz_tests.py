# encoding: utf-8
'''
Created on 01.05.2011

@author: andre
'''
import unittest
import os
import shutil
import codecs
from c4dplugwiz import TextFX
from c4dplugwiz import FolderStructure
from c4dplugwiz import CLIError

CURDIR = os.path.abspath(os.curdir)

class TestTextFX(unittest.TestCase):


    def testToCamelcase(self):
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
            result = TextFX.tocamelcase(sample)
            self.assertEqual(result, expected[i])
            
    def testToCamelcaseUnicode(self):
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
            result = TextFX.tocamelcase(sample)
            self.assertEqual(result, expected[i])
            
        self.assertEqual(u'hôtFlâmíngCåts', TextFX.tocamelcase(u'hôt_Flâmíng __ Cåts', capitalized=False))

    def testSplitcamelcase(self):
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
            result = TextFX.splitcamelcase(sample)
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
                u'"Gauß"']
        expected = ['AesbestShop', 
                    'SueperDueperPlugin', 
                    'RiemannZeta',
                    '',
                    '',
                    'AndresSSuperPLUGIN',
                    'AndisSSuperPluginSTOP',
                    'Gauss']
        for i, sample in enumerate(data):
            result = TextFX.sanitize(sample, safechar='', 
                                     replacediacritics=True, 
                                     replaceumlauts=True, 
                                     replacegreek=True, 
                                     allowedchars='')
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
                                     replacediacritics=True, 
                                     replaceumlauts=False, 
                                     replacegreek=True, 
                                     allowedchars=r'\\')
            self.assertEqual(result, expected[i])
            

class TestFolderStructure(unittest.TestCase):

    def assertFilesEqual(self, file1, file2):
        text1 = codecs.open(file1, 'rU', 'utf-8').read()
        text2 = codecs.open(file2, 'rU', 'utf-8').read()
        return self.assertMultiLineEqual(text1, text2)
      
    def testInitialization(self):
        fs = FolderStructure()
        bogusrootdir = './data/doesnexist'
        bogusrulesfile = '../..'
        rootdir = './data/sources/filenametests'
        rulesfile = './data/rules.py'
        self.assertRaises(CLIError, fs.initialize, bogusrootdir, bogusrulesfile)
        fs = FolderStructure()
        fs.initialize(rootdir, rulesfile)
        self.assertEqual(os.path.join(CURDIR, 'data', 'sources', 'filenametests'), fs.dir)
        self.assertEqual(os.path.join(CURDIR, 'data', 'rules.py'), fs.rulesfilepath)
        self.assertTrue(len(fs.ruleslist) > 0)
        
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
        rulesfile = './data/rules.py'
        fs = FolderStructure()
        fs.initialize(rootdir, rulesfile)
        fs.filltokentable('1000001', 'My Greatest Plugin', 'Andre Berg', 'Berg Media')
        self.assertTrue(len(fs.tokentable) > 0)
        fs.processnames(True)
        m = 0
        for dirpath, dirnames, filenames in os.walk(rootdir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                # assert that there are no magic token chars left in any one file name
                self.assertTrue('<' not in somefile)
                self.assertTrue('>' not in somefile)
                self.assertTrue('${' not in somefile)
                m += 1
        self.assertEqual(n, m, 'number of input files should equal number expected output files')
        
    def testFileContentsProcessing(self):
        destdir = os.path.abspath('./data/output/contenttests')
        sourcedir = os.path.abspath('./data/sources/contenttests')
        expectdir = os.path.abspath('./data/expected/contenttests')
        rulesfile = './data/rules.py'
        n = 0
        for dirpath, dirnames, filenames in os.walk(sourcedir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                filepath = os.path.join(dirpath, somefile)
                destpath = os.path.join(destdir, somefile)
                shutil.copy2(filepath, destpath)
                n += 1
        fs = FolderStructure()
        fs.initialize(destdir, rulesfile)
        fs.filltokentable(1000003, "Make Awesome Button", "Andre Berg", "Berg Media")
        fs.processcontents()
        m = 0
        for dirpath, dirnames, filenames in os.walk(destdir): #@UnusedVariable IGNORE:W0612
            for somefile in filenames:
                actual = os.path.join(dirpath, somefile)
                expected = os.path.join(expectdir, somefile)
                self.assertFilesEqual(actual, expected)
                m += 1
        self.assertEqual(n, m, 'number of input files should equal number expected output files')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()