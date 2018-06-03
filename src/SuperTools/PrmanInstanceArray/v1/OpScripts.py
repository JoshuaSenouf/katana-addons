def instanceArraySetupScript():
    return """
local instanceSourcesList = Interface.GetOpArg("user.instanceSourcesList"):getNearestSample(Interface.GetCurrentTime())

Interface.SetAttr("type", StringAttribute("instance array"))
Interface.SetAttr("geometry.instanceSource", StringAttribute(instanceSourcesList, 1))
"""

def scatterDensityControlScript():
    return """
local instanceCount = Interface.GetAttr("geometry.instanceIndex")

if instanceCount == nil then
    print ("[PrmanInstanceArray] ERROR - OpScript_ScatterDensityControl - The instanceIndex attribute is invalid, the scatter density control will be skipped.")
    do return end
end

local scatterDensityPercentage = 100 - Interface.GetOpArg("user.scatterDensity"):getValue()
local scatterDensityRange = instanceCount * (scatterDensityPercentage / 100)
local omitListArray = {}

if scatterDensityPercentage > 0 then
    for idx = 0, scatterDensityRange do
        table.insert(omitListArray, math.floor(i * instanceCount / scatterDensityRange))
    end

    Interface.SetAttr("geometry.omitList", IntAttribute(omitListArray, 1))
end
"""

def previewPointCloudSetupScript():
    return """
Interface.SetAttr("type", StringAttribute("pointcloud"))
"""

def deleteInstanceArrayChildrenScript():
    return """
Interface.DeleteChildren()
"""