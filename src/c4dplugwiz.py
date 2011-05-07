#!/usr/local/bin/python2.7
# encoding: utf-8
# pylint: disable-msg=W0603
'''
B{c4dplugwiz -- CINEMA 4D Python plugin wizard}

c4dplugwiz is a command line tool and a template system 
that helps with creating python plugins for CINEMA 4D. 
It works by copying pre-existing folder structures from
a data repository to a destination specified by the user.

Definition
==========

A I{wizard} or I{assistant} is defined to be any process
that is helpful in some creational undertaking, providing
means to a customizable starting point and easing the user 
into the next steps towards some goal.

Here, the goal is the creation of Python plugins, and the 
means are blueprint folder structures with files, utilizing
a magic token and rules based templating system. 
Embedding tokens and search terms within the contents and 
names of files will then result in text replacements with 
the token's or search term's associated value. 

How It Works
============

First, copy the corresponding blueprint folder structure 
from a source repository to a destination folder (there can
be multiple destination folders). Then, process any template
tokens. This is divided into 2 steps:

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

Currently, the following data points can be used:
 
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
modules to import. Each of these lines must have the following 
syntax: C{# import module1,module2,module3 ...} and so on
(the ellipsis not being part of the syntax). 

Lines in C{rules.py} other than the initialization line starting 
with the hash character are considered comments and ignored, as
well as lines that do not have a format of C{<I{key}>\s*=\s*<I{value}>}
where C{<I{...}>} stands for a variable term and C{\s*} stands for zero
or more spaces. 

Tips For Creating The Rules File
================================

If you need a value for a key to span multiple lines, assign the 
value in I{raw text} form, e.g. between single, double or tripple 
quotes and with carriage returns, linefeeds etc. escaped. 

Also, if you expect to make full use of non-ASCII characters, such 
as accented e's or umlauts, keep in mind that you must define them 
in C{rules.py} as unicode string (C{u'...'}) and set an encoding
comment at the very beginning (e.g. C{# coding: utf-8}). The same 
goes for the strings in the templated file where the unicode value
should be inserted: these must be unicode strings too and the file
also needs a coding comment at the top. 


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
import unicodedata as ud

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from distutils import dir_util as du
from subprocess import Popen, PIPE
import shutil as su
import codecs

__all__ = ['FolderStructure', 'TextFX']
__version__ = 0.4
__date__ = '2011-04-30'
__updated__ = '2011-05-05'

DEBUG = 1
TESTRUN = 1
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
    '''Methods for processing and transforming text.'''
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
        
    @staticmethod
    def precompunicode(word, canonical=True):
        '''
        Precompose Unicode character sequences, using either canonical 
        or nominal mapping. 
        E.g. C{LATIN SMALL LETTER E} (C{U+0065}) + C{COMBINING ACUTE ACCENT} (C{U+0301}) 
        becomes C{LATIN SMALL LETTER E WITH ACUTE} (C{U+00E9}). 
        
        @param word: the unicode word to preccompose
        @type word: C{unicode}
        @param canonical: if C{True} combining diacritical marks 
            will be mapped to their non-combining forms when they 
            cannot be combined with the letter preceeding the position.
        @type canonical: C{bool}
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
    def decompunicode(word, canonical=True):
        '''
        Decompose Unicode character sequences using either canonical 
        or nominal mapping. 
        E.g. C{LATIN SMALL LETTER E WITH ACUTE} (C{U+00E9}) becomes 
        C{LATIN SMALL LETTER E} (C{U+0065}) + C{COMBINING ACUTE ACCENT} (C{U+0301}). 
        
        @param word: the unicode word to decompose
        @type word: C{unicode}
        @param canonical: if C{True} non-combining diacritical marks 
            will be mapped to their combining forms and maybe combined 
            with the letter preceeding the position.
        @type canonical: C{bool}
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
        u'''
        Convert 'word' to CamelCase.
        Examples: 
        
        >>> TextFX.tocamelcase('hot flaming cats')
        'HotFlamingCats'
        >>> TextFX.tocamelcase('HotFlamingCats')
        'HotFlamingCats'
        >>> TextFX.tocamelcase('hotFlamingCats')
        'HotFlamingCats'
        >>> TextFX.tocamelcase('hot_flaming_cats')
        'HotFlamingCats'
        >>> TextFX.tocamelcase('Hot Flaming _ Cats')
        'HotFlamingCats'
        >>> print TextFX.tocamelcase(u'höt_fläming_cäts', False)
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
        word = re.sub(ur'_+([^_]+)', __capitalizematch, word, re.UNICODE)
        word = re.sub(ur' ([^ ]+)', __capitalizematch, word, re.UNICODE)
        word = re.sub(' ', '', word, re.UNICODE)
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
        'ASPS'
        
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
    def sanitize(word, safechar='_', replaceumlauts=False, replacediacritics=False, replacegreek=False, allowedchars='_\-()'):
        u'''
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
        
        Examples:
        
        >>> TextFX.sanitize(u'Äsbëst-Shop')
        u'_sb_st-Shop'
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='')
        u'sbst-Shop'
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='', replaceumlauts=True)
        u'Aesbst-Shop'
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='', replaceumlauts=True, replacediacritics=True)
        u'Aesbest-Shop'
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='', replaceumlauts=True, replacediacritics=True, allowedchars='')
        u'AesbestShop'
                        
        @param word: the word to sanitize
        @type word: C{string}
        @param safechar: the char to use for replacing non-allowed chars
        @type safechar: C{string}
        @param replaceumlauts: 
            if True, replace umlauts like 'ä' with a phonetic 
            equivalent like 'ae'.
        @type replaceumlauts: C{bool}
        @param replacediacritics: 
            if True, replace diacritics with a decomposed 
            form where the mark is dropped (e.g. 'ç' becomes 'c')
        @type replacediacritics: C{bool}
        @param replacegreek: 
            if True, replace greek letters with their 
            translitterated name, e.g. 'π' becomes 'pi'.
        @type replacegreek: C{bool}
        @param allowedchars: string of chars to allow unchanged 
            (note: the string is used within a regex)
        @type allowedchars: C{string}
        '''
        word = re.sub(' ', safechar, word)
        if replaceumlauts:
            temp = u''
            for c in word:
                if c in TextFX.phoneticumlauts:
                    temp += TextFX.phoneticumlauts[c]
                else:
                    temp += c
            word = temp
        if replacediacritics:
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
    
    Provides methods for replacements in the names and 
    contents of files contained within a folder structure.
    '''
    tokencharstart  = '<'
    tokencharend    = '>'
    tokenregex      = re.compile(r'%s(?P<token>\w+?)%s' % (tokencharstart, tokencharend))
    tokenxformregex = re.compile(r'%s(?P<token>\w+?)As(?P<form>\w+?)%s' % (tokencharstart, tokencharend))
    initregex       = re.compile(r'#\s*import (?P<modules>[\w, ]+)')
    kvsplitregex    = re.compile(r'\s*=\s*')
    hiddenfiles     = ['.DS_Store', 'desktop.ini']
    
    def __init__(self):
        super(FolderStructure, self).__init__()
        self.dir = None
        self.tokentable = {}
        self.ruleslist = []
        self.rulesfilepath = None
        self.dir = None

    def initialize(self, rootdir, rulesfilepath):
        '''
        Set C{self.dir} to C{rootdir} to be used in processing later on.
        @param rootdir: an existing directory relative to C{os.curdir} 
            or as absolute path
        @type rootdir: C{string}
        @param rulesfilepath: path to rules.py
        @type rulesfilepath: C{string}
        '''
        absrootdir = os.path.abspath(rootdir)
        if os.path.exists(absrootdir):
            self.dir = absrootdir
        else:
            raise CLIError("Destination root not found at path '%s'" % absrootdir)
        rulesfileabspath = os.path.abspath(rulesfilepath)
        if os.path.exists(rulesfileabspath):
            self.rulesfilepath = rulesfileabspath
        else:
            raise CLIError("Rules file not found at path '%s'" % rulesfileabspath)
        self._fillruleslist()
        
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
                    import win32api # IGNORE:F0401 @UnresolvedImport
                    fulluser = win32api.GetUserName()
                result = fulluser.strip() # IGNORE:E1103
            except Exception, e:
                raise CLIError(e)
        return result
    
    def printtokentable(self, indent=3):
        '''
        Print data entries of the token table, including forms.
        
        @param indent: how many spaces for indentation
        @type indent: C{int}
        '''
        spaces = " " * indent
        spaces2 = spaces + spaces
        print "Listing token table..."
        print
        print "Format:"
        print "%sdatum\n%sform1\n%sform2\n%s..." % (spaces, spaces2, spaces2, spaces2)
        print "Usage:"
        print "%sDatum" % (spaces)
        print "%sDatumAsForm1" % (spaces)
        print "%sDatumAsForm2" % (spaces)
        for k, v in self.tokentable.iteritems():
            print 
            print "%s" % k,
            print
            for entry in v:
                print "%s%s" % (spaces, entry)
        return True
         
    def filltokentable(self, pluginid, pluginname, authorname, orgname):
        '''
        Create and fill table of angle bracket C{<...>} based magic tokens.
        
        Angle bracket based tokens are tokens where the value
        can be deferred automatically (to a degree), with as little 
        user intervention as possible.
        
        Examples are date, time and author name determined
        from the logon environment.
        
        The table consists of a dict of metadata dicts, 
        the latter of which can have multiple entries,
        one for each form the datum can be in. E.g. if
        the datum is C{AuthorName}, it can have a form as
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
            replaceumlauts=True, 
            replacediacritics=True, 
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
                replaceumlauts=True, 
                replacediacritics=True, 
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
                replaceumlauts=True, 
                replacediacritics=True, 
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
    
    def _fillruleslist(self):
        '''
        Parse the rules file and build the rules list.
        
        C{rules.py} contains a mapping of search terms to replacement terms,
        on one line each and separated by the regex C{\s*=\s*}. The search
        term comes first and then the replacement term follows. 
        '''
        rulesfileabspath = os.path.abspath(self.rulesfilepath)
        rules = []
        lineno = 0
        with codecs.open(rulesfileabspath, encoding='utf-8') as rulesfile:
            for line in rulesfile:
                lineno += 1
                if len(str(line)) == 0:
                    # empty line
                    continue
                elif line[0] == '#':
                    mat = re.search(FolderStructure.initregex, line.strip())
                    if mat:
                        # import line
                        try:
                            modules = mat.group('modules')
                            modules = modules.split(',')
                            for module in modules:
                                module = module.strip()
                                if verbose > 0:
                                    print "Importing '%s'" % module
                                exec "import %s" % module # IGNORE:W0122
                        except Exception, e: # IGNORE:W0703
                            print "E: initialiation: %s" % e
                    else:
                        # comment
                        continue
                else:
                    # search replace mapping
                    try:
                        if re.search(FolderStructure.kvsplitregex, line):
                            search, replace = re.split(FolderStructure.kvsplitregex, line)
                            rules.append((eval(search), eval(replace)))
                    except Exception, e: # IGNORE:W0703
                        print "E: at line %d: %s" % (lineno, e)
                        continue
        self.ruleslist = rules
        return len(rules)
    
    def _processname(self, dirpath, fileordirname, force):
        filepath = os.path.join(dirpath, fileordirname)
        filename, fileext = os.path.splitext(fileordirname)
        newpath = None
        newname = None
        # process rules
        replaced = False
        for search, replace in self.ruleslist:
            if re.search(search, filename):
                filename = re.sub(search, replace, filename, flags=re.UNICODE)
                replaced = True
        if replaced:
            newname = filename + fileext
            newpath = os.path.join(dirpath, newname)
            replaced = False
        # process tokens
        matchedtokens = re.findall(FolderStructure.tokenregex, filename)
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
        # do the actual renaming (if needed)
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
        Do magic token and rule based replacements in file and dir names.
        
        A magic token has the form C{<Value>} or C{<ValueAsForm>} where
        C{Value} is the value of an entry in the token table and C{Form} 
        a conjugate of that value. E.g. C{Value} might be C{PluginName} 
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
        rulesfilename = os.path.basename(self.rulesfilepath)
        try:
            os.remove(os.path.join(self.dir, rulesfilename))
        except OSError:
            pass
        for dirpath, dirnames, filenames in os.walk(self.dir):
            for somedir in dirnames:
                self._processname(dirpath, somedir, force)
            for somefile in filenames:
                if somefile in FolderStructure.hiddenfiles:
                    continue                    
                self._processname(dirpath, somefile, force)
        return True
    
    def _processcontent(self, dirpath, filename):
        filepath = os.path.join(dirpath, filename)
        if filename in FolderStructure.hiddenfiles:
            return False
        if os.path.exists(filepath) and len(self.ruleslist) > 0:
            if verbose > 0:
                print "Processing '%s'" % filepath
            # rename this file to filename.bak
            backupfilename = '%s%s%s' % (filename, os.extsep, "bak")
            backupfilepath = os.path.join(dirpath, backupfilename)
            # remove filename.bak from last run if it is present
            try: 
                os.remove(backupfilepath)
            except OSError: 
                pass
            os.rename(filepath, backupfilepath)
            with codecs.open(filepath, mode='w', encoding='utf-8') as processedfile:
                # then open a new file with this file's old name (w/o ".bak")
                # where we can write the processed lines to
                with codecs.open(backupfilepath, mode='r', encoding='utf-8') as curfile:
                    for line in curfile:
                        replaceline = line
                        matches = re.findall(FolderStructure.tokenregex, line)
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
                        processedfile.write(replaceline)
            # done with the backup file, remove it
            os.remove(backupfilepath)
        return True
        
    def processcontents(self, exclude=None):
        '''
        Replace tokens in file contents based on rules.py
        
        @param exclude: if filename (incl. ext) matches this regex, 
                        the file is excluded from being processed
        @type exclude: C{string}
        '''
        for dirpath, dirnames, filenames in os.walk(self.dir): # IGNORE:W0612 #@UnusedVariable
            for somefile in filenames:
                if exclude and re.match(exclude, somefile, re.UNICODE):
                    continue
                self._processcontent(dirpath, somefile)
        return True
    
def _system(cmd, args=None):
    '''
    Replacement for `cmd` statements.
    
    @param cmd: a shell command line
    @type cmd: C{string}
    @param args: a list of arguments that 
                 will be expanded in cmd 
                 starting with $0
    @type args: C{list}
    '''
    if args is None:
        args = [cmd]
    else:
        args = [cmd]+args
    out, err = Popen(args, stdout=PIPE, shell=True).communicate()
    return (out, err)
    
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

''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        # flags (optional)
        parser.add_argument('-l', '--listtokens', dest='listtokens', action="store_true", help="list available tokens + forms and exit.")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-f', '--force', dest='overwrite', action="store_true", help="overwrite existing target folders [default: %(default)s]")
        parser.add_argument('-c', '--createdir', dest='createdir', action="store_true", help="create destination path if it doesn't exist [default: %(default)s]")
        parser.add_argument('-t', '--type', dest="typ", help="type of plugin to create. Determines which subfolder is used from the sourcedata dir [default: %(default)s]")
        parser.add_argument('-s', '--sourcedata', dest='src', help="path to dir with source folder structures. Must have one folder structure per plugin type. You can also set the environment variable 'C4DPLUGWIZ_DATA'. [default: %(default)s]")
        parser.add_argument('-r', '--rulesfile', dest='rulesfile', metavar='str', help="rules file name. If None, looks for a file 'rules.py' local to each plugin type's folder structure. If this is None, falls back to looking in the sourcedata dir. [default: %(default)s]")
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
        rulesfile = args.rulesfile

        if verbose > 0:
            print "Verbose mode on"
            print "Plugin %s: '%s'" % (pluginid, name)
            print     

        source = os.path.join(sourcedatapath, typ)

        # precedence for rules file:
        # 1. path supplied by CLI arg
        # 2. per plugin type (local)
        # 3. per sourcedata dir (global)
        if rulesfile and os.path.exists(rulesfile):
            rulesfilepath = rulesfile
        else:
            rulesfile = 'rules.py'
            rulesfilepath = os.path.join(sourcedatapath, typ, rulesfile)
            if not os.path.exists(rulesfilepath):
                rulesfilepath = os.path.join(sourcedatapath, rulesfile)      

        if not os.path.exists(sourcedatapath):
            raise CLIError("sourcedata path doesn't exist ('%s')" % sourcedatapath)
        if not os.path.exists(source):
            raise CLIError("couldn't find a folder structure for plugin type '%s' at '%s'" % (typ, source))

        if verbose > 0:
            print "  Using source data at '%s'" % sourcedatapath
            print "Using folder structure '%s'" % source
            print "      Using rules from '%s'" % rulesfilepath
            print
                        
        for destpath in paths:
            if verbose > 0:
                print "Processing destination '%s' ..." % destpath
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
                
            # Steps
            fs = FolderStructure()
            
            # 1. Create and fill token table
            fs.filltokentable(pluginid, name, author, org)
            if listtokens:
                # print token table to stdout and exit
                fs.printtokentable()
                return 0
                                    
            # 2. Copy folder structure(s)
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

            # Initialize the folder structure. This:
            # a) checks if the root destination and rules.py exist
            # b) processes rules.py and creates and fills the rules list
            fs.initialize(namedfulldestpath, rulesfilepath)

            # 3. Do file name replacements
            fs.processnames(force=overwrite)
            
            # 4. Do file content replacements
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
    if TESTRUN:
        import doctest
        doctest.testmod()
    if DEBUG:
        _system('rm -rfv ./testrun')
        #os.environ['C4DPLUGWIZ_DATA'] = "../unittests/data"
        os.environ['C4DPLUGWIZ_AUTHORNAME'] = "Andre Berg"
        os.environ['C4DPLUGWIZ_ORGNAME'] = "Berg Media"
        plugintype = "tagplugin"
        main(["-v", "-c", "--type=%s" % plugintype, "-f", "1000002", "Andre's Super Plugin", "./testrun"])
        main(['-l'])
        main(['-h'])
        sys.exit(0)
    if PROFILE:
        import cProfile
        import pstats
        _system('rm -rfv ./testrun')
        os.environ['C4DPLUGWIZ_DATA'] = "../unittests/data"
        os.environ['C4DPLUGWIZ_AUTHORNAME'] = "Andre Berg"
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