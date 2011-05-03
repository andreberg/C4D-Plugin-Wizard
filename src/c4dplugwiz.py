#!/usr/local/bin/python2.7
# encoding: utf-8
'''
c4dplugwiz -- CINEMA 4D Python plugin wizard

c4dplugwiz is a command line tool and a template system 
that helps with creating python plugins for CINEMA 4D. 
It works by copying pre-existing folder structures from
a data repository to a destination specified by the user.

There can be multiple folder structures, e.g. one per type
of plugin that one can create in CINEMA 4D. 

At the heart lies the idea that these folder structures 
contain dirs and files subject to a customizable template 
system, which is divided into 2 main steps:

    1. Process file names C{I{*}}
    2. Process file contents

I{C{*}) 'file name' refers to names of files as well as folders}

1) A folder structure has dirs and files with file names
containing template tokens with special syntax, that are 
to be replaced with project relevant data. 

Such a token is denoted with the syntax C{<I{Datum}>}, where
C{I{Datum}} is a variable term referring to one datum point.
Furthermore, the ability to transform a datum point to 
obtain variations is specified, which the user can utilize 
with the syntax C{<I{Datum}AsI{Form}>}. Note the adverb C{As}, 
which is used here as a delimiter.

For example, data about the plugin name can be replaced 
unchanged as initially entered by the user in the form of
just C{<PluginName>}, or, instead a variation can be chosen
in the form of C{<PluginNameAsIdentifier>} which will be 
replaced with the name of the plugin, sanitized and in 
I{CamelCase} format. There are a fixed number of variations 
per datum point and the best way to find out about those 
is to use L{FolderStructure.printtokentable()} or simply 
pass the C{-l/--listtokens} flag to the CLI.

Currently, the following data points are used: 
    - C{ID}            I{Supplied by user with a CLI argument}
    - C{PluginName}    I{Supplied by user with a CLI argument}
    - C{AuthorName}    I{Supplied by user with a CLI option, or an environment variable}
    - C{OrgName}       I{Supplied by user with a CLI option, or an environment variable}
    - C{Date}          I{Constructed from C{time.strftime()}}
    - C{Time}          I{Constructed from C{time.strftime()}}

If a datum point is used but the corresponding value can't 
be retrieved, an exception is raised to avoid continuing 
with false information. To ensure a value is found for author
and organization names, you can set the environment variables
C{C4DPLUGWIZ_AUTHORNAME} and C{C4DPLUGWIZ_ORGNAME} respectively.

2) The contents of each file within a folder structure are
then parsed and searched for special patterns. 

These patterns are specified as C{Key = Value} mappings in a 
file called C{rules.py} that should exist at the top level 
of the source data path. Keys as well as Values can be ordinary 
strings or Python statements such as raw regex strings (e.g. C{r'[a-z]'})
or functions calls (e.g. C{time.strftime('%Y')}). 

If you need to import additional modules in order to use some 
functionality for Keys or Values, a special initialization line 
in C{rules.py} can be used to specify a comma separated list of 
modules to import. It must appear as the very first line and 
have the following syntax: C{# import module1,module2,module3 ...} 
and so on (the ellipsis not being part of the syntax). 

Lines in C{rules.py} other than the initialization line starting 
with the hash character are considered comments and ignored, as
well as lines that do not have a format of C{<I{key}>\s*=\s*<I{value}>}
where C{<I{...}>} stands for a variable term and C{\s*} stands for zero
or more spaces. If you need a value for a key to span multiple 
lines, assign the value in I{raw text} form, e.g. between single, 
double or tripple quotes and with carriage returns, linefeeds etc. 
escaped.


@author:     André Berg
             
@copyright:  2011 Berg Media. All rights reserved.
             
@license:    Licensed under the Apache License, Version 2.0 (the "License");\n
             you may not use this file except in compliance with the License.
             You may obtain a copy of the License at
             
             U{http://www.apache.org/licenses/LICENSE-2.0}
             
             Unless required by applicable law or agreed to in writing, software
             distributed under the License is distributed on an B{"AS IS"} B{BASIS},
             B{WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND}, either express or implied.
             See the License for the specific language governing permissions and
             limitations under the License.

@contact:    andre.bergmedia@googlemail.com
@deffield    updated: Updated
'''

import sys
import os
import re
import time
import fileinput
import unicodedata as ud

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from distutils import dir_util as du
from subprocess import Popen, PIPE
import shutil as su
import codecs

__all__ = ['FolderStructure', 'TextFX', 'main']
__version__ = 0.2
__date__ = '2011-04-30'
__updated__ = '2011-05-03'

DEBUG = 1
TESTRUN = 0
PROFILE = 0 or (os.environ.has_key('BMProfileLevel') and os.environ['BMProfileLevel'] > 0)

verbose = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

class TextFX(object):
    '''
    Methods for processing and transforming text.
    Note: currently Unicode support is rather lax.
    '''
    greekchars = {
        'alpha':'a',
        'beta':'b',
        'chi':'c',
        'Delta':'D',
        'delta':'d',
        'epsiv':'e',
        'eta':'h',
        'Gamma':'G',
        'gamma':'g',
        'iota':'i',
        'kappa':'k',
        'Lambda':'L',
        'lambda':'l',
        'mu':'m',
        'nu':'n',
        'Omega':'W',
        'omega':'w',
        'omicron':'x',
        'Phi':'F',
        'phi':'f',
        'phiv':'j',
        'Pi':'P',
        'pi':'p',
        'piv':'v',
        'Psi':'Y',
        'psi':'y',
        'rho':'r',
        'Sigma':'S',
        'sigma':'s',
        'sigmav':'V',
        'tau':'t',
        'Theta':'Q',
        'theta':'q',
        'thetav':'j',
        'Xi':'X',
        'xi':'x',
        'zeta':'z'    
    }
    greektrans = { # IGNORE:W0109
        u'α': 'a',  u'Α': 'A', 
        u'β': 'b',  u'Β': 'B', 
        u'γ': 'g',  u'Γ': 'G', 
        u'δ': 'd',  u'Δ': 'D', 
        u'ε': 'e',  u'Ε': 'E',
        u'ζ': 'z',  u'Ζ': 'Z', 
        u'η': 'e',  u'Η': 'E', 
        u'θ': 'th', u'Θ': 'Th', 
        u'ι': 'i',  u'Ι': 'I', 
        u'κ': 'k',  u'Κ': 'K', 
        u'λ': 'l',  u'Λ': 'L', 
        u'μ': 'm',  u'Μ': 'M', 
        u'ν': 'n',  u'Ν': 'N', 
        u'ξ': 'ks', u'Ξ': 'Ks', 
        u'ο': 'o',  u'Ο': 'O', 
        u'π': 'p',  u'Π': 'P',
        u'ρ': 'r',  u'Ρ': 'R', 
        u'σ': 's',  u'Σ': 'S', 
        u'τ': 't',  u'Τ': 'T', 
        u'υ': 'y',  u'Υ': 'Y', 
        u'φ': 'ph', u'Φ': 'Ph', 
        u'χ': 'ch', u'Χ': 'Ch', 
        u'Ψ': 'ps', u'Ψ': 'Ps', 
        u'ω': 'o',  u'Ω': 'O'        
    }
    greekalphabet = {
        u'α': 'alpha', u'β': 'beta', u'γ': 'gamma', u'δ': 'delta', u'ε': 'epsilon',
        u'ζ': 'zeta', u'η': 'eta', u'θ': 'theta', u'ι': 'iota', u'κ': 'kappa', 
        u'λ': 'lambda', u'μ': 'mu', u'ν': 'nu', u'ξ': 'xi', u'ο': 'omicron', 
        u'π': 'pi', u'ρ': 'rho', u'σ': 'sigma', u'ς': 'fsigma', u'τ': 'tau', 
        u'υ': 'upsilon', u'φ': 'phi', u'χ': 'chi', u'ψ': 'psi', u'ω': 'omega', 
        
        u'Α': 'Alpha', u'Β': 'Beta', u'Γ': 'Gamma', u'Δ': 'Delta', u'Ε': 'Epsilon',
        u'Ζ': 'Zeta', u'Η': 'Eta', u'Θ': 'Theta', u'Ι': 'Iota', u'Κ': 'Kappa', 
        u'Λ': 'Lambda', u'Μ': 'Mu', u'Ν': 'Nu', u'Ξ': 'Xi', u'Ο': 'Omicron', u'Π': 'Pi',
        u'Ρ': 'Rho', u'Σ': 'Sigma', u'Τ': 'Tau', u'Υ': 'Upsilon', u'Φ': 'Phi', 
        u'Χ': 'Chi', u'Ψ': 'Psi', u'Ω': 'Omega'
    }
    phoneticumlauts = {
        u'\xe4': 'ae',
        u'\xe6': 'ae',
        u'\xfc': 'ue',
        u'\xf6': 'oe',
        u'\xdf': 'ss',
        u'\xc4': 'Ae',
        u'\xc6': 'Ae',
        u'\xdc': 'Ue',
        u'\xd6': 'Oe',
        u'\u0153': 'oe',
        u'\u0276': 'oe'
    }
    def __init__(self):
        super(TextFX, self).__init__()

    #def _combiningmarkslistgen():
    #    '''Generates a list with unicode combining marks in range U+0300 to U+036F'''
    #    allmarks = []
    #    for i in range(0, 7):
    #        for j in range(0, 16):
    #            r = u'%su03%x%x' % (u'\\', i, j)
    #            allmarks.append(r.decode('unicode_escape'))
    #            #filename = re.sub(re.compile(r.decode('unicode_escape')), '', filename)
    #    #print allmarks
    #    #print len(allmarks)
    #    return allmarks
        
    @staticmethod
    def precompunichars(word, canonical=True):
        '''
        Precompose Unicode character sequences, using either canonical 
        or nominal mapping, e.g. LATIN SMALL LETTER E (U+0065) + COMBINING ACUTE ACCENT (U+0301) 
        becomes LATIN SMALL LETTER E WITH ACUTE (U+00E9). If canonical 
        is True combining diacritical marks will be mapped to their 
        non-combining forms when they cannot be combined with the letter 
        preceeding the position.
        '''
        if not isinstance(word, unicode):
            raise TypeError("param 'word': expected unicode, got %s" % type(word))
        result = word
        try:
            if canonical:
                result = ud.normalize('NFKC', word)
            else:
                result = ud.normalize('NFC', word)
        except Exception, e:
            print e
            raise e
        
        return result

    @staticmethod
    def decompunichars(word, canonical=True):
        '''
        Decompose Unicode character sequences using either canonical 
        or nominal mapping, e.g. LATIN SMALL LETTER E WITH ACUTE (U+00E9) 
        becomes LATIN SMALL LETTER E (U+0065) + COMBINING ACUTE ACCENT (U+0301). 
        If canonical is True non-combining diacritical marks will be 
        mapped to their combining forms and maybe combined with the letter 
        preceeding the position.
        '''
        if not isinstance(word, unicode):
            raise TypeError("param 'word': expected unicode, got %s" % type(word))
        result = word
        try:
            if canonical:
                result = ud.normalize('NFKD', word)
            else:
                result = ud.normalize('NFD', word)
        except Exception, e:
            print e
            raise e
        
        return result
    
    @staticmethod
    def tocamelcase(word, capitalized=True):
        '''
        Convert 'word' to CamelCase.
        Examples: 
        
        >>> TextFX.tocamelcase('hot flaming cats')
        HotFlamingCats
        >>> TextFX.tocamelcase('HotFlamingCats')
        HotFlamingCats
        >>> TextFX.tocamelcase('hotFlamingCats')
        HotFlamingCats
        >>> TextFX.tocamelcase('hot_flaming_cats')
        HotFlamingCats
        >>> TextFX.tocamelcase('Hot Flaming _ Cats')
        HotFlamingCats
        >>> TextFX.tocamelcase(u'höt_fläming_cäts', False)
        hötFlämingCäts
        
        @param word: the string to convert
        @type word: C{string} or C{unicode}
        @param capitalized: if C{True}, always capitalize the 
                            first character of the result.
        @type capitalized: C{bool}
        '''
        def __capitalizematch(matchobj):
            grp1 = matchobj.group(1)
            if grp1:
                return grp1.capitalize()
            else:
                return matchobj.group(0)
        if word is None: return ''
        word = word.strip()
        word = re.sub(r'_+([^_]+)', __capitalizematch, word)
        word = re.sub(r' ([^ ]+)', __capitalizematch, word)
        word = re.sub(' ', '', word)
        if capitalized:
            word = '%s%s' % (word[0].upper(), word[1:])
        return word
    
    @staticmethod
    def splitcamelcase(word):
        '''
        Split a CamelCaseString into ['Camel', 'Case', 'String'].
        @param word: the string to split
        @type word: C{string}
        '''
        pat = re.compile(r'[A-Z]+[a-z]*', re.UNICODE)
        return re.findall(pat, word)

    @staticmethod
    def abbreviate(word, maxchars=-1):
        '''
        Reduce some string to an abbreviation of a given length.
        Example:
        
        >>> TextFX.abbreviate('AndisSSuper_PluginSTOP ')
        ASPS
        
        @param word: the string to abbreviate
        @type word: C{string}
        @param maxchars: if > 0, determines length of abbreviation, 
                         e.g. with a length of 3, 'ASPS' above became 'ASP'.
        @type maxchars: C{int}
        '''
        word = word.strip()
        #pat = re.compile(r'\b(\w)', re.UNICODE)
        pat = re.compile(r"([A-Z])[A-Z]*[a-z]*")
        word = re.findall(pat, word)
        if maxchars > 0:
            word = word[0:maxchars]
        return "".join(word)
    
    @staticmethod
    def sanitize(word, safechar='_', replaceumlaut=False, replacediacritic=False, replacegreek=False, allowedchars='_\-()'):
        '''
        Sanitize word so that it might be used as a filename 
        in an online transfer or in software that needs to 
        work on a restricted set of names for files and other
        resource descriptors, e.g. only underscores are allowed, 
        no accented characters, etc.
        
        Tries to deal gracefully with higher order characters, 
        such as diacritics so that the original meaning of a 
        word may be preserved better than, for example, just 
        replacing higher order chars with a char deemed safe, 
        like an underbar '_', e.g. given 'Über', 'Ueber' or
        'Uber' are generally favorable to '_ber'.
                        
        @param word: the word to sanitize
        @type word: C{string}
        @param safechar: the char to use for replacing non-allowed chars
        @type safechar: C{string}
        @param replaceumlaut: 
            if True, replace umlauts like 'ä' with a phonetic 
            equivalent like 'ae'.
        @type replaceumlaut: C{bool}
        @param replacediacritic: 
            if True, replace diacritics with a decomposed 
            form where the mark is dropped (e.g. 'ç' becomes 'c')
        @type replacediacritic: C{bool}
        @param replacegreek: 
            if True, replace greek letters with their 
            translitterated name, e.g. 'π' becomes 'pi'.
        @type replacegreek: C{bool}
        @param allowedchars: string of chars to allow unchanged 
            (note: the string is used within a regex)
        @type allowedchars: C{string}
        '''
        #fileparts = re.split(ur'(.*)\.(.*)$', word.rstrip())
        # if len(fileparts) > 1:
        #     filename = u"".join(fileparts[0:-2])
        #     fileext = u".%s" % fileparts[-2]
        # else:
        #     filename = fileparts[0]
        #     fileext = u""
        word = re.sub(' ', safechar, word)
        if replaceumlaut:
            temp = ''
            for c in word:
                if c in TextFX.phoneticumlauts:
                    temp += TextFX.phoneticumlauts[c]
                else:
                    temp += c
            word = temp
        if replacediacritic:
            # canonically decompose the search string so we can "weed out" the diacritical marks
            word = ud.normalize('NFKD', unicode(word))
            # dynamically generate combining marks list
            marks = []
            for i in range(0, 7):
                for j in range(0, 16):
                    r = u"%su03%x%x" % ('\\', i, j)
                    marks.append(r.decode('unicode_escape'))        
            # loop through filename and filter out the diacritical marks
            res = u''
            for char in word:
                if char in marks:
                    pass
                else:
                    res = res + char
            word = res
        if replacegreek:
            temp = ''
            for c in word:
                if c in TextFX.greekalphabet:
                    temp += TextFX.greekalphabet[c]
                else:
                    temp += c
            word = temp
        word = re.sub(ur'[^a-zA-Z0-9%s]' % allowedchars, safechar, word)
        return word
        
class FolderStructure(object):
    '''
    Represents the folder structure for one type of plugin.
    
    Provides methods for token replacements in the names and 
    content of files contained within the folder structure.
    '''
    TOKENREGEX      = re.compile(r'<(?P<token>\w+?)>')
    TOKENXFORMREGEX = re.compile(r'<(?P<token>\w+?)As(?P<form>\w+?)>')
    INITREGEX       = re.compile(r'#\s*import (?P<modules>[\w, ]+)')
    KVSPLITREGEX    = re.compile(r'\s*=\s*')
    HIDDENFILES     = ['.DS_Store', 'desktop.ini']
    
    def __init__(self):
        super(FolderStructure, self).__init__()
        self.dir = None
        self.tokentable = {}
        self.ruleslist = []

    def setrootdir(self, rootdir):
        '''
        Set C{self.dir} to C{rootdir} to be used in processing later on.
        @param rootdir: an existing directory relative to C{os.curdir} 
            or as absolute path
        @type rootdir: C{string}
        '''
        if os.path.exists(os.path.abspath(rootdir)):
            self.dir = rootdir
        else:
            raise CLIError("path at '%s' doesn't exist" % rootdir)
        
    def _getauthorname(self):
        result = None
        if os.environ.has_key('C4DPLUGWIZ_AUTHORNAME'):
            result = os.environ['C4DPLUGWIZ_AUTHORNAME']
        else:
            try:
                if sys.platform == 'darwin':
                    out, err = Popen(
                        ['/bin/sh -c "arch -i386 osascript -e \'long user name of (system info)\'"'], 
                        stdout=PIPE, shell=True
                    ).communicate()
                    if err: print err
                    fulluser = out
                elif 'win' in sys.platform:
                    #import _winreg as wreg # IGNORE:F0401 @UnresolvedImport
                    #key = wreg.OpenKey(wreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer')
                    #fulluser = wreg.QueryValue(key, 'Logon User Name')
                    import win32api # IGNORE:F0401 @UnresolvedImport
                    fulluser = win32api.GetUserName()
                result = fulluser.strip() # IGNORE:E1103
            except Exception, e:
                raise CLIError(e)
        return result
    
    def printtokentable(self, indent=3):
        '''
        Print datum and form entries of the token table.
        
        @param indent: how many spaces for indentation
        @type indent: C{int}
        '''
        spaces = " " * indent
        spaces2 = spaces + spaces
        if verbose > 0:
            print "Listing token table..."
            print "Format:"
            print "%sdatum\n%sform1\n%sform2\n%s..." % (spaces, spaces2, spaces2, spaces2)
        for k, v in self.tokentable.iteritems():
            print 
            print "%s" % k,
            print
            for entry in v:
                print "%s%s" % (spaces, entry)
        return True
         
    def filltokentable(self, pluginid, pluginname, authorname, orgname):
        '''
        Fill the table of angle bracket ('<...>') tokens.
        
        The table consists of a dict of metadata dicts, 
        the latter of which can have multiple entries,
        one for each form the datum can be in. E.g. if
        the datum is 'AuthorName', it can have a form as
        identifier, as abbreviation, etc.
        
        @param pluginid: unique ID for the plugin
        @type pluginid: C{string}
        @param pluginname: name of the plugin as entered 
            by the user
        @type pluginname: C{string}
        @param authorname: name of the author (if any) as 
            entered by the user
        @type authorname: C{string}
        '''
        pluginidtokens = {}
        pluginidtokens[''] = str(pluginid)
        pluginidtokens['entered'] = pluginidtokens['']
        self.tokentable['id'] = pluginidtokens
        pluginnametokens = {}
        pluginnametokens[''] = pluginname
        pluginnametokens['entered'] = pluginname
        pluginnametokens['cleaned'] = TextFX.sanitize(
            pluginname, safechar='', 
            replaceumlaut=True, 
            replacediacritic=True, 
            replacegreek=True, 
            allowedchars=' ')
        pluginnametokens['identifier'] = TextFX.tocamelcase(pluginnametokens['cleaned'], True)
        pluginnametokens['uppercaseidentifier'] = TextFX.tocamelcase(pluginnametokens['cleaned'], True).upper()
        pluginnametokens['abbreviation'] = TextFX.abbreviate(pluginnametokens['cleaned'], 6)
        self.tokentable['pluginname'] = pluginnametokens
        authornametokens = {}
        if authorname is None:
            _authorname = self._getauthorname()
        else:
            _authorname = authorname
        if _authorname:
            authornametokens[''] = _authorname
            authornametokens['entered'] = _authorname
            authornametokens['cleaned'] = TextFX.sanitize(
                _authorname, safechar='', 
                replaceumlaut=True, 
                replacediacritic=True, 
                replacegreek=True, 
                allowedchars=' ')
            authornametokens['identifier'] = TextFX.tocamelcase(_authorname, True)
            authornametokens['abbreviation'] = TextFX.abbreviate(_authorname, 6)
            self.tokentable['authorname'] = authornametokens
        orgnametokens = {}
        if orgname is not None:
            orgnametokens[''] = orgname
            orgnametokens['entered'] = orgname
            orgnametokens['cleaned'] = TextFX.sanitize(
                orgname, safechar='', 
                replaceumlaut=True, 
                replacediacritic=True, 
                replacegreek=True, 
                allowedchars=' ')
            orgnametokens['identifier'] = TextFX.tocamelcase(orgname, True)
            orgnametokens['abbreviation'] = TextFX.abbreviate(orgname, 6)
            self.tokentable['orgname'] = orgnametokens
        datetokens = {}
        datetokens[''] = time.strftime('%Y%m%d')
        datetokens['isoseparated'] = time.strftime('%F')
        datetokens['iso'] = TextFX.sanitize(datetokens['isoseparated'], safechar='', allowedchars='')
        datetokens['englishseparated'] = time.strftime('%D').replace('/', '-')
        datetokens['english'] = TextFX.sanitize(datetokens['englishseparated'], safechar='', allowedchars='')
        datetokens['localeseparated'] = time.strftime('%x')
        datetokens['locale'] = TextFX.sanitize(datetokens['localeseparated'], safechar='', allowedchars='')
        datetokens['nameofday'] = time.strftime('%A')
        datetokens['shortnameofday'] = time.strftime('%a')
        self.tokentable['date'] = datetokens
        timetokens = {}
        timetokens[''] = TextFX.sanitize(time.strftime('%X'), safechar='', allowedchars='')
        timetokens['localeseparated'] = time.strftime('%X')
        timetokens['locale'] = TextFX.sanitize(timetokens['localeseparated'], safechar='', allowedchars='')
        timetokens['englishseparated'] = time.strftime('%r')
        timetokens['english'] = TextFX.sanitize(timetokens['englishseparated'], safechar='', allowedchars='')
        timetokens['secondssinceepoch'] = time.strftime('%s')
        self.tokentable['time'] = timetokens
    
    def fillruleslist(self, rulesfilepath):
        '''
        Parse and evaluate rules.py from the sourcedata dir.
        
        rules.py contains a mapping of search terms to replacement terms,
        on one line each and separated by the regex '\s*=\s*'. The search
        term is found first and then the replacement term follows. 
        
        @param rulesfilepath: path to rules.py
        @type rulesfilepath: C{string}
        '''
        rulesfilepath = os.path.abspath(rulesfilepath)
        rules = []
        firstline = True
        lineno = 0
        if os.path.exists(rulesfilepath):
            with codecs.open(rulesfilepath, encoding='utf-8') as rulesfile:
                lineno += 1
                for line in rulesfile:
                    if line[0] == '#':
                        if firstline:
                            # process initialization line
                            try:
                                mat = re.search(FolderStructure.INITREGEX, line.strip())
                                if mat:
                                    modules = mat.group('modules')
                                    modules = modules.split(',')
                                    for module in modules:
                                        module = module.strip()
                                        if verbose > 0:
                                            print "Importing '%s'" % module
                                        exec "import %s" % module # IGNORE:W0122
                            except Exception, e: # IGNORE:W0703
                                print "E: initialiation: %s" % e
                            firstline = False
                        else:
                            # ordinary comment
                            continue
                    else:
                        # no comment
                        try:
                            search, replace = re.split(FolderStructure.KVSPLITREGEX, line)
                            rules.append((eval(search), eval(replace)))
                        except Exception, e: # IGNORE:W0703
                            print "E: bogus value at line %d: %s" % (lineno, e)
                            continue
            self.ruleslist = rules
        else:
            raise CLIError("Rules file not found at path '%s'" % rulesfilepath)
        return len(rules)
    
    def _processname(self, dirpath, fileordirname, force):
        filepath = os.path.join(dirpath, fileordirname)
        filename, fileext = os.path.splitext(fileordirname)
        matchedtokens = re.findall(FolderStructure.TOKENREGEX, filename)
        newpath = None
        if len(matchedtokens) > 0:
            newname = ''
            for mat in matchedtokens:
                if 'As' in mat:
                    mat = mat.split('As')
                    token = mat[0].lower()
                    form = mat[1].lower()
                else:
                    token = mat.lower()
                    form = ''                    
                newname += self.tokentable[token][form]
            newname += fileext
            newpath = os.path.join(dirpath, newname)
        if newpath:
            if os.path.exists(newpath):
                if force:
                    os.remove(newpath)
                else:
                    if verbose > 0:
                        print "E: File at '%s' exists. Skipping...\nUse -f/--force to overwrite." % newpath
                    return False
            if verbose > 0:
                print "  Renaming '%s' to '%s'" % (fileordirname, newname)
            os.rename(filepath, newpath)
        return True
    
    def processnames(self, force=False):
        '''
        Replace magic tokens in file and dir names.
        
        A magic token has the form C{<Value>} or C{<ValueAsForm>} where
        C{Value} is the value of an entry in the token table and C{Form} 
        a conjugate of that value. E.g. C{Value} might be "PluginName" 
        which would result in the plugin's name as entered by the user.
        C{PluginNameAsIdentifier} is C{PluginName} taking the form of an 
        C{Identifier}, meaning it has invalid characters replaced, 
        spaces stripped and is generally in I{CamelCase} form. There are
        multiple such forms. For a rundown use L{printtokentable()}.
        
        @param force: if True, rename a file or dir even if it would 
            replace an already existing file or dir.
        @type force: C{bool}
        '''
        if not self.dir:
            raise RuntimeError('E: self.dir cannot be None. Set dir via self.setrootdir() first.')
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for somedir in dirnames:
                self._processname(dirpath, somedir, force)
            for somefile in filenames:
                if somefile in FolderStructure.HIDDENFILES:
                    continue
                self._processname(dirpath, somefile, force)
        return True
    
    def _processcontent(self, dirpath, filename):
        filepath = os.path.join(dirpath, filename)
        if filename in FolderStructure.HIDDENFILES:
            return False
        if os.path.exists(filepath) and len(self.ruleslist) > 0:
            if verbose > 0:
                print "Processing '%s'" % filepath
            #with codecs.open(filepath, 'rw', encoding='utf-8', buffering=0) as curfile:
            #    for line in curfile:
            #        for search, replace in self.ruleslist:
            #            if re.search(search, line):
            #                curfile.write(re.sub(search, replace, line))
            for line in fileinput.input(filepath, inplace=1):
                replaceline = line
                matches = re.findall(FolderStructure.TOKENREGEX, line)
                if len(matches) > 0:
                    for mat in matches:
                        if 'As' in mat:
                            _mat = mat.split('As')
                            token = _mat[0].lower()
                            form = _mat[1].lower()
                        else:
                            token = mat.lower()
                            form = ''
                        try:
                            replace = self.tokentable[token][form]
                            replaceline = re.sub("<%s>" % mat, replace, replaceline, flags=re.UNICODE)
                        except KeyError:
                            # can't use "print" here, since it would end up in the written replaceline
                            pass
                for search, replace in self.ruleslist:
                    if re.search(search, line):
                        replaceline = re.sub(search, replace, replaceline, flags=re.UNICODE)
                # Using the fileinput module, we can perform inplace replacement 
                # of lines as they are parsed. This is done by re-routing stdout, 
                # so if we use the print statement it is going to end up in the 
                # processed file.
                print replaceline,
        return True
        
    def processcontents(self):
        '''Replace tokens in file contents based on rules.py'''
        for dirpath, dirnames, filenames in os.walk(self.dir): # IGNORE:W0612 #@UnusedVariable
            for somefile in filenames:
                self._processcontent(dirpath, somefile)
        return True
    
    
def main(argv=None): # IGNORE:C0111
    if isinstance(argv, list):
        sys.argv.extend(argv)
    
    program_name = "c4dplugwiz" # IGNORE:W0612 @UnusedVariable
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = '''c4dplugwiz -- CINEMA 4D Python plugin wizard'''
    program_license = u'''%s
    
  Created by André Berg on %s.
  Copyright 2011 Berg Media. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        # flags (optional)
        parser.add_argument('-l', '--listtokens', dest='listtokens', action="store_true", help="list available tokens and variations and exit.")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-f', '--force', dest='overwrite', action="store_true", help="overwrite existing target folders [default: %(default)s]")
        parser.add_argument('-c', '--createdir', dest='createdir', action="store_true", help="create dir at destination path if it doesn't exist [default: %(default)s]")
        parser.add_argument('-t', '--type', dest="typ", help="the type of plugin to create. Determines which subfolder is used from the sourcedata dir [default: %(default)s]")
        parser.add_argument('-s', '--sourcedata', dest='src', help="path to dir with source folder structures. Must have one folder structure per plugin type. You can also set the environment variable 'C4DPLUGWIZ_DATA'. [default: %(default)s]")
        parser.add_argument('-a', '--author', dest='author', help="name of the plugin author to be used in file/dir name replacements. You can also set the environment variable 'C4DPLUGWIZ_AUTHORNAME'. [default: %(default)s]")
        parser.add_argument('-o', '--org', dest='org', help="name of the organization the author belongs to, used for file/dir name replacements. You can also set the environment variable 'C4DPLUGWIZ_ORGNAME'. [default: %(default)s]")
        # positional arguments (required)
        parser.add_argument(dest="id", help="unique ID of the plugin (obtained from PluginCafe)", metavar="id")
        parser.add_argument(dest="name", help="name of the plugin.", metavar="name")
        parser.add_argument(dest="paths", help="paths to destination folder(s)", metavar="paths", nargs='+')
        
        # Environment variable defaults
        if os.environ.has_key('C4DPLUGWIZ_DATA'):
            defaultsource = os.environ['C4DPLUGWIZ_DATA']
        else:
            defaultsource = os.path.join(os.curdir, "c4dplugwiz_data")
        if os.environ.has_key('C4DPLUGWIZ_AUTHORNAME'):
            defaultauthor = os.environ['C4DPLUGWIZ_AUTHORNAME']
        else:
            defaultauthor = None
        if os.environ.has_key('C4DPLUGWIZ_ORGNAME'):
            defaultorg = os.environ['C4DPLUGWIZ_ORGNAME']
        else:
            defaultorg = None

        parser.set_defaults(src=defaultsource, typ="commandplugin", author=defaultauthor, org=defaultorg, verbose=0)
        
        # Process arguments
        args = parser.parse_args()
        
        global verbose # IGNORE:W0601
        
        verbose = args.verbose
        listtokens = args.listtokens
        paths = args.paths
        pluginid = args.id
        name = args.name
        typ = args.typ
        sourcedatapath = args.src
        overwrite = args.overwrite
        createdir = args.createdir
        author = args.author
        org = args.org
        
        source = os.path.join(sourcedatapath, typ)
        rulesfilepath = os.path.join(sourcedatapath, 'rules.py')

        if verbose > 0:
            print "Verbose mode on"
            print "Plugin %s: '%s'" % (pluginid, name)
            print            

        if not os.path.exists(sourcedatapath):
            raise CLIError("sourcedata path doesn't exist ('%s')" % sourcedatapath)
        if not os.path.exists(source):
            raise CLIError("couldn't find a folder structure for plugin type '%s' at '%s'" % (typ, source))
        
        for destpath in paths:
            if verbose > 0:
                print "Processing destination '%s' ..." % destpath
                print "  Using source data at '%s'" % sourcedatapath
                print "Using folder structure '%s'" % source
                print
                
            absdestpath = os.path.abspath(destpath)
            fulldestpath = os.path.join(absdestpath, typ)
            namedfulldestpath = os.path.join(absdestpath, name)
            destparentdir, destdir = absdestpath, typ # IGNORE:W0612 #@UnusedVariable
            
            if not os.path.exists(destparentdir):
                if createdir:
                    du.mkpath(destparentdir, 0755)
                    if not os.path.exists(destparentdir):
                        raise CLIError("creating parent dir for destination '%s'  failed. skipping..." % destpath)
                else:
                    raise CLIError("destination '%s' doesn't exist. skipping..." % destpath)
            
            # Steps (needed to re-order them a little)

            fs = FolderStructure()
            
            # 2a. Pre-process tokens and rules.py
            fs.filltokentable(pluginid, name, author, org)
            
            if listtokens:
                # print token list to stdout and exit
                fs.printtokentable()
                return 0
            
            fs.fillruleslist(rulesfilepath)
                        
            # 1. Copy folder structure(s)
            if overwrite and os.path.exists(namedfulldestpath):
                if verbose > 0:
                    print "Overwriting dir at '%s'" % namedfulldestpath
                du.copy_tree(source, namedfulldestpath, verbose=verbose)
            else:
                try:
                    su.copytree(source, namedfulldestpath)
                except OSError, e:
                    if 'exists' in str(e):
                        raise CLIError("Dir exists: '%s'\nUse -f/--force to overwrite" % fulldestpath)          

            fs.setrootdir(namedfulldestpath)
            # 2b. Do file name replacement
            fs.processnames(force=overwrite)
            
            # 3. Do file content replacement
            fs.processcontents()
            
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except CLIError, e:
        print e
        return 1
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + unicode(e).decode('unicode_escape')
        print >> sys.stderr, "\t for help use --help"
        return 2

if __name__ == "__main__":
    '''Command line options.''' # IGNORE:W0105
    if DEBUG:
        #print TextFX.sanitize(u'äÄÖndréRülΩçœ', replaceumlauts=True, replacediacritics=True, replacegreek=True)
        os.environ['C4DPLUGWIZ_DATA'] = "../unittests/data"
        #os.environ['C4DPLUGWIZ_AUTHORNAME'] = u"André Berg"
        os.environ['C4DPLUGWIZ_ORGNAME'] = "Berg Media"
        plugintype = "tagplugin"
        #sys.argv.append("-h")
        #sys.argv.append("-l")
        sys.argv.append("-v")
        sys.argv.append("-c")
        sys.argv.append("-t")
        sys.argv.append(plugintype)
        sys.argv.append("-f")
        sys.argv.append("1000001")
        sys.argv.append("Andre's Super Plugin")
        sys.argv.append("./testrun")
        #sys.argv.append("./testrun2")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        os.environ['C4DPLUGWIZ_DATA'] = "../unittests/data"
        os.environ['C4DPLUGWIZ_AUTHORNAME'] = u"Andre Berg"
        os.environ['C4DPLUGWIZ_ORGNAME'] = "Berg Media"
        profile_filename = 'c4dplugwiz_profile.pstats'
        cProfile.run('main(["-v", "-c", "--type=tagplugin", "-f", "1000001", "My Plugin", "./testrun"])', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        print >> statsfile, stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())