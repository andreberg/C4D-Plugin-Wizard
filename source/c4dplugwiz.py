#!/usr/local/bin/python
# encoding: utf-8
# pylint: disable-msg=W0603,W0212,W0702,W0703
ur'''\
**c4dplugwiz** is a command line tool and a template system 
that helps with creating python plugins for CINEMA 4D. 
It works by copying pre-existing folder structures from
a data repository to a destination specified by the user.

Definition
----------

A *wizard* or *assistant* is defined to be any process
that is helpful in some creational undertaking, providing
means to a customizable starting point and easing the user 
into the steps towards some goal.

Here, the goal is the creation of Python plugins, and the 
means are blueprint folder structures. The files of which, 
embed within their contents special text that is utilized 
from a magic token and rules based templating system. 

A *blueprint folder structure* is defined to be a collection
of directories and files representing one type of plugin that
can be created, e.g. tag plugin, command plugin, etc...
While there usually is a predetermined layout of directories
and subdirectories for each plugin type (see Py4D docs), the 
contents of any enclosed files can be determined by the user.
 
The *source repository* is defined to be the path to the parent
folder that contains all blueprint folder structures.

How It Works
------------

The user supplies the following data:

    * plugin ID
    * plugin name
    * destination path(s)
    * author name (optional - see CLI args)
    * org name (optional - see CLI args)

Processing is then divided into 3 main steps:

    1. Copy blueprint folder structure to destination
    2. Perform text replacements in file and directory names
    3. Perform text replacements in file contents

1) First, copy the blueprint folder structure corresponding to
the specified plugin type from the source repository to a destination 
folder (there can be multiple destinations). 

2) Then, loop through the directories and files of the copied
folder structure and perform text replacements of magic tokens
and search terms found within the file and directory names.

3) Finally, parse the contents of each file within the copied 
folder structure and perform magic token and rule based text 
replacements.

Text Replacements
-----------------

There are two systems for replacing text:

    1. magic tokens
    2. search/replace rules

Magic Tokens
~~~~~~~~~~~~

A magic token is denoted by the syntax ``%!Datum!%``, where
``Datum`` is a variable term referring to one piece of data,
called a datum point. Datum points are generally concerned with
project relevant metadata (who, what, when - plugin id/name, 
author/org, date/time). 

Magic tokens can also have alternate forms, which insert a variation
of the replacement text. The syntax for this is ``%!DatumAsForm!%``. 
Note the adverb ``As`` (case sensitive!), which is used as a separator 
between the datum point and its form.

For example, if the datum point ``%!PluginName!%`` is found it will
be replaced by the name of the plugin as supplied by the user.
If the alternate form ``%!PluginNameAsIdentifier!%`` is found, the
name of the plugin as entered by the user will be sanitized for
illegal characters and transformed to *CamelCase* format.

There are a fixed number of variations per datum point and to find 
out about those, pass the ``-l/--list-tokens`` flag to the CLI.
 
Currently, the following datum points can be used:
 
    - ``ID``            *supplied by user with a CLI argument*
    - ``PluginName``    *supplied by user with a CLI argument*
    - ``AuthorName``    *supplied by user with a CLI option, or an environment variable*
    - ``OrgName``       *supplied by user with a CLI option, or an environment variable*
    - ``Date``          *constructed from ``time.strftime()*``
    - ``Time``          *constructed from ``time.strftime()*``
    - ``DateTime``      *constructed from ``time.strftime()*``
    
Note: datum point names are case sensitive!

If a datum point is used but the corresponding value can't 
be retrieved, an exception is raised to avoid continuing 
with false information. To ensure a value is found for author
and organization names, you can pass the relevant values per 
the CLI or set the environment variables ``C4DPLUGWIZ_AUTHORNAME`` 
and ``C4DPLUGWIZ_ORGNAME`` respectively.


Search/Replace Rules
--------------------

Search/replace rules are specified as ``key = value`` mappings in a 
file called ``rules.py``. There can be multiple rules files at different
locations, but one location will take precendence over the others as 
indicated in the following listing:

With decreasing precedence:

    1. arbitrary file path, passed with ``-r/--rules-file`` CLI argument
    2. at the root level of each blueprint folder structure (*type local*)
    3. at the root level of the source repository (*repository global*)

Keys as well as values must be valid Python statements and can therefore 
include raw regex strings (e.g. ``r'[a-z]'``) and functions calls 
(e.g. ``time.strftime('%Y')``). 

If you need to import additional modules in order to use some 
functionality for keys or values, a special line, called an import line, 
in ``rules.py`` can be used to specify a comma separated list of 
modules to import. Each of these lines must have the following 
syntax: ``# import module1,module2,module3 ...`` and so on
(the ellipsis not being part of the syntax). 

Lines in ``rules.py`` other than an import line starting with the hash 
character are considered comments and ignored, as well as lines that do 
not have a format of ``<key>\s*=\s*<value>`` where ``<...>`` stands 
for a variable term and ``\s*`` stands for zero or more spaces. 

If you need a value for a key to span multiple lines, assign the 
value in *raw text* form, e.g. between single, double or tripple 
quotes and with carriage returns, line feeds etc. escaped. 

Also, if you expect to make full use of non-ASCII characters, such 
as accented e's or umlauts, keep in mind that you must define them 
in ``rules.py`` as unicode string (``u'...'``) and set an encoding
comment at the very beginning (e.g. ``# coding: utf-8``). The same 
goes for the strings in the templated file where the unicode value
should be inserted: these must be unicode strings too and the file
also needs a coding comment at the top. 


:author:     André Berg
             
:copyright:  2013 Sera Media VFX. All rights reserved.
             
:license:    Licensed under the Apache License, Version 2.0 (the "License");\n
             you may not use this file except in compliance with the License.
             You may obtain a copy of the License at
             
             http://www.apache.org/licenses/LICENSE-2.0
             
             Unless required by applicable law or agreed to in writing, software
             distributed under the License is distributed on an **"AS IS"** **BASIS**,
             **WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND**, either express or implied.
             See the License for the specific language governing permissions and
             limitations under the License.

:contact:    seramediavfx@gmail.com
'''
from __future__ import print_function

import sys
import os
import re
import time
import codecs
import shutil as su
import unicodedata as ud

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from subprocess import Popen, PIPE

__all__ = ['PluginWizard', 'TextFX']
__version__ = (0, 5)
__versionstr__ = '.'.join(str(x) for x in __version__)
__date__ = '2011-04-30'
__updated__ = '2013-08-21'


DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)
PROFILE = 0 or ('ProfileLevel' in os.environ and os.environ['ProfileLevel'] > 0)


# GLOBALS

PLUGIN_TYPE_CMD = 'cmdplugin'
PLUGIN_TYPE_TAG = 'tagplugin'
PLUGIN_ID_TESTING = 1000001


DEFAULT_ENV_AUTHOR = 'C4DPLUGWIZ_AUTHORNAME'
DEFAULT_ENV_ORG = 'C4DPLUGWIZ_ORGNAME'
DEFAULT_ENV_DATA = 'C4DPLUGWIZ_DATA'

DEFAULT_FILE_EXCLUDES = [
    '.DS_Store', 
    '.hotfiles.btree',
    'Thumbs.db',
    'desktop.ini'
]

DEFAULT_DIR_EXCLUDES = [
    '.git',
    '.svn',
    '.hg',
    'CVS',
    '.Trash', 
    '.Trashes', 
    '.fseventsd', 
    '.Spotlight-V100'
]

DEFAULT_EXCLUDES = list(set(DEFAULT_FILE_EXCLUDES).union(set(DEFAULT_DIR_EXCLUDES)))

DEFAULT_DATADIR = 'c4dplugwiz_data'
DEFAULT_RULES_FILENAME = 'rules.py'

g_verbose = 0

# Use this section to set different token chars per OS
# Just beware of illegal characters for the file system
# which are different on Windows and OS X.
#
# Windows can't have: \ / : * ? " < > |
# OS X: can't have : (colon) I believe
#
if 'darwin' in sys.platform:
    # OS X
    g_mts = '%!'    # g_magictoken_start
    g_mte = '!%'    # g_magictoken_end
    g_osx = True
    g_win = False
elif 'win' in sys.platform:
    # Windows
    g_mts = '%!'
    g_mte = '!%'
    g_osx = False
    g_win = True


class CLIError(Exception):
    ''' Generic exception to raise and log fatal errors 
        during command line interface execution.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "%s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


class TextFX(object):
    '''Methods for processing and transforming text.'''
    greek_chars = {
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
        'Omicron':'X',
        'Phi':'F',
        'phi':'f',
        'phiv':'j',
        'Pi':'P',
        'pi':'p',
        'piv':'v',
        'Psi':'Y',
        'psi':'y',
        'rho':'r',
        'Rho':'R',
        'Sigma':'S',
        'sigma':'s',
        'sigmav':'V',
        'tau':'t',
        'Tau':'T',
        'Theta':'Q',
        'theta':'q',
        'thetav':'j',
        'Xi':'X',
        'xi':'x',
        'zeta':'z',
        'Zeta':'Z'
    }
    greek_trans = { # IGNORE:W0109
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
    greek_alphabet = {
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
    phonetic_umlauts = {
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
    def precomp_unicode(word, canonical=True):
        '''
        Precompose Unicode character sequences, using either canonical 
        or nominal mapping. 
        E.g. ``LATIN SMALL LETTER E`` (``U+0065``) + ``COMBINING ACUTE ACCENT`` (``U+0301``) 
        becomes ``LATIN SMALL LETTER E WITH ACUTE`` (``U+00E9``). 
        
        :param unicode word: the unicode word to preccompose
        :param bool canonical: if ``True`` combining diacritical 
            marks will be mapped to their non-combining forms when they 
            cannot be combined with the letter preceeding the position.
        '''
        if not isinstance(word, unicode):
            raise TypeError("E: param 'word': expected unicode, got %s" % type(word))
        result = word
        try:
            if canonical:
                result = ud.normalize('NFKC', word)
            else:
                result = ud.normalize('NFC', word)
        except Exception, e:
            print(e)
            raise e
        
        return result

    @staticmethod
    def decomp_unicode(word, canonical=True):
        '''
        Decompose Unicode character sequences using either canonical 
        or nominal mapping. 
        
        E.g. ``LATIN SMALL LETTER E WITH ACUTE`` (``U+00E9``) becomes 
        ``LATIN SMALL LETTER E`` (``U+0065``) + ``COMBINING ACUTE ACCENT`` (``U+0301``). 
        
        :param unicode word: the unicode word to decompose
        :param bool canonical: if ``True`` non-combining 
            diacritical marks will be mapped to their combining 
            forms and maybe combined with the letter preceeding 
            the position.
        '''
        if not isinstance(word, unicode):
            raise TypeError("E: param 'word': expected unicode, got %s" % type(word))
        result = word
        try:
            if canonical:
                result = ud.normalize('NFKD', word)
            else:
                result = ud.normalize('NFD', word)
        except Exception, e:
            print(e)
            raise e
        
        return result
    
    @staticmethod
    def to_camelcase(word, capitalized=True):
        u'''
        Convert 'word' to CamelCase.
        
        Examples: 
        
        >>> TextFX.to_camelcase('hot flaming cats')
        'HotFlamingCats'
        >>> TextFX.to_camelcase('HotFlamingCats')
        'HotFlamingCats'
        >>> TextFX.to_camelcase('hotFlamingCats')
        'HotFlamingCats'
        >>> TextFX.to_camelcase('hot_flaming_cats')
        'HotFlamingCats'
        >>> TextFX.to_camelcase('Hot Flaming _ Cats')
        'HotFlamingCats'
        >>> print(TextFX.to_camelcase(u'höt_fläming_cäts', False))
        hötFlämingCäts
        
        :param unicode word: the string to convert
        :param bool capitalized: if ``True``, always capitalize 
            the first character of the result.
        '''
        def __capitalizematch(matchobj):
            grp1 = matchobj.group(1)
            if grp1:
                return grp1.capitalize()
            else:
                return matchobj.group(0)
        if word is None or len(word) == 0: return ''
        word = word.strip()
        word = re.sub(ur'_+([^_]+)', __capitalizematch, word, re.UNICODE)
        word = re.sub(ur' ([^ ]+)', __capitalizematch, word, re.UNICODE)
        word = re.sub(' ', '', word, re.UNICODE)
        if capitalized:
            word = '%s%s' % (word[0].upper(), word[1:])
        return word
    
    @staticmethod
    def split_camelcase(word):
        '''
        Split a CamelCaseString into ``['Camel', 'Case', 'String']``.
        
        :param string word: the string to split
        '''
        if word is None or len(word) == 0: return ''
        pat = re.compile(r'[A-Z]+[a-z]*', re.UNICODE)
        return re.findall(pat, word)

    @staticmethod
    def abbreviate(word, maxchars=-1):
        '''
        Reduce some string to an abbreviation of a given length.
        Example:
        
        >>> TextFX.abbreviate('AndisSSuper_PluginSTOP ')
        'ASPS'
        
        :param string word: the string to abbreviate
        :param int maxchars: if > 0, determines length 
            of abbreviation, e.g. with a length of 3, 'ASPS' 
            above becomes 'ASP'.
        '''
        if word is None or len(word) == 0: return ''
        word = word.strip()
        #pat = re.compile(r'\b(\w)', re.UNICODE)
        pat = re.compile(r"([A-Z])[A-Z]*[a-z]*")
        word = re.findall(pat, word)
        if maxchars > 0:
            word = word[0:maxchars]
        return "".join(word)
    
    @staticmethod
    def sanitize(word, safechar='_', 
                 replace_umlauts=False, replace_diacritics=False, 
                 replace_greek=False, allowed_chars=r'_\-()', errors='replace', 
                 encoding="utf-8"):
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
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='', replace_umlauts=True)
        u'Aesbst-Shop'
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='', replace_umlauts=True, replace_diacritics=True)
        u'Aesbest-Shop'
        >>> TextFX.sanitize(u'Äsbëst-Shop', safechar='', replace_umlauts=True, replace_diacritics=True, allowed_chars='')
        u'AesbestShop'
                        
        :param string word: the word to sanitize
        :param string safechar: the char to use for replacing non-allowed chars
        :param bool replace_umlauts: if True, replace umlauts like 'ä' with a 
            phonetic equivalent like 'ae'.
        :param bool replace_diacritics: if True, replace diacritics with a 
            decomposed form where the mark is dropped (e.g. 'ç' becomes 'c')
        :param bool replace_greek: if True, replace greek letters with their 
            translitterated name, e.g. 'π' becomes 'pi'.
        :param string allowed_chars: string of chars to leave unchanged. 
            Note that the string is used within a regex.
        :param string errors: if 'strict' raise whatever exception occurred.
            If 'replace', replace each character that causes an error during
            processing with an underscore. Default is 'replace'.
        '''
        if word is None or len(word) == 0: return safechar
        allowed_chars += safechar
        if ' ' not in allowed_chars:
            word = re.sub(' ', safechar, word)
        try:
            word = unicode(word.decode(encoding).encode("utf-8"))
        except:
            word = unicode(word, errors="replace")
        if replace_umlauts:
            temp = u''
            for c in word:
                try:
                    if c in TextFX.phonetic_umlauts:
                        temp += TextFX.phonetic_umlauts[c]
                    else:
                        temp += c
                except Exception as e:
                    if errors == 'strict':
                        raise(e)
                    else:
                        temp += safechar
            word = temp
        if replace_diacritics:
            # canonically decompose the search string so we can "weed out" the diacritical marks
            word = ud.normalize('NFKD', word)
            # dynamically generate combining marks list
            marks = []
            for i in range(0, 7):
                for j in range(0, 16):
                    r = u"%su03%x%x" % ('\\', i, j)
                    marks.append(r.decode('unicode_escape'))        
            # loop through filename and filter out the diacritical marks
            res = u''
            for char in word:
                try:
                    if char in marks:
                        pass
                    else:
                        res += char
                except Exception as e:
                    if errors == 'strict':
                        raise(e)
                    else:
                        res += safechar
            word = res
        if replace_greek:
            temp = ''
            for c in word:
                try:
                    if c in TextFX.greek_alphabet:
                        temp += TextFX.greek_alphabet[c]
                    else:
                        temp += c
                except Exception as e:
                    if errors == 'strict':
                        raise(e)
                    else:
                        temp += safechar
            word = temp
        word = re.sub(ur'[^a-zA-Z0-9%s]' % allowed_chars, safechar, word)
        return word


class PluginWizard(object):
    '''
    CINEMA 4D plugin template wizard.
    
    Main class which provides methods for replacements in 
    the names and contents of files contained within a folder 
    structure.
    '''
    tokenchar_start   = g_mts
    tokenchar_end     = g_mte
    token_regex       = re.compile(r'%s(?P<token>\w+?)%s' % (tokenchar_start, tokenchar_end))
    token_xform_regex = re.compile(r'%s(?P<token>\w+?)As(?P<form>\w+?)%s' % (tokenchar_start, tokenchar_end))
    #import_regex      = re.compile(r'#\s*import (?P<modules>[\w, ]+)')
    #kvsplit_regex     = re.compile(r'\s*=\s*')
    
    def __init__(self, config, plugin_type=PLUGIN_TYPE_CMD):
        super(PluginWizard, self).__init__()
        self.plugin_type = plugin_type
        self._check_config(config)
        self.config = config
        if not 'excludedFiles' in config:
            config['excludedFiles'] = DEFAULT_EXCLUDES
        self.destdir = None
        self.srcdir = os.path.realpath(config['srcdataPath'])
        self._token_table = {}
        self._rules_list = []
        self._rules_filename = DEFAULT_RULES_FILENAME
        self._rules_filepath = None
        self._fill_tokentable()
        self._fill_ruleslist()

    def _check_config(self, config):
        if not 'pluginId' in config:
            raise ValueError("E: plugin id not present in config object.")
        if not 'srcdataPath' in config:
            raise ValueError("E: source data path not present in config object.")
        
    def _check_destdir(self, somedir):
        real_destdir = os.path.realpath(somedir)
        if os.path.exists(real_destdir):
            self.destdir = real_destdir
        else:
            raise CLIError("Invalid path for destination dir: '%s'" % real_destdir)
        
    def _find_rules_file(self):
        ''' Find the rules file to use. 
        
        Set ``self._rules_filepath`` to absolute path if found.        
        Only accepts files with name equal to ``self._rules_filename``.
                
        Searches multiple locations with the following precedence:
        
            1. path supplied by CLI arg
            2. per plugin type (local)
            3. per sourcedata rootdir (global)
            
        :raise: CLIError if a rules file couldn't be found.
        :return: path to the rules file.
        '''
        if 'rulesFile' in self.config:
            rules_file = self.config['rulesFile']
        else:
            rules_file = None
        if rules_file is not None and os.path.exists(rules_file):
            rules_filepath = self.config['rulesFile']
        else:   
            rules_filepath = None     
            rules_filename = self._rules_filename
            candidate_paths = [
                os.path.realpath(os.path.join(self.config['srcdataPath'], self.plugin_type, rules_filename)),
                os.path.realpath(os.path.join(self.config['srcdataPath'], rules_filename))
            ]
            for cpath in candidate_paths:
                if os.path.exists(cpath):
                    rules_filepath = cpath
        if rules_filepath is None:
            #if DEBUG: 
            #    print("rules file not found. Paths searched: %s%s" % (os.linesep, os.linesep.join(candidate_paths)))
            pass
        else: 
            rules_filepath_dir, rules_filepath_name = os.path.split(rules_filepath)  # IGNORE:W0612 @UnusedVariable
            if rules_filepath_name != self._rules_filename:
                raise CLIError("rules file name doesn't match name specified for rules files. " + 
                               "Expected %r, got %r" % (self._rules_filename, rules_filepath_name))
        self._rules_filepath = os.path.realpath(rules_filepath)
        return rules_filepath
                     
    def _fill_tokentable(self):
        '''
        Create and fill table of ``%!...!%`` magic tokens.
        
        Angle bracket based tokens are tokens where the value
        can be deferred automatically (to a degree), with as little 
        user intervention as possible.
        
        Examples are date, time and author name determined
        from the logon environment.
        
        The table consists of a dict of metadata dicts, 
        the latter of which can have multiple entries,
        one for each form the datum can be in. 
        
        E.g. if the datum is ``AuthorName``, it can have a form as
        identifier, as abbreviation, etc.
        
        :param string plugin_id: unique ID for the plugin
        :param string plugin_name: name of the plugin as 
            entered by the user
        :param string author_name: name of the author as 
            entered by the user
        '''
        config = self.config
        
        # Plugin ID
        plugin_id = config['pluginId']
        if plugin_id is None or len(str(plugin_id)) == 0:
            plugin_id = PLUGIN_ID_TESTING
        else:
            plugin_id = str(plugin_id)
        pluginid_tokens = {}
        pluginid_tokens[''] = plugin_id
        pluginid_tokens['Entered'] = pluginid_tokens['']
        self._token_table['ID'] = pluginid_tokens
        
        # Plugin Name
        plugin_name = config['pluginName']
        if plugin_name is None or len(plugin_name) == 0:
            plugin_name = 'Unnamed Plugin'
        else:
            plugin_name = str(plugin_name)
        pluginname_tokens = {}
        pluginname_tokens[''] = plugin_name
        pluginname_tokens['Entered'] = plugin_name
        pluginname_tokens['Cleaned'] = TextFX.sanitize(
            plugin_name, safechar='', 
            replace_umlauts=True, 
            replace_diacritics=True, 
            replace_greek=True, 
            allowed_chars=' ')
        pluginname_tokens['Identifier'] = TextFX.to_camelcase(pluginname_tokens['Cleaned'], True)
        pluginname_tokens['UppercaseIdentifier'] = TextFX.to_camelcase(pluginname_tokens['Cleaned'], True).upper()
        pluginname_tokens['Abbreviation'] = TextFX.abbreviate(pluginname_tokens['Cleaned'], 6)
        self._token_table['PluginName'] = pluginname_tokens
        
        # Author Name
        author_name = config['author']
        authorname_tokens = {}
        if author_name:
            authorname_tokens[''] = author_name
            authorname_tokens['Entered'] = author_name
            authorname_tokens['Cleaned'] = TextFX.sanitize(
                author_name, 
                replace_umlauts=True, 
                replace_diacritics=True, 
                replace_greek=True, 
                allowed_chars=r'_\-() ')
            authorname_tokens['Identifier'] = TextFX.to_camelcase(author_name, True)
            authorname_tokens['Abbreviation'] = TextFX.abbreviate(author_name, 6)
            self._token_table['AuthorName'] = authorname_tokens
            
        # Organization Name
        org_name = config['org']
        orgname_tokens = {}
        if org_name is not None:
            orgname_tokens[''] = org_name
            orgname_tokens['Entered'] = org_name
            orgname_tokens['Cleaned'] = TextFX.sanitize(
                org_name, safechar='', 
                replace_umlauts=True, 
                replace_diacritics=True, 
                replace_greek=True, 
                allowed_chars=r'_\-()')
            orgname_tokens['Identifier'] = TextFX.to_camelcase(org_name, True)
            orgname_tokens['Abbreviation'] = TextFX.abbreviate(org_name, 6)
            self._token_table['OrgName'] = orgname_tokens
            
        # Date+Time
        datetime_tokens = {}
        datetime_tokens[''] = time.strftime('%Y-%m-%dT%H:%M:%S')
        datetime_tokens['Iso'] = datetime_tokens['']
        datetime_tokens['Locale'] = time.strftime('%x %X')
        self._token_table['DateTime'] = datetime_tokens
        
        # Date
        date_tokens = {}
        date_tokens['IsoSeparated'] = time.strftime('%Y-%m-%d')
        date_tokens['Iso'] = time.strftime('%Y%m%d')
        date_tokens['EnglishDashSeparated'] = time.strftime('%m-%d-%y')
        date_tokens['EnglishSeparated'] = time.strftime('%m/%d/%y')
        date_tokens['English'] = time.strftime('%m%d%y')
        date_tokens['LocaleSeparated'] = time.strftime('%x')
        date_tokens['Locale'] = TextFX.sanitize(date_tokens['LocaleSeparated'], safechar='', allowed_chars='')
        date_tokens['NameOfDay'] = time.strftime('%A')
        date_tokens['ShortNameOfDay'] = time.strftime('%a')
        date_tokens[''] = date_tokens['IsoSeparated']
        self._token_table['Date'] = date_tokens
        
        # Time
        time_tokens = {}
        time_tokens[''] = TextFX.sanitize(time.strftime('%X'), safechar='', allowed_chars='')
        time_tokens['LocaleSeparated'] = time.strftime('%X')
        time_tokens['Locale'] = TextFX.sanitize(time_tokens['LocaleSeparated'], safechar='', allowed_chars='')
        time_tokens['EnglishSeparated'] = time.strftime('%H:%M:%S %p')
        time_tokens['English'] = TextFX.sanitize(time_tokens['EnglishSeparated'], safechar='', allowed_chars='')
        time_tokens['SecondsSinceEpoch'] = str(time.time())
        self._token_table['Time'] = time_tokens
    
    def _fill_ruleslist(self):
        r'''
        Parse the rules file and build the rules list. If there is not rules files,
        an empty list is returned.
        
        A rules file (usually called ``rules.py`` but this can be changed internally)
        contains a mapping of search terms to replacement terms, on one line each and 
        separated by the regex ``\s*=\s*``. The search term comes first and then the 
        replacement term follows. 
        '''
        if self._rules_filepath is None:
            self._find_rules_file()
        RULES = {}  # needs to be uppercase so it is shadowed from exec below
        ruleslist = []
        if self._rules_filepath is not None:
            rules_filepath = self._rules_filepath
            try:
                rules_filedir, rules_filename = os.path.split(rules_filepath)   # IGNORE:W0612 @UnusedVariable
                with open(rules_filepath, 'rb') as f:
                    src = f.read()
                # if the following succeeds RULES is aliased by the
                # contents of RULES in rules file at self._rules_filepath 
                exec(compile(src, rules_filename, 'exec'))  # IGNORE:W0122
            except Exception as e:
                CLIError("E: while processing %s: %s" % (rules_filename, e))
                return None
            for search, replace in RULES.iteritems():
                search = re.escape(search)
                ruleslist.append((search, replace))
        self._rules_list = ruleslist
        return ruleslist
    
    def _process_name(self, dirpath, fileordirname, force):
        filepath = os.path.join(dirpath, fileordirname)
        filename, fileext = os.path.splitext(fileordirname)
        newpath = None
        newname = None
        
        # process rules (if we have a rules file)
        
        if self._rules_filepath is not None:
            replaced = False
            for search, replace in self._rules_list:
                if re.search(search, filename):
                    filename = re.sub(search, replace, filename, flags=re.UNICODE)
                    replaced = True
            if replaced:
                newname = filename + fileext
                newpath = os.path.join(dirpath, newname)
                replaced = False
        
        # process tokens
        
        matchedtokens = re.findall(PluginWizard.token_regex, filename)
        if len(matchedtokens) > 0:
            newname = fileordirname
            for mat in matchedtokens:
                fulltoken = self.tokenchar_start + mat + self.tokenchar_end
                if 'As' in mat:
                    mat = mat.split('As')
                    token = mat[0]
                    form = mat[1]
                else:
                    token = mat
                    form = ''
                newname = re.sub(re.escape(fulltoken), self._token_table[token][form], newname)
                
            newpath = os.path.join(dirpath, newname)
            
        # do the actual renaming (if needed)
        if newpath:
            if os.path.exists(newpath):
                if force:
                    os.remove(newpath)
                else:
                    if g_verbose > 0:
                        print("E: File at '%s' exists. Skipping...\nUse -f/--force to overwrite." % newpath)
                    return False
            if g_verbose > 0:
                print("  Renaming '%s' to '%s'" % (fileordirname, newname))
                
            try:
                os.rename(filepath, newpath)
            except Exception as e:
                print("Renaming '%s' to '%s' failed: %s" % (filepath, newpath, e))
        
        return True
        
    def _process_content(self, dirpath, filename):
        filepath = os.path.join(dirpath, filename)
        if filename in self.config['excludedFiles']:
            return False
        if os.path.exists(filepath):
            if g_verbose > 0:
                print("Processing '%s'" %  (format_relpath(filepath)))

            # Backup
            
            # rename this file to filename.bak
            backup_filename = '%s%s%s' % (filename, os.extsep, "bak")
            backup_filepath = os.path.join(dirpath, backup_filename)
            try: 
                # remove filename.bak from last run if it is present
                os.remove(backup_filepath)
            except OSError: 
                pass
            os.rename(filepath, backup_filepath)
            
            with codecs.open(filepath, mode='w', encoding='utf-8') as processed_file:
                # then open a new file with this file's old name (w/o ".bak")
                # where we can write the processed lines to
                with codecs.open(backup_filepath, mode='r', encoding='utf-8') as curfile:
                    for line in curfile:
                        replaceline = line
                        matches = re.findall(PluginWizard.token_regex, line)
                        if len(matches) > 0:
                            for mat in matches:
                                if 'As' in mat:
                                    _mat = mat.split('As')
                                    token = _mat[0]
                                    form = _mat[1]
                                else:
                                    token = mat
                                    form = ''
                                try:
                                    replace = self._token_table[token][form]
                                    search = "%s%s%s" % (self.tokenchar_start, mat, self.tokenchar_end)
                                    replaceline = re.sub(search, replace, replaceline, flags=re.UNICODE)
                                except KeyError:
                                    # can't use "print" here, since it would end up in the written replaceline
                                    pass
                        if  len(self._rules_list) > 0:
                            for search, replace in self._rules_list:
                                if re.search(search, line):
                                    replaceline = re.sub(search, replace, replaceline, flags=re.UNICODE)
                        processed_file.write(replaceline)
            # done with the backup file, remove it
            os.remove(backup_filepath)
        return True

    def process_names(self, overwrite=False):
        '''
        Do magic token and rule based replacements in file and rootdir names.
        
        A magic token has the form ``%!Value!%`` or ``%!ValueAsForm!%`` where
        ``Value`` is the value of an entry in the token table and ``Form`` 
        a conjugate of that value. 
        
        E.g. ``Value`` might be ``PluginName`` which would result in the 
        plugin's name as entered by the user. 
        
        ``PluginNameAsIdentifier`` is ``PluginName`` taking the form of an 
        ``Identifier``, meaning it has invalid characters replaced, 
        spaces stripped and converted to *CamelCase* form. 
        
        There are multiple such forms for each magic token. 
        For an overview call :py:func:`print_tokentable`.
        
        :param bool overwrite: if True, rename a file or rootdir even 
            if it would replace an already existing file or rootdir.
        '''
        if self.destdir is None:
            raise ValueError("E: dest dir can't be None. Did you forget to call set_destdir()?")
        if self._rules_filepath is None:
            self._find_rules_file()
            if self._rules_filepath is not None:
                rules_filename = os.path.basename(self._rules_filepath)
                dest_rules_file = os.path.join(self.destdir, rules_filename)
            try:
                # remove copied rules file if there was one in the 
                # source data dir for our plugin type
                os.remove(dest_rules_file)
            except OSError:
                pass
        for dirpath, dirnames, filenames in os.walk(self.destdir):
            for somedir in dirnames:
                self._process_name(dirpath, somedir, overwrite)
            for somefile in filenames:
                if somefile in self.config['excludedFiles']:
                    continue                    
                self._process_name(dirpath, somefile, overwrite)
        return True
        
    def process_contents(self, exclude=None):
        '''
        Replace tokens in file contents based on rules.py
        
        :param string exclude: if filename (incl. ext) 
            matches this regex, the file is excluded from 
            being processed. Note that ``self.excluded_files``
            are being skipped by default.
        '''
        if self.destdir is None:
            raise ValueError("E: dest dir can't be None. Did you forget to call set_destdir()?")
        for dirpath, dirnames, filenames in os.walk(self.destdir):  # IGNORE:W0612 #@UnusedVariable
            for somefile in filenames:
                if exclude and re.match(exclude, somefile, re.UNICODE):
                    continue
                self._process_content(dirpath, somefile)
        return True

    def get_tokentable_listing(self, indent=3):
        '''
        Get a string with all data entries of the token table, including forms.
        
        :param int indent: how many spaces for indentation.
        '''
        result = ""
        spaces = " " * indent
        for k, v in self._token_table.iteritems():
            result += ("%s:" % k) + os.linesep
            for entry in v:
                if entry == '': # default form
                    continue
                else:
                    result += ("%s%sAs%s" % (spaces, k, entry)) + os.linesep
            result += os.linesep
        return result

    def set_destdir(self, somepath):
        self._check_destdir(somepath)
        self.destdir = somepath
    

def format_relpath(path, start=os.curdir):
    '''
    Make ``path`` into a relative path with ``start`` 
    as base and canonicalize path separators in the 
    process.
    '''
    if '/' in path:
        sep = '/'
    elif r'\\' in path:
        sep = r'\\'
    else:
        sep = os.sep
    return ('%s%s%s' % (os.curdir, sep, os.path.relpath(path, start)))


def canonicalize_path(path):
    ''' Canonicalize path separators. '''
    if g_win:
        return path.replace('/', '\\')
    elif g_osx:
        return path.replace('\\', '/')
    return path


def truncate_path(path, max_size, alignment, ellipsis="..."):
    elen = len(ellipsis)
    if alignment == "mid":
        p1 = int(round(max_size/2)-elen)
        p2 = int(-(round(max_size/2)))
        return path[:p1] + ellipsis + path[p2:]
    elif alignment == "start" or alignment == "left":
        return ellipsis + path[-(max_size-elen):]
    else:
        # alignment == "end" or aligment == "right"
        return path[:(max_size-elen)] + ellipsis


def is_valid_path(path):
    return os.path.isdir(path)


def is_valid_plugin_id(someId):
    ''' Test if 'someId' is a valid Plugin Cafe ID. '''
    if isinstance(someId, basestring):
        try:
            someId = int(someId, 10)
        except ValueError:
            return False
    if not isinstance(someId, (int, long)):
        return False
    else:
        return (someId > 1000000)


def get_author_name():
    result = None
    if DEFAULT_ENV_AUTHOR in os.environ:
        result = os.environ[DEFAULT_ENV_AUTHOR]
    else:
        fulluser = None
        if g_osx:
            user = os.environ['USER']
            try:
                out, err = Popen(
                    ['/bin/sh -c "osascript -e \'long user name of (system info)\'"'],
                    stdout=PIPE, shell=True
                ).communicate()
                if err: 
                    print(err)
                else:
                    fulluser = out
            except:
                fulluser = user
        elif g_win:
            user = os.environ['USERNAME']
            try:
                import win32api # IGNORE:F0401 @UnresolvedImport
                fulluser = win32api.GetUserName()
            except:
                fulluser = user
        if fulluser is None:
            result = "Unknown Author"
        else:
            result = fulluser.strip() # IGNORE:E1103
    return result


def get_company_name():
    default = ''
    if DEFAULT_ENV_ORG in os.environ:
        return os.environ[DEFAULT_ENV_ORG]
    return default

def get_data_path():
    default = os.path.realpath(DEFAULT_DATADIR)
    if DEFAULT_ENV_DATA in os.environ:
        return os.environ[DEFAULT_ENV_DATA]
    return canonicalize_path(default)


def system(cmd, args=None):
    '''
    Convenience function for firing off commands to 
    the system console. Used instead of `subprocess.call`_
    so that shell variables will be expanded properly.
    
    Not the same as `os.system`_ as here it captures 
    returns ``stdout`` and ``stderr`` in a tuple in
    Python 2.5 and lower or a ``namedtuple`` in 2.6
    and higher. So you can use ``result[0]`` in the
    first case and ``result.out`` in the second.

    :param string cmd: a console command line
    :param list args: list of arguments that 
        will be expanded in cmd starting with 
        ``$0``.
    :return: ``tuple`` or ``namedtuple``
    '''
    if args is None:
        fullcmd = cmd
    else:
        args = ["'{}'".format(s.replace(r'\\', r'\\\\')
                               .replace("'", r"\'")) for s in args]
        fullcmd = "%s %s" % (cmd, ' '.join(args))
    out, err = Popen(fullcmd, stdout=PIPE, shell=True).communicate()
    system.out = out
    system.err = err
    try:
        from collections import namedtuple
        StdStreams = namedtuple('StdStreams', ['out', 'err'])
        return StdStreams(out=out, err=err)
    except ImportError:
        return (out, err)


def rmtree_onerror(func, path, exc_info):  # IGNORE:W0613
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        try:
            if g_win:
                os.system('rmdir /S /Q \"{}\"'.format(path))
            elif g_osx:
                os.system('rm -rf \"{}\"'.format(path))
        except Exception as e:
            print(e)


def copytree_ignore(src, names):  # IGNORE:W0613
    excludes = list(set(DEFAULT_DIR_EXCLUDES).intersection(set(names)))
    if g_verbose > 0:
        for e in excludes:
            print("Excluding '%s'. reason: in dir exclude list." % e)
    return excludes
    

CONFIG_DEFAULT = {
    'pluginId': str(PLUGIN_ID_TESTING),    # required
    'pluginName': 'Unnamed Plugin',        # optional
    'author': get_author_name(),           # optional
    'org': get_company_name(),             # optional
    'rulesFile': None,                     # optional, will be set later by search in sourcedata_path
    'srcdataPath': get_data_path(),        # required
    'excludedFiles': DEFAULT_EXCLUDES      # optional
}


def main(argv=None, extend=True):  # IGNORE:C0111
    '''
    :param list argv: a list of arguments to use instead of ``sys.argv``.
    :param bool extend: set to False if the passed ``argv`` should replace 
        ``sys.argv`` completely instead of extending it. The GUI script uses 
        this so that ``argv[0]`` which is usually the path to the executing 
        program doesn't end up standing in for one of the needed args such
        as plugin ID and plugin name.
    '''
    if isinstance(argv, list):
        if extend is True:
            sys.argv.extend(argv)
        else:
            sys.argv = argv
    
    program_name = "c4dplugwiz"  # IGNORE:W0612 @UnusedVariable
    program_version = "v%s" % __versionstr__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = '''c4dplugwiz -- CINEMA 4D plugin wizard'''
    program_license = u'''%s
    
  Created by André Berg on %s.
  Copyright 2013 Sera Media VFX. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        
        # flags (optional)
        parser.add_argument('-l', '--list-tokens', dest='list_tokens', action="store_true", help="list available tokens plus forms and exit.")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-f', '--force', dest='overwrite', action="store_true", help="overwrite existing target folders [default: %(default)s]")
        parser.add_argument('-c', '--create-rootdir', dest='createdir', action="store_true", help="create destination path if it doesn't exist [default: %(default)s]")
        parser.add_argument('-t', '--type', dest="plugin_type", help="type of plugin to create. Determines which subfolder is used from the sourcedata rootdir [default: %(default)s]")
        parser.add_argument('-s', '--source-data', dest='src', help="path to rootdir with source folder structures. Must have one folder structure per plugin type. You can also set the environment variable '" + DEFAULT_ENV_DATA + "'. [default: %(default)s]")
        parser.add_argument('-r', '--rules-file-name', dest='rules_file', metavar='str', help="rules file name. If None, looks for a file 'rules.py' relative to the main data dir or relative to each plugin type's template folder structure. If this is None, falls back to looking in the sourcedata rootdir. [default: %(default)s]")
        parser.add_argument('-a', '--author', dest='author', help="name of the plugin author to be used in file/rootdir name replacements. You can also set the environment variable '" + DEFAULT_ENV_AUTHOR + "'. [default: %(default)s]")
        parser.add_argument('-o', '--org', dest='org', help="name of the organization the author belongs to, used for file/rootdir name replacements. You can also set the environment variable '" + DEFAULT_ENV_ORG + "'. [default: %(default)s]")
        parser.add_argument('-d', '--destination', dest='dest', help="name of the destination folder. [default: %(default)s]")
        
        # positional arguments (required)
        parser.add_argument(dest="plugin_id", help="unique ID of the plugin (obtained from www.PluginCafe.com)", metavar="id", nargs="?")
        parser.add_argument(dest="plugin_name", help="name of the plugin.", metavar="name", nargs="?")
        
        # Environment variable defaults
        default_source = get_data_path()
        default_author = get_author_name()
        default_org = get_company_name()

        parser.set_defaults(src=default_source, plugin_type=PLUGIN_TYPE_CMD, 
                            author=default_author, org=default_org, verbose=0, 
                            dest=os.curdir, list_tokens=False)
        
        # Process arguments
        args = parser.parse_args()
        
        global g_verbose  # IGNORE:W0601
        
        g_verbose = args.verbose
        list_tokens = args.list_tokens
        paths = [args.dest]
        plugin_id = args.plugin_id
        plugin_name = args.plugin_name
        plugin_type = args.plugin_type
        source_datapath = canonicalize_path(args.src)
        overwrite = args.overwrite
        createdir = args.createdir
        author = args.author
        org = args.org
        rules_file = args.rules_file

        config = CONFIG_DEFAULT
        
        # required
        config['pluginId'] = plugin_id
        config['pluginName'] = plugin_name
        config['srcdataPath'] = source_datapath
        
        # optional
        if author:
            config['author'] = author
        if org:
            config['org'] = org
        if rules_file:
            config['rulesFile'] = rules_file
        
        # Steps
        # 1. Create and setup wizard. 
        
        # This also creates and fills the token table
        # as well as the rules list.
        pw = PluginWizard(config, plugin_type)

        if list_tokens:
            # print token table to stdout and exit
            indent = 3
            spaces = " " * indent
            print("Listing token table...")
            print("")
            print("Format:")
            print("%sDatum" % (spaces))
            print("%sDatumAsForm1" % (spaces))
            print("%sDatumAsForm2" % (spaces))
            print("%s..." % (spaces))
            print("")
            print(pw.get_tokentable_listing(indent))
            return 0
        else:
            if plugin_id is None:
                raise CLIError("E: missing plugin id.")
            if plugin_name is None:
                raise CLIError("E: missing plugin name.")
            if source_datapath is None or not is_valid_path(source_datapath):
                raise CLIError("E: source data path invalid.")
                        
        if g_verbose > 0:
            print("Verbose mode on")
            print("Plugin ID %s: %s    name: '%s' %s    type: '%s'" % 
                  (plugin_id, os.linesep, plugin_name, os.linesep, plugin_type))
            print("")
            if rules_file is not None or pw._rules_filepath is not None:
                print("     Using rules file at '%s' with %d rules and %d tokens." % 
                      (format_relpath(pw._rules_filepath), len(pw._rules_list), len(pw._token_table.values())))

        source = canonicalize_path(os.path.join(source_datapath, plugin_type))

        if not os.path.exists(source_datapath):
            raise CLIError("source data doesn't exist at path: '%s'" % canonicalize_path(source_datapath))
        if not os.path.exists(source):
            raise CLIError("couldn't find template folder structure for plugin type '%s' at '%s'" % 
                           (plugin_type, source))

        if g_verbose > 0:
            print("    Using source data at '%s'" % format_relpath(source_datapath))
            print("Using template structure '%s'" % format_relpath(source))
            print("")
                        
        for destpath in paths:
            if g_verbose > 0:
                print("Processing destination '%s'" % os.path.realpath(destpath))
                print("")
                
            real_destpath = canonicalize_path(os.path.realpath(destpath))
            full_destpath = os.path.join(real_destpath, plugin_type)
            named_fulldestpath = canonicalize_path(os.path.join(real_destpath, plugin_name))
            dest_parentdir, destdir = real_destpath, plugin_type  # IGNORE:W0612 #@UnusedVariable
            
            if not os.path.exists(dest_parentdir):
                if createdir:
                    os.makedirs(dest_parentdir, mode=0o755)
                    if not os.path.exists(dest_parentdir):
                        raise CLIError("creating parent dir for destination '%s'  failed. skipping..." % destpath)
                else:
                    raise CLIError("destination '%s' doesn't exist. skipping..." % destpath)
                                    
            # 2. Copy folder structure(s)
            if overwrite and os.path.exists(named_fulldestpath):
                if g_verbose > 0:
                    print("Overwriting destination dir at '%s'" %  (os.path.relpath(named_fulldestpath, 
                                                                                    os.path.realpath(os.curdir))))
                try:
                    su.rmtree(named_fulldestpath, onerror=rmtree_onerror)
                    su.copytree(source, named_fulldestpath, ignore=copytree_ignore)
                except Exception as e:
                    raise CLIError("E: %s" % str(e))
            else:
                try:
                    if g_verbose > 0:
                        print("Copying template folder structure to destination.")
                    su.copytree(source, named_fulldestpath, ignore=copytree_ignore)
                except OSError, e:
                    if 'exists' in str(e):
                        raise CLIError("dir exists: '%s'%sUse -f/--force to overwrite" % (full_destpath, os.linesep))          

            pw.set_destdir(named_fulldestpath)
            
            # 3. Do file name replacements
            pw.process_names(overwrite=overwrite)
            
            # 4. Do file content replacements
            pw.process_contents()
            
        return 0
    except KeyboardInterrupt:
        return 0
#     except Exception as e:
#         if DEBUG or TESTRUN:
#             raise(e)
#         sys.stderr.write("%s%s" % (str(e), os.linesep))
#         sys.stderr.write("for help use --help")
#         return 2


if __name__ == "__main__":
    if TESTRUN:
        import doctest
        doctest.testmod()
    if DEBUG:
        if os.path.isdir('testrun'):
            su.rmtree('testrun', onerror=rmtree_onerror)
        #os.environ[DEFAULT_ENV_DATA] = "../unittests/data"
        os.environ[DEFAULT_ENV_AUTHOR] = "Andre Berg"
        os.environ[DEFAULT_ENV_ORG] = "Sera Media VFX"
        plugintype = "tagplugin"
        #main(['-l'])
        #main(['-h'])
        main(['--verbose', '--create-rootdir', '--force', u'--destination=testrun', 
              u'--org=', u'--author=Andre Berg', u'--type=cmdplugin', 
              u'1000001', u"Unnamed Plugins"])
        sys.exit(0)
    if PROFILE:
        import cProfile
        import pstats
        if os.path.isdir('testrun', onerror=rmtree_onerror):
            su.rmtree('testrun')
        #os.environ[DEFAULT_ENV_DATA] = "../tests/data"
        os.environ[DEFAULT_ENV_AUTHOR] = "Andre Berg"
        os.environ[DEFAULT_ENV_ORG] = "Sera Media VFX"
        profile_filename = 'c4dplugwiz_profile.pstats'
        cProfile.run('main(["-v", "-c", "--type=tagplugin", "-f", "-d=testrun", "1000001", "My Plugin"])', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        print(stats.print_stats(), file=statsfile)
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
