#include "PassCollections.h"

#include <pystring/pystring.h>


void PassCollections::setup(Foundry::Katana::GeolibSetupInterface& interface)
{
    interface.setThreading(Foundry::Katana::GeolibSetupInterface::ThreadModeConcurrent);
}

void PassCollections::cook(Foundry::Katana::GeolibCookInterface& interface)
{
    // Check if we are using one of the supported renderers.
    if (!isCurrentRenderer(interface, "dl") &&
        !isCurrentRenderer(interface, "prman") &&
        !isCurrentRenderer(interface, "arnold"))
    {
        return;
    }

    // Get the currently active pass location at the root.
    const FnAttribute::StringAttribute activePassLocationAttr = interface.getAttr("passResolve.activePassLocation",
        "/root");

    // Check if the attribute is valid, i.e. if the related pass was at least defined,
    // otherwise we abort the process and the traversal.
    if (!activePassLocationAttr.isValid())
    {
        Foundry::Katana::ReportError(interface,
            "No active pass location was found at the root. Please check if the pass is properly setup.");
        interface.stopChildTraversal();

        return;
    }

    const std::string activePassLocationValue = activePassLocationAttr.getValue();

    // Check if the active pass location found at the root does exist in the SceneGraph,
    // otherwise we abort the process and the traversal.
    if (!interface.doesLocationExist(activePassLocationValue))
    {
        Foundry::Katana::ReportError(interface,
            "The provided active pass location is not valid. Please check if the location exists in your SceneGraph.");
        interface.stopChildTraversal();

        return;
    }

    // We make sure that the active pass location attribute state was correctly processed without any lingering and
    // pending operations before we try to access it and its data.
    interface.prefetch(activePassLocationValue);
    const FnAttribute::GroupAttribute passDefineAttrGroup = interface.getAttr("passDefine", activePassLocationValue);

    // Check if the active pass location found at the root have a valid "passDefine" group,
    // which would be the case if the pass is enabled or anything other user interaction with the pass parameters,
    // otherwise we abort the process and the traversal.
    if (!passDefineAttrGroup.isValid())
    {
        Foundry::Katana::ReportError(interface,
            "No pass information available at the provided active pass location. "
            "Please check that the pass has been correctly enabled and set up.");
        interface.stopChildTraversal();

        return;
    }

    const FnAttribute::IntAttribute enablePassAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.enablePass", activePassLocationValue);

    // We check if the pass is enabled, otherwise we abort the process and the traversal.
    if(!enablePassAttr.getValue(0, false))
    {
        interface.stopChildTraversal();

        return;
    }

    // If everything is fine up until now, we setup the rays related attributes of the current location according
    // to the active pass configuration.
    setPassCollections(interface, activePassLocationValue);
}

///
void PassCollections::setPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation)
{
    const FnAttribute::StringAttribute rendererAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.renderer", activePassLocation);

    // We gather the visibility related attributes of the pass on the currently evaluated locations.
    const FnAttribute::StringAttribute globalVisibilityShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.global.show", activePassLocation);
    const FnAttribute::StringAttribute globalVisibilityHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.global.hide", activePassLocation);
    const FnAttribute::StringAttribute camerasVisibilityShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.cameras.show", activePassLocation);
    const FnAttribute::StringAttribute camerasVisibilityHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.cameras.hide", activePassLocation);
    const FnAttribute::StringAttribute lightsVisibilityShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.lights.show", activePassLocation);
    const FnAttribute::StringAttribute lightsVisibilityHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.lights.hide", activePassLocation);
    const FnAttribute::StringAttribute cameraRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.camera.show", activePassLocation);
    const FnAttribute::StringAttribute cameraRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.camera.hide", activePassLocation);
    const FnAttribute::StringAttribute matteRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.matte.show", activePassLocation);
    const FnAttribute::StringAttribute matteRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.matte.hide", activePassLocation);

    const std::vector<std::string> passLocationSplitVec = splitString(activePassLocation, "/");

    // Visibility collections.
    if (globalVisibilityShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Global_Show.cel",
            globalVisibilityShowAttr, false);
    }
    if (globalVisibilityHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Global_Hide.cel",
            globalVisibilityHideAttr, false);
    }
    if (camerasVisibilityShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Cameras_Show.cel",
            camerasVisibilityShowAttr, false);
    }
    if (camerasVisibilityHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Cameras_Hide.cel",
            camerasVisibilityHideAttr, false);
    }
    if (lightsVisibilityShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Lights_Show.cel",
            lightsVisibilityShowAttr, false);
    }
    if (lightsVisibilityHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Lights_Hide.cel",
            lightsVisibilityHideAttr, false);
    }

    // Per-ray type collections.
    if (cameraRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Camera_Show.cel",
            cameraRaysShowAttr, false);
    }
    if (cameraRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Camera_Hide.cel",
            cameraRaysHideAttr, false);
    }
    if (matteRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Matte_Show.cel",
            matteRaysShowAttr, false);
    }
    if (matteRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Matte_Hide.cel",
            matteRaysHideAttr, false);
    }

    // We set the renderer-specific rays attributes depending which one
    // the user is using.
    if (rendererAttr.getValue("dl", false) == "dl" &&
        isCurrentRenderer(interface, "dl"))
    {
        setDlPassCollections(interface, activePassLocation, passLocationSplitVec);
    }
    else if (rendererAttr.getValue("dl", false) == "prman" &&
        isCurrentRenderer(interface, "prman"))
    {
        setPRManPassCollections(interface, activePassLocation, passLocationSplitVec);
    }
    else if (rendererAttr.getValue("dl", false) == "arnold" &&
        isCurrentRenderer(interface, "arnold"))
    {
        setArnoldPassCollections(interface, activePassLocation, passLocationSplitVec);
    }
}

///
void PassCollections::setDlPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation,
    const std::vector<std::string>& passLocationSplitVec)
{
    const FnAttribute::StringAttribute shadowRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.shadow.show", activePassLocation);
    const FnAttribute::StringAttribute shadowRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.shadow.hide", activePassLocation);
    const FnAttribute::StringAttribute diffuseRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.diffuse.show", activePassLocation);
    const FnAttribute::StringAttribute diffuseRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.diffuse.hide", activePassLocation);
    const FnAttribute::StringAttribute specularRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.specular.show", activePassLocation);
    const FnAttribute::StringAttribute specularRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.specular.hide", activePassLocation);
    const FnAttribute::StringAttribute reflectionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.reflection.show", activePassLocation);
    const FnAttribute::StringAttribute reflectionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.reflection.hide", activePassLocation);
    const FnAttribute::StringAttribute transmissionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.transmission.show", activePassLocation);
    const FnAttribute::StringAttribute transmissionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.transmission.hide", activePassLocation);

    if (shadowRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Shadow_Show.cel", shadowRaysShowAttr, false);
    }
    if (shadowRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Shadow_Hide.cel", shadowRaysHideAttr, false);
    }
    if (diffuseRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Diffuse_Show.cel", diffuseRaysShowAttr, false);
    }
    if (diffuseRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Diffuse_Hide.cel", diffuseRaysHideAttr, false);
    }
    if (specularRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Specular_Show.cel", specularRaysShowAttr, false);
    }
    if (specularRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Specular_Hide.cel", specularRaysHideAttr, false);
    }
    if (reflectionRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Reflection_Show.cel", reflectionRaysShowAttr, false);
    }
    if (reflectionRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Reflection_Hide.cel", reflectionRaysHideAttr, false);
    }
    if (transmissionRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Transmission_Show.cel", transmissionRaysShowAttr, false);
    }
    if (transmissionRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Dl_Rays_Transmission_Hide.cel", transmissionRaysHideAttr, false);
    }
}

///
void PassCollections::setPRManPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation,
    const std::vector<std::string>& passLocationSplitVec)
{
    const FnAttribute::StringAttribute indirectRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.indirect.show", activePassLocation);
    const FnAttribute::StringAttribute indirectRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.indirect.hide", activePassLocation);
    const FnAttribute::StringAttribute transmissionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.transmission.show", activePassLocation);
    const FnAttribute::StringAttribute transmissionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.transmission.hide", activePassLocation);

    if (indirectRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_PRMan_Rays_Indirect_Show.cel", indirectRaysShowAttr, false);
    }
    if (indirectRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_PRMan_Rays_Indirect_Hide.cel", indirectRaysHideAttr, false);
    }
    if (transmissionRaysShowAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_PRMan_Rays_Transmission_Show.cel", transmissionRaysShowAttr, false);
    }
    if (transmissionRaysHideAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_PRMan_Rays_Transmission_Hide.cel", transmissionRaysHideAttr, false);
    }
}

///
void PassCollections::setArnoldPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation,
    const std::vector<std::string>& passLocationSplitVec)
{

}

/// Check if the Katana scene is using a specific renderer.
bool PassCollections::isCurrentRenderer(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& rendererToTest)
{
    const std::string defaultRenderer = getEnvVar("DEFAULT_RENDERER");
    const FnAttribute::StringAttribute currentRenderer = interface.getAttr("renderSettings.renderer", "/root");

    if (defaultRenderer == rendererToTest && !currentRenderer.isValid())
    {
        return true;
    }
    else if (currentRenderer.isValid())
    {
        if (currentRenderer.getValue() != rendererToTest)
        {
            return false;
        }
    }

    return true;
}

/// Return the requested environment variable if found, else a default string that
/// the user has set up in.
const std::string PassCollections::getEnvVar(const std::string& envVarName,
    const std::string& defaultValue)
{
    const char* envVarValue = getenv(envVarName.c_str());

    return (envVarValue != nullptr) ? std::string(envVarValue) : defaultValue;
}

/// Split a std::string using user-defined delimiter chars, and return a std::vector
/// containing the result of the split.
const std::vector<std::string> PassCollections::splitString(const std::string& stringToSplit,
    const std::string& delimChars,
    int numSplit)
{
    std::vector<std::string> splitVec;

    pystring::split(stringToSplit, splitVec, delimChars, numSplit);

    return splitVec;
}
