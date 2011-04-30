#!/usr/local/bin/python2.7
# encoding: utf-8
'''
c4dplugwiz -- CINEMA 4D Python plugin wizard

c4dplugwiz is a command line tool that helps with creating 
python plugins for CINEMA 4D by copying some pre-existing 
folder structure to a destination specified by the user.

The folder structure contains template files with special
file names and magic text tokens that are to be replaced,
by variations of the name of the plugin as entered by the
user.

There can be multiple folder structures, e.g. one per type
of plugin that one can create in CINEMA 4D.

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

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2011-04-30'
__updated__ = '2011-04-30'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

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
    '''Collection of methods (effects) for transforming text.'''
    
    def __init__(self):
        super(TextFX, self).__init__()
        
class FolderStructure(object):
    '''
    Represents the folder structure for one type of plugin.
    
    Provides methods for token replacements in the names and 
    content of files contained within the folder structure.
    '''
    
    def __init__(self):
        super(FolderStructure, self).__init__()
        
def main(argv=None): # IGNORE:C0111
    if argv is None:
        argv = sys.argv
    else:
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
        #parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        #parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
        #parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-t', '--type', dest="typ", help="the type of plugin to create. Determines which subfolder is used from the sourcedata dir")
        parser.add_argument('-s', '--sourcedata', dest='src', help="path to dir with source folder structures. Must have one folder structure per plugin type. Tip: you can also set the environment variable 'C4DPLUGWIZ_DATA'. [default: %(default)s]")
        parser.add_argument(dest="name", help="name of the plugin.", metavar="name")
        parser.add_argument(dest="paths", help="paths to destination folder(s) [default: %(default)s]", metavar="paths", nargs='+')
        
        if os.environ.has_key('C4DPLUGWIZ_DATA'):
            default_source = os.environ['C4DPLUGWIZ_DATA']
        else:
            default_source =os.path.join(os.curdir, "c4dplugwiz_data")
        parser.set_defaults(src=default_source)
        
        # Process arguments
        args = parser.parse_args()
        
        paths = args.paths
        verbose = args.verbose
        #recurse = args.recurse
        #inpat = args.include
        #expat = args.exclude
        name = args.name
        sourcedatapath = args.src
        typ = args.typ
        source = os.path.join(sourcedatapath, typ)
   
        if verbose > 0:
            print "Verbose mode on"
            print "Plugin '%s'" % name
            print
            #if recurse:
            #    print "Recursive mode on"
            #else:
            #    print "Recursive mode off"
        
        #if inpat and expat and inpat == expat:
        #    raise CLIError(u"include and exclude pattern are equal! Nothing will be processed."
        if not os.path.exists(sourcedatapath):
            raise CLIError("sourcedata path doesn't exist ('%s')" % sourcedatapath)
        if not os.path.exists(source):
            raise CLIError("couldn't find a folder structure for plugin type '%s' at '%s'" % (typ, source))
        
        for destpath in paths:
            if verbose > 0:
                print "Processing destination '%s' ..." % destpath
                print "  Using source data at '%s'" % sourcedatapath
                print "Using folder structure '%s'" % source
            destpath = os.path.abspath(destpath)
            if not os.path.exists(destpath):
                raise CLIError("destination '%s' doesn't exist. skipping..." % destpath)
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + unicode(e).decode('unicode_escape')
        print >> sys.stderr, "\t for help use --help"
        return 2

if __name__ == "__main__":
    '''Command line options.'''
    if DEBUG:
        #os.environ['C4DPLUGWIZ_DATA'] = "test"
        #sys.argv.append("-h")
        sys.argv.append("-v")
        #sys.argv.append("-r")
        sys.argv.append("-t")
        sys.argv.append("tagplugin")
        sys.argv.append("My Plugin")
        sys.argv.append(".")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'c4dplugwiz_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        print >> statsfile, stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())