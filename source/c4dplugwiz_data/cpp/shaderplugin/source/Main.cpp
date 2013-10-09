// -*- coding: ${ENCODING}  -*-
// 
//  Main.cpp
//  %!PluginName!%
//  
//  Created by %!AuthorName!% on ${DATE}.
//  Copyright ${YEAR} %!OrgName!%. All rights reserved.
//  

// Starts the plugin registration

#include "c4d.h"
#include <string.h>

// forward declarations
Bool Register_%!PluginNameAsID!%(void);

Bool PluginStart(void) {

    if (!Register_%!PluginNameAsID!%()) {
        return false;
    }

    GePrint("%!PluginName!%, %!AuthorName!% ${YEAR}.");
    
    return true;
}

void PluginEnd(void) {
}

Bool PluginMessage(Int32 id, void * data) {
    
    switch (id) {
        case C4DPL_INIT_SYS:
            if (!resource.Init()) { // don't start plugin without resource
                return false;
            }
            return true;

        case C4DMSG_PRIORITY:
            return true;

        case C4DPL_BUILDMENU:
            break;

    }

    return false;
}
