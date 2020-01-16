def configure_pass_location_opscript():
    return """local passRootLocation = Interface.GetOpArg("user.passRootLocation"):getValue()
local enablePass = tonumber(Interface.GetOpArg("user.enablePass"):getValue())
local type = Interface.GetOpArg("user.type"):getValue()
local prefix = Interface.GetOpArg("user.prefix"):getValue()
local element = Interface.GetOpArg("user.element"):getValue()
local suffix = Interface.GetOpArg("user.suffix"):getValue()

local passLocation = passRootLocation .. "/" .. type .. "_" .. prefix .. "_" .. element .. "_" .. suffix

if Interface.GetInputLocationPath() == "/root" then
    local sscb = OpArgsBuilders.StaticSceneCreate(true)
    sscb:createEmptyLocation(passLocation, "pass")
    sscb:setAttrAtLocation(passLocation, "visible", IntAttribute(enablePass, 1))

    Interface.ExecOp("StaticSceneCreate", sscb:build())
end
"""
