# encoding: utf-8
'''
Created on 01.05.2011

@author: andre
'''
import unittest
from c4dplugwiz import TextFX

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
            result = TextFX.sanitize(sample, safechar='', replacediacritic=True, replaceumlaut=True, replacegreek=True, allowedchars='')
            self.assertEqual(result, expected[i])
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()