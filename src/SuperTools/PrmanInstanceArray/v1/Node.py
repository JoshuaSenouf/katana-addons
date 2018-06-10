from Katana import NodegraphAPI
from Katana import Nodes3DAPI
from Katana import GeoAPI

import OpScripts as OS
import ScriptActions as SA
import logging

log = logging.getLogger("PrmanInstanceArray.Node")


class PrmanInstanceArrayNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.addInputPort("input")
        self.addOutputPort("output")

        self.abcGeoPathsList = []
        self.abcScatterScenegraphLocation = ""
        
        self.getParameters().createChildString("instanceArrayLoc", "/root/world/geo/instanceArray")
        self.getParameters().createChildString("instanceSourcesLoc", "/root/world/geo/instanceSources")
        self.getParameters().createChildString("abcScatterPath", "")
        self.getParameters().createChildString("abcGeoPaths", "")
        self.getParameters().createChildString("loadingMode", "during op resolve")

        self.getParameters().createChildNumber("scatterDensity", 100)

        self.getParameters().createChildString("positionPrimvar", "P")
        self.getParameters().createChildString("rotationPrimvar", "rotationPP")
        self.getParameters().createChildString("scalePrimvar", "scalePP")
        self.getParameters().createChildString("protoIndicesPrimvar", "objectId")
        self.getParameters().createChildString("idsPrimvar", "particleId")
        self.getParameters().createChildString("velocityPrimvar", "velocity")
        self.getParameters().createChildString("angularVelocityPrimvar", "angularVelocity")

        self.getParameters().createChildNumber("useMotionBlur", 0)
        self.getParameters().createChildNumber("intensityMultiplier", 1)

        self.__buildDefaultNetwork()

    def __buildDefaultNetwork(self):
        self.abcGeoPathsList = (self.getParameterValue("abcGeoPaths", 1).split("|")
            if self.getParameterValue("abcGeoPaths", 1) else [])

        mergeInputs_Node = self.mergeInputsNode()
        abcScatter_Node = self.abcScatterNode()
        createABCSources_Node = self.createABCSourcesNode()
        setInstanceSourceType_Node = self.setInstanceSourceTypeNode()
        instanceArraySetup_Node = self.instanceArraySetupNode()
        previewPointCloudSetup_Node = self.previewPointCloudSetupNode()
        computeInstanceArray_Node = self.computeInstanceArrayNode()
        scatterDensityControl_Node = self.scatterDensityControlNode()
        deleteInstanceArrayChildren_Node = self.deleteInstanceArrayChildrenNode()

        self.getSendPort(self.getInputPortByIndex(0).getName()).connect(mergeInputs_Node.getInputPort("inputScene"))

        abcScatter_Node.getOutputPortByIndex(0).connect(mergeInputs_Node.getInputPort("inputScatter"))
        createABCSources_Node.getOutputPortByIndex(0).connect(mergeInputs_Node.getInputPort("inputGeometry"))
        mergeInputs_Node.getOutputPortByIndex(0).connect(setInstanceSourceType_Node.getInputPortByIndex(0))
        setInstanceSourceType_Node.getOutputPortByIndex(0).connect(instanceArraySetup_Node.getInputPortByIndex(0))
        instanceArraySetup_Node.getOutputPortByIndex(0).connect(previewPointCloudSetup_Node.getInputPortByIndex(0))
        previewPointCloudSetup_Node.getOutputPortByIndex(0).connect(computeInstanceArray_Node.getInputPortByIndex(0))
        computeInstanceArray_Node.getOutputPortByIndex(0).connect(scatterDensityControl_Node.getInputPortByIndex(0))
        scatterDensityControl_Node.getOutputPortByIndex(0).connect(deleteInstanceArrayChildren_Node.getInputPortByIndex(0))

        SA.FnLayoutInputNodes(mergeInputs_Node)
        SA.FnLayoutInputNodes(abcScatter_Node)
        SA.FnLayoutInputNodes(createABCSources_Node)
        SA.FnLayoutInputNodes(setInstanceSourceType_Node)
        SA.FnLayoutInputNodes(instanceArraySetup_Node)
        SA.FnLayoutInputNodes(previewPointCloudSetup_Node)
        SA.FnLayoutInputNodes(computeInstanceArray_Node)
        SA.FnLayoutInputNodes(scatterDensityControl_Node)
        SA.FnLayoutInputNodes(deleteInstanceArrayChildren_Node)

        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            deleteInstanceArrayChildren_Node.getOutputPortByIndex(0))

    def addParameterHints(self, attrName, inputDict):
        inputDict.update(_nodeFieldsHints.get(attrName, {}))

    def mergeInputsNode(self):
        mergeInputs_Node = NodegraphAPI.CreateNode("Merge", self)
        mergeInputs_Node.setName("Merge_Inputs")

        mergeInputs_Node.addInputPort("inputScene")
        mergeInputs_Node.addInputPort("inputGeometry")
        mergeInputs_Node.addInputPort("inputScatter")

        SA.FnAddNodeReferenceParam(self, "node_Merge_Inputs", mergeInputs_Node)

        return mergeInputs_Node

    def abcScatterNode(self):
        abcScatter_Node = NodegraphAPI.CreateNode("Alembic_In", self)
        abcScatter_Node.setName("AlembicIn_LoadScatter")

        if self.getParameterValue("abcScatterPath", 1):
            abcScatter_Node.getParameter("name").setExpression(("getParent().instanceArrayLoc "
                "+ \"/\"\"" + self.getParameterValue("abcScatterPath", 1).rsplit("/", 1)[1].split(".abc", 1)[0] + "\""), True)
            abcScatter_Node.getParameter("abcAsset").setExpression("getParent().abcScatterPath")

            # Very dirty way to get to the pointcloud location of the Alembic file.
            # Right now, we also assume that the Alembic file contains a single pointcloud,
            # and even that it contains one in the first place, which is not necessarily true.
            abcScatter_GeoProducer = Nodes3DAPI.GetGeometryProducer(abcScatter_Node)
            while abcScatter_GeoProducer.getFirstChild() != None:
                abcScatter_GeoProducer = abcScatter_GeoProducer.getFirstChild()

            self.abcScatterScenegraphLocation = str(abcScatter_GeoProducer.getFullName())

        SA.FnAddNodeReferenceParam(self, "node_AlembicIn_LoadScatter", abcScatter_Node)

        return abcScatter_Node

    def createABCSourcesNode(self):
        createABCSources_Node = NodegraphAPI.CreateNode("OpScript", self)
        createABCSources_Node.setName("OpScript_CreateABCSources")

        createABCSources_Node.getParameter("location").setExpression("getParent().instanceSourcesLoc", True)
        createABCSources_Node.getParameter("script.lua").setValue(OS.createABCSourcesScript(), 1)

        createABCSources_UserGroup = createABCSources_Node.getParameters().createChildGroup("user")

        instanceSourcesNamesAttr = createABCSources_UserGroup.createChildStringArray("instanceSourcesNames", len(self.abcGeoPathsList))
        instanceSourcesNamesList = ["\"" + self.abcGeoPathsList[idx].rsplit("/", 1)[1].split(".abc", 1)[0] + "\""
            for idx in xrange(0, len(self.abcGeoPathsList))] if self.abcGeoPathsList else []

        for nameIdx in range(len(instanceSourcesNamesList)):
            instanceSourcesNamesAttr.getChildByIndex(nameIdx).setExpression(instanceSourcesNamesList[nameIdx])

        abcGeoPathsListAttr = createABCSources_UserGroup.createChildStringArray("abcGeoPaths", len(self.abcGeoPathsList))

        for fileIdx in range(len(self.abcGeoPathsList)):
            abcGeoPathsListAttr.getChildByIndex(fileIdx).setExpression("\"" + self.abcGeoPathsList[fileIdx] + "\"", True)

        createABCSources_Node.getParameter("applyWhen").setValue("immediate", 1)
        createABCSources_Node.getParameter("applyWhere").setValue("at specific location", 1)
        createABCSources_Node.getParameter("inputBehavior").setValue("only valid", 1)

        SA.FnAddNodeReferenceParam(self, "node_OpScript_CreateABCSources", createABCSources_Node)

        return createABCSources_Node

    def setInstanceSourceTypeNode(self):
        instanceSourceType_Node = NodegraphAPI.CreateNode("AttributeSet", self)
        instanceSourceType_Node.setName("ASet_AlembicGeoToInstanceSource")

        instanceSourceType_Node.getParameter("attributeType").setValue("string", 1)
        instanceSourceType_Node.getParameter("attributeName").setValue("type", 1)
        instanceSourceType_Node.getParameter("stringValue.i0").setValue("instance source", 1)
        instanceSourceType_Node.getParameter("paths").resizeArray(len(self.abcGeoPathsList))

        for idx in xrange(0, len(self.abcGeoPathsList)):
            instanceSourceType_Node.getParameter("paths.i" + str(idx)).setExpression(("getParent().instanceSourcesLoc "
                "+ \"/\"\"" + self.abcGeoPathsList[idx].rsplit("/", 1)[1].split(".abc", 1)[0] + "\""), 1)

        SA.FnAddNodeReferenceParam(self, "node_ASet_AlembicGeoToInstanceSource", instanceSourceType_Node)

        return instanceSourceType_Node

    def instanceArraySetupNode(self):
        instanceArraySetup_Node = NodegraphAPI.CreateNode("OpScript", self)
        instanceArraySetup_Node.setName("OpScript_InstanceArraySetup")

        instanceArraySetup_Node.getParameter("CEL").setExpression("\"" + self.abcScatterScenegraphLocation + "\"", True)
        instanceArraySetup_Node.getParameter("script.lua").setValue(OS.instanceArraySetupScript(), 1)

        instanceArraySetup_UserGroup = instanceArraySetup_Node.getParameters().createChildGroup("user")

        instanceSourcesListAttr = instanceArraySetup_UserGroup.createChildStringArray("instanceSourcesList", len(self.abcGeoPathsList))
        instanceSourcesLocationList = ["getParent().instanceSourcesLoc\
            + \"/\"\"" + self.abcGeoPathsList[idx].rsplit("/", 1)[1].split(".abc", 1)[0] + "\""
            for idx in xrange(0, len(self.abcGeoPathsList))] if self.abcGeoPathsList else []

        for pathIdx in range(len(instanceSourcesLocationList)):
            instanceSourcesListAttr.getChildByIndex(pathIdx).setExpression(instanceSourcesLocationList[pathIdx])

        instanceArraySetup_Node.getParameter("applyWhen").setValue("immediate", 1)
        instanceArraySetup_Node.getParameter("applyWhere").setValue("at locations matching CEL", 1)
        instanceArraySetup_Node.getParameter("inputBehavior").setValue("only valid", 1)

        SA.FnAddNodeReferenceParam(self, "node_OpScript_InstanceArraySetup", instanceArraySetup_Node)

        return instanceArraySetup_Node

    def previewPointCloudSetupNode(self):
        previewPointCloudSetup_Node = NodegraphAPI.CreateNode("OpScript", self)
        previewPointCloudSetup_Node.setName("OpScript_PreviewPointCloudSetup")

        previewPointCloudSetup_Node.getParameter("CEL").setExpression("\"" + self.abcScatterScenegraphLocation + "\"", True)
        previewPointCloudSetup_Node.getParameter("script.lua").setValue(OS.previewPointCloudSetupScript(), 1)

        previewPointCloudSetup_UserGroup = previewPointCloudSetup_Node.getParameters().createChildGroup("user")
        previewPointCloudSetup_UserGroup.createChildString("previewPointCloudName", "")
        if self.getParameterValue("abcScatterPath", 1):
            previewPointCloudSetup_Node.getParameter("user.previewPointCloudName").setExpression(("\"" +
            self.abcScatterScenegraphLocation.rsplit("/", 1)[1] + "_previewCloud\""), True)

        previewPointCloudSetup_Node.getParameter("applyWhen").setValue("immediate", 1)
        previewPointCloudSetup_Node.getParameter("applyWhere").setValue("at locations matching CEL", 1)
        previewPointCloudSetup_Node.getParameter("inputBehavior").setValue("only valid", 1)

        SA.FnAddNodeReferenceParam(self, "node_OpScript_PreviewPointCloudSetup", previewPointCloudSetup_Node)

        return previewPointCloudSetup_Node

    def computeInstanceArrayNode(self):
        computeInstanceArray_Node = NodegraphAPI.CreateNode("ComputeInstanceArray", self)
        computeInstanceArray_Node.setName("Op_ComputeInstanceArray")

        computeInstanceArray_Node.getParameter("instanceArrayLoc").setExpression("\"" + self.abcScatterScenegraphLocation + "\"", True)
        computeInstanceArray_Node.getParameter("loadingMode").setExpression("getParent().loadingMode", True)
        computeInstanceArray_Node.getParameter("positionPrimvar").setExpression("getParent().positionPrimvar", True)
        computeInstanceArray_Node.getParameter("rotationPrimvar").setExpression("getParent().rotationPrimvar", True)
        computeInstanceArray_Node.getParameter("scalePrimvar").setExpression("getParent().scalePrimvar", True)
        computeInstanceArray_Node.getParameter("protoIndicesPrimvar").setExpression("getParent().protoIndicesPrimvar", True)

        SA.FnAddNodeReferenceParam(self, "node_Op_ComputeInstanceArray", computeInstanceArray_Node)

        return computeInstanceArray_Node

    def scatterDensityControlNode(self):
        scatterDensityControl_Node = NodegraphAPI.CreateNode("OpScript", self)
        scatterDensityControl_Node.setName("OpScript_scatterDensityControl")

        scatterDensityControl_Node.getParameter("CEL").setExpression("\"" + self.abcScatterScenegraphLocation + "\"", True)
        scatterDensityControl_Node.getParameter("script.lua").setValue(OS.scatterDensityControlScript(), 1)

        scatterDensityControl_UserGroup = scatterDensityControl_Node.getParameters().createChildGroup("user")
        scatterDensityControl_UserGroup.createChildNumber("scatterDensity", 100)
        scatterDensityControl_Node.getParameter("user.scatterDensity").setExpression("getParent().scatterDensity")

        scatterDensityControl_Node.getParameter("executionMode").setValue("deferred", 1)
        scatterDensityControl_Node.getParameter("applyWhen").setValue("during op resolve", 1)
        scatterDensityControl_Node.getParameter("applyWhere").setValue("at locations matching CEL", 1)
        scatterDensityControl_Node.getParameter("inputBehavior").setValue("only valid", 1)
        scatterDensityControl_Node.getParameter("resolveIds").setValue("PrmanInstanceArray", 1)

        SA.FnAddNodeReferenceParam(self, "node_OpScript_ScatterDensityControl", scatterDensityControl_Node)

        return scatterDensityControl_Node

    def deleteInstanceArrayChildrenNode(self):
        deleteInstanceArrayChildren_Node = NodegraphAPI.CreateNode("OpScript", self)
        deleteInstanceArrayChildren_Node.setName("OpScript_DeleteInstanceArrayChildren")

        deleteInstanceArrayChildren_Node.getParameter("CEL").setExpression("\"" + self.abcScatterScenegraphLocation + "\"", True)
        deleteInstanceArrayChildren_Node.getParameter("script.lua").setValue(OS.deleteInstanceArrayChildrenScript(), 1)

        deleteInstanceArrayChildren_Node.getParameter("executionMode").setValue("deferred", 1)
        deleteInstanceArrayChildren_Node.getParameter("applyWhen").setValue("during op resolve", 1)
        deleteInstanceArrayChildren_Node.getParameter("applyWhere").setValue("at locations matching CEL", 1)
        deleteInstanceArrayChildren_Node.getParameter("inputBehavior").setValue("only valid", 1)
        deleteInstanceArrayChildren_Node.getParameter("resolveIds").setValue("PrmanInstanceArray", 1)

        SA.FnAddNodeReferenceParam(self, "node_OpScript_DeleteInstanceArrayChildren", deleteInstanceArrayChildren_Node)

        return deleteInstanceArrayChildren_Node

    def resetNetwork(self):
        for childNode in self.getChildren():
            childNode.delete()

        self.clearInstanceArrayData()
        self.__buildDefaultNetwork()

    def clearInstanceArrayData(self):
        self.abcGeoPathsList = []
        self.abcScatterScenegraphLocation = ""


_nodeFieldsHints = {
    "PrmanInstanceArray.instanceArrayLoc":{
        "label" : "Instance Array Location",
        "help" : "The scenegraph location where the instance array will be stored.",
        "widget": "scenegraphLocation"
    },
    "PrmanInstanceArray.instanceSourcesLoc":{
        "label" : "Instance Sources Location",
        "help" : "The scenegraph location where the .abc file(s) used as instance source(s) will be stored.",
        "widget": "scenegraphLocation"
    },
    "PrmanInstanceArray.abcScatterPath":{
        "label" : "Alembic Scatter Path",
        "help" : "The path to the .abc file that will be used to drive the scattering of the geometry.",
        "widget": "fileInput"
    },
    "PrmanInstanceArray.abcGeoPaths":{
        "label" : "Alembic Geometry Paths",
        "help" : "The path(s) to the .abc file(s) that will be used as instance source(s).",
        "widget" : "sortableDelimitedString",
        "isDynamicArray" : "True"
    },  
    "PrmanInstanceArray.loadingMode":{
        "label" : "Loading Mode",
        "help" : "Give the user the ability to choose when to actually compute the instance array,\
        i.e. during op resolve or immediately. The former option is used by default as waiting for op resolve\
        can help bringing the expansion time as close to zero as possible. The user will also not really be impacted\
        by such a deffered computation of the data as instanceIndex/instanceMatrix(/omitList) will be useful to PRMan\
        only most of the time.",
        "widget": "popup",
        "options": ["during op resolve", "immediate"]
    },
    "PrmanInstanceArray.scatterDensity":{
        "label" : "Scatter Density",
        "help" : "Control the density of the scattered geometry that PRMan will render.",
        "slider" : "True",
        "int" : "True",
        "min" : "0",
        "max" : "100",
        "slidermin" : "0",
        "slidermax" : "100",
        "sensitivity" : "1"
    },
    "PrmanInstanceArray.positionPrimvar":{
        "label" : "Position",
        "help" : "The name of the primvar holding the position information of the instances."
    },
    "PrmanInstanceArray.rotationPrimvar":{
        "label" : "Rotation",
        "help" : "The name of the primvar holding the rotation information of the instances."
    },
    "PrmanInstanceArray.scalePrimvar":{
        "label" : "Scale",
        "help" : "The name of the primvar holding the scaling information of the instances."
    },
    "PrmanInstanceArray.protoIndicesPrimvar":{
        "label" : "Prototypes Indices",
        "help" : "The name of the primvar holding the index information of the instances."
    },
    "PrmanInstanceArray.idsPrimvar":{
        "label" : "IDs",
        "help" : "The name of the primvar holding the ID information of the instances."
    },
    "PrmanInstanceArray.velocityPrimvar":{
        "label" : "Velocity",
        "help" : "The name of the primvar holding the velocity information of the instances."
    },
    "PrmanInstanceArray.angularVelocityPrimvar":{
        "label" : "Angular Velocity",
        "help" : "The name of the primvar holding the angular velocity information of the instances."
    },
    "PrmanInstanceArray.useMotionBlur":{
        "label" : "Use Motion Blur",
        "help" : "Control whether or not the velocity motion blur will be computed.",
        "widget": "checkBox"
    },
    "PrmanInstanceArray.intensityMultiplier":{
        "label" : "Intensity Multiplier",
        "help" : "Control the intensity of the velocity motion blur effect.",
        "slider" : "True",
        "min" : "0.1",
        "max" : "5",
        "slidermin" : "0.1",
        "slidermax" : "5",
        "sensitivity" : "0.1"
    }
}
