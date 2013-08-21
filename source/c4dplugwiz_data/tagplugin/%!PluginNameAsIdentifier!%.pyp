# -*- coding: ${ENCODING}  -*-
# 
#  %!PluginNameAsIdentifier!%.pyp
#  CINEMA 4D Python Tag Plugins
#  
#  Created by ${FULLNAME} on ${DATE}.
#  Copyright ${YEAR} ${ORGANIZATION_NAME}. All rights reserved.
#  
#  Version 0.1
#  Updated: ${DATE}
#
#  Summary: 
# 
#  How It Works:
#  STEPS 
#
#  OTHER_NOTES 
#  

"""
Name-US:%!PluginName!%
Description-US:Execute the %!PluginName!% plugin.
"""

import os
import time

__version__ = (0, 1)
__date__ = '${DATE}'
__updated__ = '${DATE}'


DEBUG = 1 or ('DebugLevel' in os.environ and os.environ['DebugLevel'] > 0)
TESTRUN = 0 or ('TestRunLevel' in os.environ and os.environ['TestRunLevel'] > 0)

if DEBUG:
    import pprint
    pp = pprint.PrettyPrinter(width=200)
    PP = pp.pprint
    PF = pp.pformat

try:
    import c4d  # @UnresolvedImport
    from c4d import plugins, bitmaps, gui, documents
    #from c4d.utils import *
except ImportError:
    if TESTRUN == 1:
        pass

CR_YEAR = time.strftime("%Y")


# -------------------------------------------
#                GLOBALS 
# -------------------------------------------

PLUGIN_NAME    = u"""%!PluginName!%"""
PLUGIN_VERSION = '.'.join(str(x) for x in __version__)
PLUGIN_HELP    = u"""Execute the %!PluginName!% plugin."""
PLUGIN_ABOUT   = u"""(C) %s ${FULLNAME} (${ORGANIZATION_NAME})
All rights reserved.

Version %s 

Use at your own risk! 

It is recommended to try out the plugin 
on a spare copy of your data first.
""" % (CR_YEAR, PLUGIN_VERSION)

# -------------------------------------------
#               PLUGING IDS 
# -------------------------------------------

# unique ID
ID_%!PluginNameAsUppercaseIdentifier!% = %!ID!%


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
class %!PluginNameAsIdentifier!%Dialog(gui.GeDialog):
    
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
            script = %!PluginNameAsIdentifier!%Script(scriptvars)
            if DEBUG:
                print("do it: %r" % msg)
                print("script = %r" % script)
                print("scriptvars = %r" % scriptvars)
            return script.run()
        elif id == IDC_BUTTON_CANCEL:
            if DEBUG:
                print("cancel: %r" % msg)
            self.Close()
        elif id == IDC_MENU_ABOUT:
            c4d.gui.MessageDialog(PLUGIN_ABOUT)
        else:
            if DEBUG:
                print("id = %s" % id)
        
        return True
    

# ------------------------------------------------------
#                   Command Script 
# ------------------------------------------------------

class %!PluginNameAsIdentifier!%Script(object):
    """Run when the user clicks the OK button."""
    def __init__(self, scriptvars=None):
        super(%!PluginNameAsIdentifier!%Script, self).__init__()
        self.data = scriptvars
    
    def run(self):
        doc = documents.GetActiveDocument()
        doc.StartUndo()
        
        sel = doc.GetSelection()
        if sel is None: return False
        
        c4d.StatusSetSpin()
        timestart = c4d.GeGetMilliSeconds()
                
        c4d.StopAllThreads()
        
        # loop through all objects
        for op in sel:
            print op.GetName()
            # and do something with op #
            op.Message(c4d.MSG_UPDATE)
        
        c4d.StatusClear()
        
        # tell C4D to update internal state  
        c4d.EventAdd() 
        doc.EndUndo()
        
        timeend = int(c4d.GeGetMilliSeconds() - timestart)
        timemsg = u"%!PluginNameAsIdentifier!%: finished in " + str(timeend) + " milliseconds"
        print(timemsg)
        
        return True
    

# ----------------------------------------------------
#                      Main 
# ----------------------------------------------------

class %!PluginNameAsIdentifier!%Main(plugins.CommandData):
    
    dialog = None
    
    def Execute(self, doc):
        # create the dialog
        if self.dialog is None:
            self.dialog = %!PluginNameAsIdentifier!%Dialog()
        return self.dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=ID_%!PluginNameAsUppercaseIdentifier!%)
    
    def RestoreLayout(self, secref):
        # manage nonmodal dialog
        if self.dialog is None:
            self.dialog = %!PluginNameAsIdentifier!%Dialog()
        return self.dialog.Restore(pluginid=ID_%!PluginNameAsUppercaseIdentifier!%, secret=secref)


if __name__ == "__main__":
    thispath = os.path.dirname(os.path.abspath(__file__))
    icon = bitmaps.BaseBitmap()
    icon.InitWith(os.path.join(thispath, "res", "icon.png"))
    plugins.RegisterCommandPlugin(
        ID_%!PluginNameAsUppercaseIdentifier!%, 
        PLUGIN_NAME, 
        0, 
        icon, 
        PLUGIN_HELP, 
        %!PluginNameAsIdentifier!%Main()
    )
    print(u"%s v%s loaded. (C) %s ${FULLNAME}" % (PLUGIN_NAME, PLUGIN_VERSION, CR_YEAR))


${LICENSE}
