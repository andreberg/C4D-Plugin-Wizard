// -*- coding: ${ENCODING}  -*-
//
//  %!PluginNameAsID!%.cpp
//  %!PluginName!%
//
//  Created by %!AuthorName!% on ${DATE}.
//  Copyright ${YEAR} %!OrgName!%. All rights reserved.
//

#include "c4d.h"
#include "c4d_symbols.h"
#include "%!PluginNameAsID!%.h"

#define DEFAULT_COLOR Vector(0.5)

class %!PluginNameAsID!%Data : public ShaderData {

    private:
        Vector color;

    public:
        virtual Bool Init(GeListNode * node);
        virtual Vector Output(BaseShader * chn, ChannelData * cd);

        virtual INITRENDERRESULT InitRender(BaseShader * sh, const InitRenderStruct& irs);
        virtual void FreeRender(BaseShader * sh);

        static NodeData * Alloc(void) { return NewObjClear(%!PluginNameAsID!%Data); }
};

Bool %!PluginNameAsID!%Data::Init(GeListNode * node) {

    BaseContainer * data = ((BaseShader *)node)->GetDataInstance();

    data->SetVector(%!PluginNameAsUppercaseID!%_COLOR, DEFAULT_COLOR);

    return true;
}

INITRENDERRESULT %!PluginNameAsID!%Data::InitRender(BaseShader * sh, const InitRenderStruct& irs) {

    BaseContainer * data = sh->GetDataInstance();

    color = data->GetVector(%!PluginNameAsUppercaseID!%_COLOR);

    return INITRENDERRESULT_OK;
}

void %!PluginNameAsID!%Data::FreeRender(BaseShader * sh) {
    // free owned memory here
}

Vector %!PluginNameAsID!%Data::Output(BaseShader * chn, ChannelData * cd) {

    Vector col = color;

    return col;
}

// be sure to use a unique ID obtained from www.plugincafe.com
#define ID_%!PluginNameAsUppercaseID!%   %!ID!%

Bool Register_%!PluginNameAsID!%(void) {
    return RegisterShaderPlugin(ID_%!PluginNameAsUppercaseID!%, GeLoadString(IDS_%!PluginNameAsUppercaseID!%), 0, %!PluginNameAsID!%Data::Alloc, "%!PluginNameAsID!%", 0);
}

