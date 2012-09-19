# -*- coding: utf-8  -*-
# 
#  MakeAwesomeButton.pyp
#  CINEMA 4D Python Plugins
#  
#  Created by Andre Berg on 2011-05-05.
#  Copyright 2011 Berg Media. All rights reserved.
#  
#  Version 0.1
#  Updated: 2011-05-05
#
#  Summary: 
# 
#  Modus Operandi:
#  STEPS 
#
#  OTHER_NOTES 
#  
#

import os
import c4d
from c4d import plugins, bitmaps, gui, documents
# from c4d.utils import *

DEBUG = True

if DEBUG:
    import pprint
    pp = pprint.PrettyPrinter(width=200)
    PP = pp.pprint
    PF = pp.pformat


# -------------------------------------------
#                GLOBALS 
# -------------------------------------------

PLUGIN_NAME    = "Make Awesome Button"
PLUGIN_VERSION = 0.1
PLUGIN_HELP    = <HelpString>
PLUGIN_ABOUT   = """(C) 2011 Andre Berg (Berg Media)
All rights reserved.

Use at your own risk! 

It is recommended to try out the plugin 
on a spare copy of your data first.
"""

# -------------------------------------------
#               PLUGING IDS 
# -------------------------------------------

# unique ID
ID_MAKEAWESOMEBUTTON = 1000003


# Element IDs
IDD_DIALOG_SETTINGS      = 10001
IDC_BUTTON_CANCEL        = 10002
IDC_BUTTON_DOIT          = 10003
IDC_GROUP_WRAPPER        = 10004
IDC_GROUP_SETTINGS       = 10005
IDC_GROUP_BUTTONS        = 10006
IDC_DUMMY                = 10007
IDC_MENU_ABOUT           = 30001

# String IDs
IDS_DIALOG_TITLE   = PLUGIN_NAME
IDS_MENU_INFO      = "Info"
IDS_MENU_ABOUT     = "About..."


# ------------------------------------------------------
#                   User Interface 
# ------------------------------------------------------
class MakeAwesomeButtonDialog(gui.GeDialog):
    
    def CreateLayout(self):
        self.SetTitle(IDS_DIALOG_TITLE)
        
        plugins.GeResource().Init(os.path.dirname(os.path.abspath(__file__)))
        self.LoadDialogResource(IDD_DIALOG_SETTINGS, flags=c4d.BFH_SCALEFIT)
        
        # Menu
        self.MenuFlushAll()
        self.MenuSubBegin(IDS_MENU_INFO)
        self.MenuAddString(IDC_MENU_ABOUT, IDS_MENU_ABOUT)
        self.MenuSubEnd()
        
        self.MenuFinished()
        
        return True
    
    def InitValues(self):
        # TODO: set default values (or read from config.ini)        
        return True
    
    def Command(self, id, msg):
        if id == IDC_BUTTON_DOIT:
            scriptvars = {
                # TODO: get scriptvars from current ui values
            }
            script = MakeAwesomeButtonScript(scriptvars)
            if DEBUG:
                print "do it: %r" % msg
                print "script = %r" % script
                print "scriptvars = %r" % scriptvars
            return script.run()
        elif id == IDC_BUTTON_CANCEL:
            if DEBUG:
                print "cancel: %r" % msg
            self.Close()
        elif id == IDC_MENU_ABOUT:
            c4d.gui.MessageDialog(PLUGIN_ABOUT)
        else:
            if DEBUG:
                print "id = %s" % id
        
        return True
    


# ------------------------------------------------------
#                   Command Script 
# ------------------------------------------------------
class MakeAwesomeButtonScript(object):
    """Run when the user clicks the OK button."""
    def __init__(self, scriptvars=None):
        super(MakeAwesomeButtonScript, self).__init__()
        self.data = scriptvars
    
    def run(self):
        doc = documents.GetActiveDocument()
        doc.StartUndo()
        
        sel = doc.GetSelection()
        if sel is None: return False
        
        c4d.StatusSetSpin()
        timestart = c4d.GeGetMilliSeconds()
                
        # very important!
        c4d.StopAllThreads()
        
        # loop through all objects
        for op in sel:
            print op.GetName()
            # and do something with op #
        
        c4d.StatusClear()
        
        # tell C4D to update internal state  
        c4d.EventAdd() 
        doc.EndUndo()
        
        timeend = int(c4d.GeGetMilliSeconds() - timestart)
        timemsg = "MakeAwesomeButton: finished in " + str(timeend) + " milliseconds"
        print timemsg
        
        return True
    

# ----------------------------------------------------
#                      Main 
# ----------------------------------------------------
class MakeAwesomeButtonMain(plugins.CommandData):
    dialog = None
    def Execute(self, doc):
        # create the dialog
        if self.dialog is None:
            self.dialog = MakeAwesomeButtonDialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=ID_MAKEAWESOMEBUTTON)
    
    def RestoreLayout(self, secref):
        # manage nonmodal dialog
        if self.dialog is None:
            self.dialog = <Plugin>Dialog()
        return self.dialog.Restore(pluginid=ID_MAKEAWESOMEBUTTON, secret=secref)
    


if __name__ == "__main__":
    thispath = os.path.dirname(os.path.abspath(__file__))
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(thispath, "res", "icon.tif"))
    plugins.RegisterCommandPlugin(
        ID_MAKEAWESOMEBUTTON, 
        PLUGIN_NAME, 
        0, 
        icon, 
        PLUGIN_HELP, 
        MakeAwesomeButtonMain()
    )
    print "%s v%.1f loaded. (C) 2011 Andre Berg" % (PLUGIN_NAME, PLUGIN_VERSION)


# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and