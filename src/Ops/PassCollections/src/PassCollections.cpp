#include "PassCollections.h"

#include <pystring/pystring.h>


void PassCollections::setup(Foundry::Katana::GeolibSetupInterface& interface)
{
    interface.setThreading(Foundry::Katana::GeolibSetupInterface::ThreadModeConcurrent);
}

void PassCollections::cook(Foundry::Katana::GeolibCookInterface& interface)
{
    // Check if we are using one of the supported renderers.
    if (!isCurrentRenderer(interface, "prman") &&
        !isCurrentRenderer(interface, "arnold") &&
        !isCurrentRenderer(interface, "dl"))
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

void PassCollections::setPassCollections(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation)
{
    // We gather the visibility related attributes of the pass on the currently evaluated locations.
    const FnAttribute::StringAttribute globalVisibilityAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.show.global", activePassLocation);
    const FnAttribute::StringAttribute camerasVisibilityAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.show.cameras", activePassLocation);
    const FnAttribute::StringAttribute lightsVisibilityAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.show.lights", activePassLocation);
    const FnAttribute::StringAttribute hideVisibilityAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.hide", activePassLocation);
    const FnAttribute::StringAttribute cameraRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.camera.show", activePassLocation);
    const FnAttribute::StringAttribute cameraRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.camera.hide", activePassLocation);
    const FnAttribute::StringAttribute matteRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.matte.show", activePassLocation);
    const FnAttribute::StringAttribute matteRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.matte.hide", activePassLocation);

    // const FnAttribute::StringAttribute indirectRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
    //     "passDefine.rays.indirect.show", activePassLocation);
    // const FnAttribute::StringAttribute indirectRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
    //     "passDefine.rays.indirect.hide", activePassLocation);
    // const FnAttribute::StringAttribute transmissionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
    //     "passDefine.rays.transmission.show", activePassLocation);
    // const FnAttribute::StringAttribute transmissionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
    //     "passDefine.rays.transmission.hide", activePassLocation);

    const std::vector<std::string> passLocationSplitVec = splitString(activePassLocation, "/");

    // Visibility collections.
    if (globalVisibilityAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Global.cel",
            globalVisibilityAttr, false);
    }
    if (camerasVisibilityAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Cameras.cel",
            camerasVisibilityAttr, false);
    }
    if (lightsVisibilityAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Lights.cel",
            lightsVisibilityAttr, false);
    }
    if (hideVisibilityAttr.isValid())
    {
        interface.setAttr("collections." + passLocationSplitVec.back() + "_Visibility_Hide.cel",
            hideVisibilityAttr, false);
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
    // if (indirectRaysShowAttr.isValid())
    // {
    //     interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Indirect_Show.cel", indirectRaysShowAttr, false);
    // }
    // if (indirectRaysHideAttr.isValid())
    // {
    //     interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Indirect_Hide.cel", indirectRaysHideAttr, false);
    // }
    // if (transmissionRaysShowAttr.isValid())
    // {
    //     interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Transmission_Show.cel", transmissionRaysShowAttr, false);
    // }
    // if (transmissionRaysHideAttr.isValid())
    // {
    //     interface.setAttr("collections." + passLocationSplitVec.back() + "_Rays_Transmission_Hide.cel", transmissionRaysHideAttr, false);
    // }
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

    return (envVarValue != NULL) ? std::string(envVarValue) : defaultValue;
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
