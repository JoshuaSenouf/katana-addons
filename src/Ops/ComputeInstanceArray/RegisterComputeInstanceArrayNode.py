def registerComputeInstanceArray():
    from Katana import Nodes3DAPI
    from Katana import FnAttribute
    from Katana import FnGeolibServices

    def buildComputeInstanceArrayOpChain(node, interface):
        frameTime = interface.getGraphState().getTime()
        interface.setMinRequiredInputs(1)
        argsGb = FnAttribute.GroupBuilder()

        instanceArrayLocParam = node.getParameter("instanceArrayLoc")
        loadingModeParam = node.getParameter("loadingMode")
        positionPrimvarParam = node.getParameter("positionPrimvar")
        rotationPrimvarParam = node.getParameter("rotationPrimvar")
        scalePrimvarParam = node.getParameter("scalePrimvar")
        protoIndicesPrimvarParam = node.getParameter("protoIndicesPrimvar")

        if instanceArrayLocParam:
            argsGb.set("instanceArrayLoc", instanceArrayLocParam.getValue(frameTime))
        if loadingModeParam:
            argsGb.set("loadingMode", loadingModeParam.getValue(frameTime))
        if positionPrimvarParam:
            argsGb.set("positionPrimvar", positionPrimvarParam.getValue(frameTime))
        if rotationPrimvarParam:
            argsGb.set("rotationPrimvar", rotationPrimvarParam.getValue(frameTime))
        if scalePrimvarParam:
            argsGb.set("scalePrimvar", scalePrimvarParam.getValue(frameTime))
        if protoIndicesPrimvarParam:
            argsGb.set("protoIndicesPrimvar", protoIndicesPrimvarParam.getValue(frameTime))

        interface.addOpSystemArgs(argsGb)

        if loadingModeParam.getValue(frameTime) == "during op resolve":
            attrSetBuilder = FnGeolibServices.OpArgsBuilders.AttributeSet()
            attrSetBuilder.setCEL([instanceArrayLocParam.getValue(frameTime)])
            attrSetBuilder.setAttr("ops.{name}".format(name = node.getName()),
                FnAttribute.GroupBuilder()
                .set("opType", "ComputeInstanceArray")
                .set("opArgs", argsGb.build())
                .set("resolveIds", "PrmanInstanceArray")
                .build())
        elif loadingModeParam.getValue(frameTime) == "immediate":
            interface.appendOp("ComputeInstanceArray", argsGb.build())
        else:
            interface.appendOp("ComputeInstanceArray", argsGb.build())


    nodeTypeBuilder = Nodes3DAPI.NodeTypeBuilder("ComputeInstanceArray")
    nodeTypeBuilder.setInputPortNames(("input",))
    nodeTypeBuilder.setIsHiddenFromMenus(True)

    gb = FnAttribute.GroupBuilder()
    gb.set("instanceArrayLoc", FnAttribute.StringAttribute("/root/world/geo/instanceArray"))
    gb.set("loadingMode", FnAttribute.StringAttribute("during op resolve"))
    gb.set("positionPrimvar", FnAttribute.StringAttribute("P"))
    gb.set("rotationPrimvar", FnAttribute.StringAttribute("rotationPP"))
    gb.set("scalePrimvar", FnAttribute.StringAttribute("scalePP"))
    gb.set("protoIndicesPrimvar", FnAttribute.StringAttribute("objectId"))

    nodeTypeBuilder.setParametersTemplateAttr(gb.build())
    nodeTypeBuilder.setHintsForParameter("instanceArrayLoc",
        {"label" : "Instance Array Location",
        "help" : "The scenegraph location where the instance array will be stored.",
        "widget": "scenegraphLocation"})
    nodeTypeBuilder.setHintsForParameter("loadingMode",
        {"label" : "Loading Mode",
        "help" : "Give the user the ability to choose when to actually compute the instance array,\
        i.e. during op resolve or immediately. The former option is used by default as waiting for op resolve\
        can help bringing the expansion time as close to zero as possible. The user will also not really be impacted\
        by such a deffered computation of the data as instanceIndex/instanceMatrix(/omitList) will be useful to PRMan\
        only most of the time.",
        "widget": "popup",
        "options": ["during op resolve", "immediate"]})
    nodeTypeBuilder.setHintsForParameter("positionPrimvar",
        {"label" : "Position",
        "help" : "The name of the primvar holding the position information of the instances."})
    nodeTypeBuilder.setHintsForParameter("rotationPrimvar",
        {"label" : "Rotation",
        "help" : "The name of the primvar holding the rotation information of the instances."})
    nodeTypeBuilder.setHintsForParameter("scalePrimvar",
        {"label" : "Scale",
        "help" : "The name of the primvar holding the scale information of the instances."})
    nodeTypeBuilder.setHintsForParameter("protoIndicesPrimvar",
        {"label" : "Prototype Indices",
        "help" : "The name of the primvar holding the index information of the instances."})

    nodeTypeBuilder.setBuildOpChainFnc(buildComputeInstanceArrayOpChain)
    nodeTypeBuilder.build()

registerComputeInstanceArray()
