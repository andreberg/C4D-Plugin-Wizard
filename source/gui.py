#!/usr/local/bin/python
# encoding: utf-8
# pylint: disable-msg=W0613,W0702,W0703
'''
gui -- graphical user interface for c4dplugwiz.

Needs PyQt4 and Qt 4.8.4 or higher.

:author:    | André Berg
:copyright: | 2013 Iris VFX. All rights reserved.
:license:   | Licensed under the Apache License, Version 2.0 (the "License");
            | you may not use this file except in compliance with the License.
            | You may obtain a copy of the License at
            | 
            | http://www.apache.org/licenses/LICENSE-2.0
            | 
            | Unless required by applicable law or agreed to in writing, software
            | distributed under the License is distributed on an **"AS IS"** **BASIS**,
            | **WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND**, either express or implied.
            | See the License for the specific language governing permissions and
            | limitations under the License.
:contact:   | irisvfx@gmail.com
'''
from __future__ import print_function

# This is only needed for Python v2 but is harmless for Python v3.
import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

# Ugly hack; but needed for py2app/py2exe since a sitecustomize doesn't work 
# for a byte compiled virtual environment...
import sys
reload(sys)
sys.setdefaultencoding("utf-8")  # IGNORE:E1101 @UndefinedVariable

import os
import re
from ConfigParser import ConfigParser

__all__ = []
__version__ = (0, 1)
__date__ = '2013-08-16'
__updated__ = '2013-10-07'

DEBUG = 0 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)
PROFILE = 0 or ('ProfileLevel' in os.environ and os.environ['ProfileLevel'] > 0)


# import logging
# logging.basicConfig(filename=(os.path.join(os.environ['HOME'], 'debug_log.txt')), level=logging.DEBUG)

import c4dplugwiz

from c4dplugwiz import (CLIError, main as c4dplugwiz_main, CONFIG_DEFAULT, 
                        PLUGIN_ID_TESTING, DEFAULT_ENV_AUTHOR, DEFAULT_ENV_ORG, DEFAULT_ENV_DATA, 
                        g_win, g_osx, canonicalize_path as canonicalizePath, is_valid_path as isValidPath,
                        is_valid_plugin_id as isValidPluginId, is_valid_plugin_name as isValidPluginName,
                        get_parent_dirpath)    

try:
    from PyQt4 import QtGui, QtCore
except ImportError as ie:
    print("E: %s. This program needs PyQt4 and Qt 4.8.4 or higher." % ie)
    

PLUGINCAFE_GETID_LINK = 'http://www.plugincafe.com/forum/developer.asp'

SETTINGS_FILE_PATH = os.path.join(os.path.split(os.path.realpath(__file__))[0], "settings.ini")


try:
    pw = c4dplugwiz.PluginWizard
    tokenTableStr = pw.get_tokentable_listing()
except Exception as e:
    tokenTableStr = ""

if g_win:
    txtsize = "13px"
else:
    # g_osx
    txtsize = "larger"

TEMPLATE_HELP_PLAIN = """<h1>Template Help</h1>

<span style="font-size: %s;">
<p>A template is a blueprint folder structure containing the files
and directories representing one type of plugin that can be created,
e.g. tag plugin, command plugin, etc.</p>

<p>While there usually is a predetermined layout of directories
and subdirectories for each plugin type (see C4D docs), the
actual contents of any file is of course up to the user.</p>

<p>When the template is read and a new plugin created, the
wizard performs replacements of <b>magic tokens</b> and <b>rules</b> in
the files and folder names of the template folder structure,
as well as the contents of any file.</p>

<p>Magic tokens are specific text snippets enclosed by the
starting character sequence <b>%%!</b> and the ending character
sequence <b>!%%</b>.</p>

<p>The text snippets that can be used inbetween are called <b>datum points</b>
and are predetermined. Datum points can also have <b>alternative forms</b> 
into which they will be transformed.</p>

<p>For example one datum point might be the plugin name as
entered by the user and one transformation might be an
uppercase transformation, called the <b>UppercaseID</b> form.
A complete magic token of the previous example would be
<b>PluginName</b>, additionally with the alternative form:
<b>PluginNameAsUppercaseID</b>.</p>

<p>Note the adverb <b>As</b> that separates the datum point from the
alternative form.</p>

<p>Rules on the other hand are read from a Python file called, 
<b>rules.py</b> that can reside in the data directory or in each 
template directory. This file won't be copied but a Python 
dictionary type variable named <b>RULES</b> will be read from it 
and the wizard will then perform searches looking for any 
text strings named the same as the keys of the RULES dict 
and will then perform replacements with the corresponding 
values.</p>

<p>So, if you have a file called <b>%%!PluginNameAsUppercaseID!%%.pyp</b>
in one of your templates and you enter "Super Awesome Plugin" as 
the plugin name in the wizard, the file will be renamed to 
<b>SUPERAWESOMEPLUGIN.pyp</b></p>

Likewise, suppose your <b>rules.py</b> file contains the following <b>RULES</b> dict:

<pre>
import time

RULES = {
    '${YEAR}': time.strftime("%%Y"),
    'COMPANY': 'My Company'
}
</pre>

The wizard will now replace any occurrence of <b>${YEAR}</b> with
the current year as returned by <span style="font-family: Courier;">
time.strftime</span> and any occurrence
of <b>COMPANY</b> with 'My Company'. Again, this includes files and
directory names as well as file contents.

<h1>Magic Tokens</h1>

<p>Currently the following magic tokens are supported:</p>

<p><i>Note: magic tokens and rules are case sensitive.</i></p>

<pre>
%s
</pre>

</span>
""" % (txtsize, tokenTableStr)

TEMPLATE_HELP_STYLED = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
   <title>Template Help</title>
   <style type="text/css" alt="default">
      body { font-family: 'Lucida Grande', Arial, sans-serif; font-size: 100%%; 
             background-color: white; color: #000; margin: 0; padding: 0; }
      div.body h1 { margin-top: 0; font-size: 200%%; }
      div.body h2 { font-size: 160%%; }
      div.body h3 { font-size: 140%%; }
      div.body h4 { font-size: 120%%; }
      div.body h5 { font-size: 110%%; }
      div.body h6 { font-size: 100%%; }
      div.body p, div.body dd, div.body li { line-height: 130%%; }
      pre { padding: 5px; color: #333333; line-height: 120%%; }
      tt { background-color: #ecf0f3; padding: 0 1px 0 1px; font-size: 0.95em; }
   </style>
   <style type="text/css" alt="pydocs3theme">
      body { background-color: white; margin-left: 1em; margin-right: 1em; }
      div.body { padding: 0 0 0 1.2em; }
      div.body p { line-height: 120%%; }
      div.body h1, div.body h2, div.body h3, div.body h4, div.body h5, div.body h6 { 
          margin: 0; border: 0; padding: 0.75em 0em 0.25em 0em; }
      div.body pre { border-radius: 3px; }
      tt, pre { font-family: monospace, sans-serif; font-size: 96.5%%; }
      div.footer { line-height: 150%%; margin-top: -2em; text-align: right; width: auto; margin-right: 10px; }
      div.footer a:hover { color: #0095C4; }
   </style>
   <style type="text/css" alt="pygments">
      .highlight .kn { color: #007020; font-weight: bold } /* Keyword.Namespace */
      .highlight .s { color: #4070a0 } /* Literal.String */
      .highlight .nn { color: #0e84b5; font-weight: bold } /* Name.Namespace */
   </style>
</head>
<body>
   <div class="body">
      <div class="section" id="about-templates">
         <h1>About Templates</h1>
         <p>A template is a blueprint folder structure containing the files and directories 
            representing one type of plugin that can be created, e.g. tag plugin, command plugin, etc.</p>
         <p>While there usually is a predetermined layout of directories and subdirectories 
            for each plugin type (see C4D docs), the actual contents of any file is of course 
            up to the user.</p>
         <p>When the template is read and a new plugin created, the wizard performs replacements 
            of <strong>magic tokens</strong> and <strong>rules</strong> in the files and folder 
            names of the template folder structure, as well as the contents of any file.</p>
         <p>Magic tokens are specific text snippets enclosed by the starting character sequence 
            <strong>%%!</strong> and the ending character sequence <strong>!%%</strong>.</p>
         <p>The text snippets that can be used inbetween are called <strong>datum points</strong> 
            and are predetermined. Datum points can also have <strong>alternative forms</strong> 
            into which they will be transformed.</p>
         <p>For example one datum point might be the plugin name as entered by the user and one 
            transformation might be an uppercase transformation, called the <strong>UppercaseID</strong> form.
            A complete magic token of the previous example would be <strong>PluginName</strong>, 
            additionally with the alternative form: <strong>PluginNameAsUppercaseID</strong>.</p>
         <p>Note the adverb <strong>As</strong> that separates the datum point from the alternative 
            form.</p>
         <p><strong>Rules</strong> on the other hand are read from a Python file called, 
            <strong>rules.py</strong> that can reside in the data directory or in each template 
            directory. This file won’t be copied but a Python dictionary type variable named 
            <strong>RULES</strong> will be read from it and the wizard will then perform searches 
            looking for any text strings named the same as the keys of the RULES dict and will then 
            perform replacements with the corresponding values.</p>
         <p>So, if you have a file called <tt class="docutils literal">
            <span class="pre">%%!PluginNameAsUppercaseID!%%.pyp</span></tt> in one of your 
            templates and you enter <tt class="docutils literal"><span class="pre">Super Awesome Plugin</span></tt> 
            as the plugin name in the wizard, the file will be renamed to <tt class="docutils literal">
            <span class="pre">SUPERAWESOMEPLUGIN.pyp</span></tt></p>
         <p>Likewise, suppose your <strong>rules.py</strong> file contains the following <strong>RULES</strong> 
            dictionary variable:</p>
         <div class="code highlight-python">
            <div class="highlight"><pre>
<span class="kn">import</span> <span class="nn">time</span>

<span class="n">RULES</span> <span class="o">=</span> <span class="p">{</span>
   <span class="s">'${YEAR}'</span><span class="p">:</span> <span class="n">time</span><span class="o">.</span><span class="n">strftime</span><span class="p">(</span><span class="s">"%%Y"</span><span class="p">),</span>
   <span class="s">'COMPANY'</span><span class="p">:</span> <span class="s">'My Company'</span>
<span class="p">}</span></pre>
            </div>
         </div>
         <p>The wizard will now replace any occurrences of <tt class="docutils literal">
            <span class="pre">${YEAR}</span></tt> with the current year as returned by 
            <tt class="docutils literal"><span class="pre">time.strftime</span></tt> and 
            any occurrence of <tt class="docutils literal"><span class="pre">COMPANY</span>
            </tt> with <tt class="docutils literal"><span class="pre">My Company</span></tt>.
            Again, this includes files and directory names as well as file contents.</p>
         <div class="section" id="magic-tokens">
            <h1>Magic Tokens</h1>
            <p>Currently the following magic tokens are supported:</p>
            <p><em>Note: magic tokens and rules are case sensitive.</em></p>
            <div class="code highlight-python">
               <pre>%s</pre>
            </div>
         </div>
      </div>
   </div>
</body>
</html>""" % (tokenTableStr)

def showError(msg, parent=None):
    QtGui.QMessageBox.warning(parent, "Error", str(msg), QtGui.QMessageBox.Ok)


def openPath(path):
    try:
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file:///" + path))
    except Exception as e:
        showError("Couldn't open '%s': %s" % (path, e))


def tryDecode(s):
    try:
        return s.decode(sys.getdefaultencoding())
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s.decode("utf-8")

class PluginWizardGui(QtGui.QWizard):
    
    def __init__(self):
        super(PluginWizardGui, self).__init__()
        self.setSubTitleFormat(1)   # Qt::TextFormat enum Qt::RichText == 1

        self.state = {}
        self.loadSettings()
                
        self.addPage(IntroPage())
        self.addPage(DetailsPage())
        self.addPage(TemplatePage())
        self.addPage(ConclusionPage())
        
        self.connect(self, QtCore.SIGNAL("currentIdChanged(int)"), self.handleIdChange)

    def getCurrentState(self):
        self.updateCurrentState()
        return self.state
    
    def updateCurrentState(self):
        conclusionPage = self.page(3)
        destPathComboBox = conclusionPage.directoryComboBox
        templatePage = self.page(2)
        pluginId = str(self.field("pluginId"))
        pluginName = str(self.field("pluginName"))      
        destinationPath = str(destPathComboBox.itemText(self.field("destinationPath")))
        author = str(self.field("author"))
        org = str(self.field("org"))
        overwrite = bool(self.field('overwrite'))
        template = templatePage.selectedTemplate
        templatePath = templatePage.selectedTemplatePath
        source = str(templatePage.currentPath)
        newState = {
            'pluginId': pluginId,
            'pluginName': pluginName,
            'author': author,
            'org': org,
            'overwrite': overwrite,
            'template': template,
            'srcdataPath': source,
            'templatePath': templatePath,
            'destinationPath': destinationPath
        }
        # if DEBUG: print("updateCurrentState: %r" % newState)
        self.state = newState
        return True

    def saveSettings(self):
        state = self.getCurrentState()
        config = ConfigParser(state)
        with open(SETTINGS_FILE_PATH, 'wb') as configfile:
            config.write(configfile)
        return True
        
    @staticmethod
    def loadSettings():
        state = {}
        if os.path.exists(SETTINGS_FILE_PATH):
            try:
                config = ConfigParser()
                config.read(SETTINGS_FILE_PATH)
            except:
                return False
            strkeys = ['pluginId', 'pluginName', 'author', 'org',  'template', 
                       'srcdataPath', 'templatePath', 'destinationPath']
            for sk in strkeys:
                try:
                    value = str(config.get("DEFAULT", sk))
                    state[sk] = tryDecode(value)
                except: # IGNORE:W0702
                    pass
            boolkeys = ['overwrite']
            for bk in boolkeys:
                try:
                    value = str(config.get("DEFAULT", bk))
                    state[bk] = bool(tryDecode(value))
                except:  # IGNORE:W0702
                    pass
        # could load from CONFIG_DEFAULT here if no settings file
        return state
  
    def accept(self, *args, **kwargs):
        self.updateCurrentState()
        
        destination = self.state['destinationPath']
        if not isValidPath(destination):
            showError("Invalid destination.", parent=self)
            return
        
        overwrite = bool(self.state['overwrite'])
        pluginId = self.state["pluginId"]
        pluginName = self.state["pluginName"]
        
        if overwrite is False and os.path.exists(os.path.join(destination, pluginName)):
            showError("A plugin named '%s' \n"
                      "already exists at the destination and \n"
                      "Overwrite? is set to %s." % (pluginName, str(overwrite)))
            return
        
        author = self.state["author"]
        org = self.state["org"]
        template = self.state['template']
        templatePath = self.state['templatePath']
        source = get_parent_dirpath(templatePath)
        
        try:
            self.saveSettings()
        except Exception as e:  # IGNORE:W0703
            print("E: couldn't save settings: %s" % e)

        args = ["--verbose", "--create-rootdir", "--source-data=%s" % source,
                '--destination=%s' % destination, "--org=%s" % org, "--author=%s" % author, 
                "--type=%s" % template, pluginId, pluginName]
        
        if overwrite == True:
            args.insert(2, '--force')
            
        # if DEBUG: print("args = %r" % args)
        result = -1
        errMsg = "Unknown error."
        try:
            result = c4dplugwiz_main(args, extend=False)
        except Exception as e:
            errMsg = "Error: " + str(e)
        if result == 0:
            openPath(os.path.realpath(os.path.join(destination, pluginName)))
            super(PluginWizardGui, self).accept()
        else:
            showError("%s.\n\n"
                      "Please double check that the selected data "
                      "directory actually contains some valid templates." % (errMsg))
    
    def handleIdChange(self, *args, **kwargs):
        # if DEBUG: print("handleIdChange: state = %r" % self.state)
        if self.currentId() == 1:
            # Details page
            self.state = self.loadSettings()
            self.page(1).pluginIdLineEdit.selectAll()
            self.page(1).pluginIdLineEdit.setFocus()
        elif self.currentId() == 2:
            # Template page
            templatePage = self.page(2)
            templatePage.updateTemplateTree()
            self.updateCurrentState()
            templateTree = templatePage.templateTree
            #if ('template' in self.state and 
            #    self.state['template'] is not None):
            #    matches = templateTree.findItems(self.state['template'], QtCore.Qt.MatchFlags(0))
            #    if len(matches) > 0:
            #        templateTable.setCurrentItem(matches[0])
            #else:
            #    templateTable.setCurrentItem(templateTable.item(0, 0))
            templateTree.setFocus()
        elif self.currentId() == 3:
            # Conclusion page
            self.updateCurrentState()
        else:
            self.updateCurrentState()
    
    def colorText(self, text, color):
        return "<font color='%s'>%s</font>" % (color, text)

    def uncolorText(self, text):
        pat = re.compile("<font color='.+?'>(.+?)</font>")
        result = re.sub(pat, r'\1', text)
        return result
    
    def validateCurrentPage(self, *args, **kwargs):
        if self.currentId() == 1:
            # Details page
            if self.field('author') == "":
                self.setField('author', 'Unknown Author')
            curPage = self.currentPage()
            pluginIdLabel = curPage.pluginIdLabel
            pluginNameLabel = curPage.pluginNameLabel
            idstr = self.field("pluginId")
            namestr = self.field("pluginName")
            if not isValidPluginId(idstr):
                pluginIdLabel.setText(self.colorText(pluginIdLabel.text(), 'red'))
                return False
            if not isValidPluginName(namestr):
                pluginNameLabel.setText(self.colorText(pluginNameLabel.text(), 'red'))
                return False
            # everything OK? set color back to no color in case user goes back a page
            pluginIdLabel.setText(self.uncolorText(pluginIdLabel.text()))
            pluginNameLabel.setText(self.uncolorText(pluginNameLabel.text()))
        if self.currentId() == 2:
            # Template page
            curPage = self.currentPage()
            if (curPage.selectedTemplate is None or 
                curPage.getPathForTemplate() is None):
                #templateTable = curPage.templateTable
                #curRow = templateTable.currentRow()
                #curCol = templateTable.currentColumn()
                #if curPage.updateSelectedTemplate(curRow, curCol) is True:
                #    return True
                templateTree = curPage.templateTree
                curIdx = templateTree.currentIndex()
                if curPage.updateSelectedTemplate(curIdx) is True:
                    return True
                return False
        if self.currentId() == 3:
            # Conclusion page
            curPage = self.currentPage()
            if not isValidPath(curPage.destinationPath):
                return False
        return QtGui.QWizard.validateCurrentPage(self, *args, **kwargs)

    
class IntroPage(QtGui.QWizardPage):    
    def __init__(self, parent=None):
        super(IntroPage, self).__init__(parent)
        self.setTitle("Introduction")
        
        imgLabel = QtGui.QLabel()
        if g_win:
            bgimg = QtGui.QPixmap("images/c4dr14bg_60p_transp.png")
            imgLabel.setPixmap(bgimg)
        
        label = QtGui.QLabel("This wizard will help you create new CINEMA 4D plugins "
                             "from a template and details that you will be able to "
                             "provide on the following pages.")
        label.setWordWrap(True)
    
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(imgLabel)
        
        self.setLayout(layout)


class DetailsPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(DetailsPage, self).__init__(parent)
        
        self.setTitle("Plugin Details")
        self.setSubTitle("Please enter the following details about your new plugin.")
        
        self.state = PluginWizardGui.loadSettings()
                
        spacer = QtGui.QSpacerItem(40, 20)
        
        self.pluginIdLabel = QtGui.QLabel("<b>Plugin ID:</b>")
        
        self.pluginIdLineEdit = QtGui.QLineEdit()

        self.pluginNameLabel = QtGui.QLabel("<b>Plugin Name:</b>")
        
        self.pluginNameLineEdit = QtGui.QLineEdit()
    
        self.authorLabel = QtGui.QLabel("<b>Author:</b>")
        
        self.authorLineEdit = QtGui.QLineEdit()
        
        self.orgLabel = QtGui.QLabel("<b>Organization:</b>") 
               
        self.orgLineEdit = QtGui.QLineEdit()
        
        requiredLabel = QtGui.QLabel('ID and name are required. '
                                     'Author will be set to Unknown Author if empty.')
        requiredLabel.setWordWrap(True)
        infoLabel = QtGui.QLabel('You can obtain a unique ID from <a href="%s">www.plugincafe.com</a> '
                                 'or use <font color="maroon">%s</font> for testing purposes.' % 
                                 (PLUGINCAFE_GETID_LINK, PLUGIN_ID_TESTING))
        infoLabel.setOpenExternalLinks(True)
        infoLabel.setWordWrap(True)
        
        emptyLabel = QtGui.QLabel("")
            
        self.registerField("pluginId*", self.pluginIdLineEdit)
        self.registerField("pluginName*", self.pluginNameLineEdit)
        self.registerField("author", self.authorLineEdit)
        self.registerField("org", self.orgLineEdit)
                
        self.pluginIdLineEdit.setToolTip('You can use a whole number in the range 1000001-1000010 for testing purposes')

        pluginIdLineEditHelp = ('ID of the plugin. Must be a whole number starting from 1000001, \n'
                                'either obtained from Plugin Cafe as registered developer or a \n'
                                'number in the range 1000001-1000010 for testing purposes. \n' 
                                'Note that your plugin may fail to load if the ID is used by \n'
                                'another plugin which comes earlier in the loading order.')
        
        self.pluginIdLineEdit.setWhatsThis(pluginIdLineEditHelp)
        self.pluginIdLineEdit.setToolTip(pluginIdLineEditHelp)
                
        self.authorLineEdit.setToolTip('Will be set to Unknown Author if left empty')
        self.orgLineEdit.setToolTip('Can be empty')
        
        verticalLayout = QtGui.QVBoxLayout()
        
        labelsAndEditsLayout = QtGui.QGridLayout()
        
        labelsAndEditsLayout.addItem(spacer)

        labelsAndEditsLayout.addWidget(self.pluginIdLabel, 1, 0)
        labelsAndEditsLayout.addWidget(self.pluginIdLineEdit, 1, 1)
        labelsAndEditsLayout.addWidget(self.pluginNameLabel, 2, 0)
        labelsAndEditsLayout.addWidget(self.pluginNameLineEdit, 2, 1)
        labelsAndEditsLayout.addWidget(self.authorLabel, 3, 0)
        labelsAndEditsLayout.addWidget(self.authorLineEdit, 3, 1)
        labelsAndEditsLayout.addWidget(self.orgLabel, 4, 0)
        labelsAndEditsLayout.addWidget(self.orgLineEdit, 4, 1)
        labelsAndEditsLayout.addWidget(emptyLabel, 5, 0)
        
        verticalLayout.insertLayout(0, labelsAndEditsLayout)
        verticalLayout.addWidget(requiredLabel)
        verticalLayout.addWidget(infoLabel)
        
        self.setLayout(verticalLayout)
        
    def initializePage(self):  
        if 'pluginId' in self.state:
            self.setField("pluginId", self.state['pluginId'])
            self.pluginIdLineEdit.setText(self.state['pluginId'])
        else:
            self.setField("pluginId", CONFIG_DEFAULT['pluginId'])
            self.pluginIdLineEdit.setText(self.field("pluginId"))
 
        if 'pluginName' in self.state:
            self.setField("pluginName", self.state['pluginName'])
            self.pluginNameLineEdit.setText(self.state['pluginName'])
        else:
            self.setField("pluginName", CONFIG_DEFAULT['pluginName'])
            self.pluginNameLineEdit.setText(self.field("pluginName"))
 
        if 'author' in self.state:
            self.setField("author", self.state['author'])
            self.authorLineEdit.setText(self.state['author'])        
        elif DEFAULT_ENV_AUTHOR in os.environ:
            author = tryDecode(os.environ[DEFAULT_ENV_AUTHOR])
            self.setField("author", author)
            self.authorLineEdit.setText(author)
        else:
            author = tryDecode(CONFIG_DEFAULT['author'])
            self.setField("author", author)
            self.authorLineEdit.setText(author)
 
        if 'org' in self.state:
            self.setField("org", self.state['org'])
            self.orgLineEdit.setText(self.state['org'])                    
        elif DEFAULT_ENV_ORG in os.environ:
            self.setField("org", os.environ[DEFAULT_ENV_ORG])
            self.orgLineEdit.setText(os.environ[DEFAULT_ENV_ORG])
        else:
            self.setField("org", CONFIG_DEFAULT['org'])
            self.orgLineEdit.setText(CONFIG_DEFAULT['org'])
         

class TemplatePage(QtGui.QWizardPage):
    '''Template selection page.'''
    
    def __init__(self, parent=None):
        super(TemplatePage, self).__init__(parent)
        self.setTitle("Template Selector")
        self.setSubTitle("Select the template to use from the data directory. "
                         "By default the data directory is in the same location "
                         "as this wizard but you can select a different directory below.")

        self.state = PluginWizardGui.loadSettings()
        
        self.selectedTemplate = None
        self.selectedTemplatePath = None
        self.currentPath = None
        self.currentDir = None
        self.showTemplatePaths = False  # show full paths in a second column in templates table?

        if isValidPath(RESPATH):
            self.updatePath(RESPATH)
                
        browseButton = self.createButton("&Browse...", self.browse)
        browseButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        
        directoryLabel = QtGui.QLabel("Data Directory:")
        directoryLabel.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        
        self.directoryComboBox = self.createDirectoryComboBox()
        self.directoryComboBox.setSizeAdjustPolicy(2)
                
        self.helpButton = self.createButton("Template Help", self.help)
        self.helpButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        
        spacer = QtGui.QSpacerItem(40, 20)
        
        self.fileSystemModel = QtGui.QFileSystemModel()
        self.fileSystemModel.setReadOnly(True)
        self.fileSystemModel.setRootPath(self.currentPath)
        self.fileSystemModel.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        self.templateTree = self.createTemplateTree()
         
        self.templatesFoundLabel = QtGui.QLabel()
        self.templatesFoundLabel.setText("Select template folder (double click entry to open it)")
        
        self.registerField("dataDir", self.directoryComboBox)
                        
        mainLayout = QtGui.QVBoxLayout()
        
        gridLayout = QtGui.QGridLayout()
        gridLayout.addItem(spacer, 0, 0)
        gridLayout.addWidget(directoryLabel, 1, 0)
        gridLayout.addWidget(self.directoryComboBox, 1, 1)
        gridLayout.addWidget(browseButton, 1, 2)
        
        mainLayout.insertLayout(0, gridLayout)
        mainLayout.addWidget(self.templateTree)
        
        bottomLayout = QtGui.QHBoxLayout()
        
        bottomLayout.addWidget(self.templatesFoundLabel)
        bottomLayout.addWidget(self.helpButton)
        
        mainLayout.addLayout(bottomLayout)
        
        self.setLayout(mainLayout)
        
        self.updateTemplateTree()
        
    def initializePage(self, *args, **kwargs):
        if 'srcdataPath' in self.state:
            dataDir = self.state['srcdataPath']
        elif DEFAULT_ENV_DATA in os.environ:
            dataDir = tryDecode(os.environ[DEFAULT_ENV_DATA])
        else:
            #dataDir = canonicalizePath(os.path.realpath(os.path.join(RESPATH, CONFIG_DEFAULT['srcdataPath'])))
            dataDir = CONFIG_DEFAULT['srcdataPath']
        if dataDir[0] == os.path.sep:
            # remove preeceeding path sep but only if dataDir as fetched isn't 
            # representing a valid path to a folder. This is to guard for the fact 
            # that the user will probably supply absolute paths rooted at the main
            # root '/' and we don't want to clobber those paths.
            if not os.path.isdir(dataDir) and os.path.isdir(dataDir[1:]):
                dataDir = dataDir[1:]                
        self.updateComboBox(self.directoryComboBox, dataDir)
       
    def updateSelectedTemplate(self, idx=None):  # IGNORE:W0613
        try:
            if idx is None:
                idx = self.templateTree.currentIndex()
            self.selectedTemplate = self.fileSystemModel.fileName(idx)
            self.selectedTemplatePath = self.fileSystemModel.filePath(idx)
            return True
        except:
            return False
        
    def updateTemplateTree(self):
        path = self.getPathFromDirectoryComboBox()
        if path is None:
            return
        self.fileSystemModel.setRootPath(path)
        self.templateTree.setRootIndex(self.fileSystemModel.index(path))
    
    def updatePath(self, path):
        isValid = isValidPath(path)
        if isValid:
            self.currentPath = os.path.realpath(path)
            self.currentDir = QtCore.QDir(self.currentPath)

    def updateComboBox(self, comboBox, newValue=None):
        if newValue is None:
            newValue = comboBox.currentText()
        self.state['srcdataPath'] = newValue
        if (comboBox.findText(newValue) == -1 and 
            comboBox.findText(newValue + os.sep) == -1 and
            comboBox.findText(newValue[:-1]) == -1):
            if newValue[-1] == os.sep:
                comboBox.addItem(newValue[:-1])
            else:
                comboBox.addItem(newValue)
        elif comboBox.findText(newValue) != -1:
            comboBox.setCurrentIndex(comboBox.findText(newValue))
        
    def getPathForTemplate(self, template=None):
        if template is None and self.selectedTemplate is None:
            return None
        else:
            return self.fileSystemModel.filePath(self.templateTree.currentIndex())
    
    def getPathFromDirectoryComboBox(self):
        try:
            entry = self.directoryComboBox.itemText()
        except TypeError:
            # not sure if this is wise to return current path here
            # if asked for the current entry; as this is technically not
            # the correct answer...
            entry = self.currentPath
        if os.path.exists(entry) and os.path.isdir(entry):
            fullpath = canonicalizePath(os.path.realpath(entry))
            self.updatePath(fullpath)
            return fullpath
        return None
    
    def getSrcdataPathFromField(self):
        return self.directoryComboBox.itemText(self.field("srcdataPath"))

    def help(self):
        window = HelpWindow()
        window.resize(QtCore.QSize(500, 500))
        window.show()
        window.exec_()
        
    def browse(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, "Select Data Directory", 
                                                           self.directoryComboBox.itemText(self.field("dataDir")))
        directory = canonicalizePath(directory)
        if directory:
            self.updateComboBox(self.directoryComboBox, newValue=directory)
            #self.directoryComboBox.setCurrentIndex(self.directoryComboBox.findText(directory))
        
        self.updatePath(directory)
        self.updateTemplateTree()
        
    def openTemplateFolder(self, idx=None):
        if idx is None:
            idx = self.templateTree.currentIndex()
        self.selectedTemplate = self.fileSystemModel.fileName(idx)
        self.selectedTemplatePath = self.fileSystemModel.filePath(idx)
        openPath(self.selectedTemplatePath)
            
    def createButton(self, text, member):
        button = QtGui.QPushButton(text)
        button.clicked.connect(member)
        return button
    
    def dataDirTextEdited(self, *args, **kwargs):
        newDir = args[0]
        if isValidPath(newDir):
            self.updatePath(newDir)
            self.updateTemplateTable()
            self.updateComboBox(self.directoryComboBox, newValue=newDir)
            
    def dataDirIndexChanged(self, *args, **kwargs):
        newIndex = args[0]
        newPath = self.directoryComboBox.itemText(newIndex)
        self.updatePath(newPath)
        self.updateTemplateTree()

    def createDirectoryComboBox(self, text=None):
        comboBox = QtGui.QComboBox()
        comboBox.setEditable(True)
        if text is not None:
            comboBox.addItem(text)
        comboBox.setMinimumContentsLength(30)
        comboBox.lineEdit().textEdited.connect(self.dataDirTextEdited)
        comboBox.currentIndexChanged.connect(self.dataDirIndexChanged)
        comboBoxHelp = ("Select the data directory to look for templates in.\n\n"
                        "By default, this will be a directory named data_python \n"
                        "in the same location as the main program.")
        comboBox.setWhatsThis(comboBoxHelp)
        comboBox.setToolTip(comboBoxHelp)
        return comboBox
    
    def createTemplateTree(self):
        
        templateTree = QtGui.QTreeView()
        templateTree.setSortingEnabled(True)
        templateTree.setModel(self.fileSystemModel)
        templateTree.setRootIndex(self.fileSystemModel.index(self.currentPath))

        templateTree.clicked.connect(self.updateSelectedTemplate)
        templateTree.activated.connect(self.openTemplateFolder)
        
        templateTree.setWhatsThis("Select the template to use. A template is a folder containing "
                                   "the files and directory structure needed for one type of plugin. "
                                   "Press Template Help to view a complete introduction to templates.")
        return templateTree
    
    
class ConclusionPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(ConclusionPage, self).__init__(parent)
                
        self.setTitle("Confirmation")
        
        self.state = PluginWizardGui.loadSettings()
        
        label = QtGui.QLabel("Please verify that the following info is correct. Be very conscious about "
                             "the template path and the destination dir since no additional checks are "
                             "performed.\n\n"
                             "Press 'Done' to create your new plugin.")
        label.setWordWrap(True)
            
        self.browser = QtGui.QTextBrowser()

        spacer = QtGui.QSpacerItem(40, 20)

        browseButton = self.createButton("&Browse...", self.browse)
        browseButton.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        
        directoryLabel = QtGui.QLabel("Destination Dir:")
        directoryLabel.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)

        self.destinationPath = canonicalizePath(QtCore.QDir.homePath())
        self.destinationDir = QtCore.QDir(self.destinationPath)
        
        self.directoryComboBox = self.createDirectoryComboBox(self.destinationPath)
        directoryComboBoxHelp = "Select a destination directory where the new plugin should be stored."
        self.directoryComboBox.setWhatsThis(directoryComboBoxHelp)
        self.directoryComboBox.setToolTip(directoryComboBoxHelp)
        
        self.overwriteCheckBox = self.createCheckBox("Overwrite?", self.updateOverwrite)
        overwriteCheckBoxHelp = "Check to overwrite existing plugins with the same name in the destination directory."
        self.overwriteCheckBox.setWhatsThis(overwriteCheckBoxHelp)
        self.overwriteCheckBox.setToolTip(overwriteCheckBoxHelp)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(label)
        mainLayout.addItem(spacer)
        mainLayout.addWidget(self.browser)
                
        gridLayout = QtGui.QGridLayout()
        gridLayout.addItem(spacer, 0, 0)
        gridLayout.addWidget(directoryLabel, 1, 0)
        gridLayout.addWidget(self.directoryComboBox, 1, 1)
        gridLayout.addWidget(browseButton, 1, 2)
        gridLayout.addWidget(self.overwriteCheckBox, 2, 1)
        
        mainLayout.insertLayout(3, gridLayout)
        
        self.registerField("destinationPath", self.directoryComboBox)
        self.registerField("overwrite", self.overwriteCheckBox)
                    
        self.setLayout(mainLayout)
         
    def initializePage(self):
        if DEBUG: print("initialize Conclusion page")
          
        self.updateBrowserText()
 
        if 'overwrite' in self.state and self.state['overwrite'] is not None:
            self.setField("overwrite", self.state['overwrite'])
            self.overwriteCheckBox.setChecked(bool(self.state['overwrite']))
        else:
            self.setField("overwrite", False) # default value
            self.overwriteCheckBox.setChecked(bool(self.field('overwrite')))
 
        if ('destinationPath' in self.state and 
            self.state['destinationPath'] is not None):
            comboBox = self.directoryComboBox
            destinationPath = self.state['destinationPath']
            comboBox.setEditText(destinationPath)
            self.updateComboBox(comboBox, destinationPath)
            self.updatePath(destinationPath)
            comboBox.setCurrentIndex(comboBox.findText(destinationPath))

        
    def updatePath(self, path): 
        if isValidPath(path):
            self.destinationPath = os.path.realpath(path)
            self.destinationDir = QtCore.QDir(self.destinationPath)

    def updateOverwrite(self): 
        isChecked = self.overwriteCheckBox.isChecked()
        self.setField('overwrite', isChecked)
        self.state['overwrite'] = isChecked
        # if DEBUG: print("self.field(overwrite) = %s" % self.field("overwrite"))

    def updateBrowserText(self):
        self.browser.setText(self.makeDetailsText())
        
    def updateComboBox(self, comboBox, newValue=None):
        if newValue is None:
            newValue = comboBox.currentText()
        self.state['destinationPath'] = newValue
        if (comboBox.findText(newValue) == -1 and 
            comboBox.findText(newValue + os.sep) == -1 and
            comboBox.findText(newValue[:-1]) == -1):
            if newValue[-1] == os.sep:
                comboBox.addItem(newValue[:-1])
            else:
                comboBox.addItem(newValue)
        elif comboBox.findText(newValue) != -1:
            comboBox.setCurrentIndex(comboBox.findText(newValue))
    
    def destDirTextEdited(self, *args, **kwargs):
        newDir = args[0]
        if isValidPath(newDir):
            self.updatePath(newDir)
            self.updateBrowserText()
            self.updateComboBox(self.directoryComboBox)
            
    def destDirIndexChanged(self, *args, **kwargs):
        newIndex = args[0]
        newPath = self.directoryComboBox.itemText(newIndex)
        self.updatePath(newPath)
        self.updateBrowserText()
        #self.updateComboBox(self.directoryComboBox)
        #if DEBUG: print("self.destinationPath = %s" % self.destinationPath)
        
    def createDirectoryComboBox(self, text=None):
        comboBox = QtGui.QComboBox()
        comboBox.setEditable(True)
        if text is not None:
            comboBox.addItem(text)
        #comboBox.setMinimumContentsLength(40)
        comboBox.lineEdit().textEdited.connect(self.destDirTextEdited)
        comboBox.currentIndexChanged.connect(self.destDirIndexChanged)
        return comboBox

    def createButton(self, text, member):
        button = QtGui.QPushButton(text)
        button.clicked.connect(member)
        return button
    
    def createCheckBox(self, text, member):
        checkBox = QtGui.QCheckBox(text)
        checkBox.clicked.connect(member)
        return checkBox
    
    def getDestinationPathFromField(self):
        return self.directoryComboBox.itemText(self.field("destinationPath"))
        
    def browse(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self, "Select Destination Directory", self.getDestinationPathFromField())
        directory = canonicalizePath(directory)
        if directory:
            self.updateComboBox(self.directoryComboBox, newValue=directory)
            self.directoryComboBox.setCurrentIndex(self.directoryComboBox.findText(directory))
        
        self.updatePath(directory)
           
    def makeDetailsText(self):
        idtxt = "<b>Plugin ID:</b> %s<br>" % self.field("pluginId")
        nametxt = "<b>Plugin Name:</b> %s<br>" % self.field("pluginName")
        authortxt = "<b>Author:</b> %s<br>" % self.field("author")
        orgtxt = "<b>Organization:</b> %s<br>" % self.field("org")
        templatePage = self.wizard().page(2)
        templatetxt = "<b>Template:</b> %s<br>" % templatePage.selectedTemplate
        fullpath = os.path.join(os.path.realpath(templatePage.currentPath), templatePage.selectedTemplate)
        templatepathtxt = "<b>Template Path:</b> %s<br>" % fullpath
        return (idtxt + nametxt + authortxt + orgtxt + templatetxt + templatepathtxt)



class HelpWindow(QtGui.QDialog):
    
    def __init__(self):
        super(HelpWindow, self).__init__()
        self.textEdit = QtGui.QTextEdit()
        self.setupGui()
        self.setWindowTitle("Template Help")

    def setupGui(self):
        self.textEdit.setHtml(TEMPLATE_HELP_STYLED)
        self.textEdit.setReadOnly(True)
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.textEdit)

        self.setLayout(mainLayout)
        

def main(argv=None):  # IGNORE:C0111
    if isinstance(argv, list):
        sys.argv.extend(argv)
    
    try:
        app = QtGui.QApplication(sys.argv)
        
        translatorFileName = "qt_"
        translatorFileName += QtCore.QLocale.system().name()
        
        translator = QtCore.QTranslator(app)
        
        if (translator.load(translatorFileName, 
                            QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))):
            app.installTranslator(translator)
            
        wizard = PluginWizardGui()
        wizard.setWindowTitle("CINEMA 4D Plugin Wizard")
        wizard.window().setStyleSheet("QWizard { background: white; }")
        
        wizard.show()
        
        if g_osx:
            w = 725
            h = 425
            wizard.setMinimumSize(w, h)
            wizard.window().resize(w, h)
            wizard.setPixmap(QtGui.QWizard.BackgroundPixmap, QtGui.QPixmap("images/c4dr14bg.png"))
        else:
            w = 525
            h = 425
            wizard.setMinimumSize(w, h)
            wizard.window().resize(w, h)
        
        return app.exec_()
    
    except KeyboardInterrupt:
        return 0
    except CLIError as e:
        print(e)
        return 1
    except Exception as e:
        if DEBUG or TESTRUN:
            raise(e)
        sys.stderr.write("%s: %s%s" % (sys.argv[0].split("/")[-1], str(e), os.linesep))
        sys.stderr.write("\t for help use --help")
        return 2

RESPATH = os.curdir 

if __name__ == "__main__":
    if TESTRUN:
        import doctest
        doctest.testmod()
    if DEBUG:
        #os.environ[DEFAULT_ENV_AUTHOR] = u"André Berg"
        #os.environ[DEFAULT_ENV_ORG] = u"Iris VFX"
        main(sys.argv)
        sys.exit(0)
    if PROFILE:
        import cProfile
        import pstats
        os.environ[DEFAULT_ENV_DATA] = "../tests/data"
        os.environ[DEFAULT_ENV_AUTHOR] = "Andre Berg"
        os.environ[DEFAULT_ENV_ORG] = "Iris VFX"
        profile_filename = 'gui_profile.pstats'
        cProfile.run('main()', profile_filename)
        statsfile = open("gui_profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        print(stats.print_stats(), file=statsfile)
        statsfile.close()
        sys.exit(0)
    #if sys.platform == "darwin" and hasattr(sys, "_MEIPASS"):
    #    # running from a PyInstaller 2.0 created onefile binary app
    #    # change the current directory to the Resources folder of the app bundle
    #    resourcesPath = os.path.realpath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'Resources'))
    #    os.chdir(resourcesPath)
    #    QtCore.QDir.setCurrent(resourcesPath)
    #    RESPATH = resourcesPath
    sys.exit(main())
