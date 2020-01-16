#include "PassRays.h"


void PassRays::setup(Foundry::Katana::GeolibSetupInterface& interface)
{
    interface.setThreading(Foundry::Katana::GeolibSetupInterface::ThreadModeConcurrent);
}

void PassRays::cook(Foundry::Katana::GeolibCookInterface& interface)
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
    setPassRays(interface, activePassLocationValue);
}

void PassRays::setPassRays(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation)
{
    // We gather the visibility related attributes of the pass on the currently evaluated locations.
    const FnAttribute::StringAttribute cameraRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.camera.show", activePassLocation);
    const FnAttribute::StringAttribute cameraRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.camera.hide", activePassLocation);
    const FnAttribute::StringAttribute matteRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.matte.show", activePassLocation);
    const FnAttribute::StringAttribute matteRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.matte.hide", activePassLocation);

    bool canMatchChildren = false;

    FnGeolibServices::FnGeolibCookInterfaceUtils::MatchesCELInfo matchesCELInfo;

    // We enable and/or disable the camera rays for the provided location(s).
    if (cameraRaysShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, cameraRaysShowAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.camera", FnAttribute::IntAttribute(1));

            if (isCurrentRenderer(interface, "prman"))
                interface.setAttr("prmanStatements.attributes.visibility.camera", FnAttribute::IntAttribute(1));
            else if (isCurrentRenderer(interface, "arnold"))
                interface.setAttr("arnoldStatements.visibility.AI_RAY_CAMERA", FnAttribute::IntAttribute(1));
            else if (isCurrentRenderer(interface, "dl"))
                interface.setAttr("dlObjectSettings.visibility.camera", FnAttribute::IntAttribute(1));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    if (cameraRaysHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, cameraRaysHideAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.camera", FnAttribute::IntAttribute(0));

            if (isCurrentRenderer(interface, "prman"))
                interface.setAttr("prmanStatements.attributes.visibility.camera", FnAttribute::IntAttribute(0));
            else if (isCurrentRenderer(interface, "arnold"))
                interface.setAttr("arnoldStatements.visibility.AI_RAY_CAMERA", FnAttribute::IntAttribute(0));
            else if (isCurrentRenderer(interface, "dl"))
                interface.setAttr("dlObjectSettings.visibility.camera", FnAttribute::IntAttribute(0));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

    // We enable and/or disable the matte for the provided location(s).
    if (matteRaysShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, matteRaysShowAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.matte", FnAttribute::IntAttribute(1));
            interface.setAttr("prmanStatements.attributes.Matte", FnAttribute::IntAttribute(1));

            if (isCurrentRenderer(interface, "prman"))
                interface.setAttr("prmanStatements.attributes.Matte", FnAttribute::IntAttribute(1));
            else if (isCurrentRenderer(interface, "arnold"))
                interface.setAttr("arnoldStatements.matte", FnAttribute::IntAttribute(1));
            else if (isCurrentRenderer(interface, "dl"))
                interface.setAttr("dlObjectSettings.visibility.compositingMode", FnAttribute::IntAttribute(1));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    if (matteRaysHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, matteRaysHideAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.matte", FnAttribute::IntAttribute(0));

            if (isCurrentRenderer(interface, "prman"))
                interface.setAttr("prmanStatements.attributes.Matte", FnAttribute::IntAttribute(0));
            else if (isCurrentRenderer(interface, "arnold"))
                interface.setAttr("arnoldStatements.matte", FnAttribute::IntAttribute(0));
            else if (isCurrentRenderer(interface, "dl"))
                interface.setAttr("dlObjectSettings.visibility.compositingMode", FnAttribute::IntAttribute(0));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

    if (isCurrentRenderer(interface, "prman"))
        setPassPRManRays(interface, activePassLocation, canMatchChildren);
    else if (isCurrentRenderer(interface, "arnold"))
        setPassArnoldRays(interface, activePassLocation, canMatchChildren);
    else if (isCurrentRenderer(interface, "dl"))
        setPassDlRays(interface, activePassLocation, canMatchChildren);

    // In case there is no more potential location to match down the line,
    // we stop the traversal of the SceneGraph here.
    if (!canMatchChildren)
    {
        interface.stopChildTraversal();

        return;
    }
}

void PassRays::setPassPRManRays(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation,
    bool& canMatchChildren)
{

    const FnAttribute::StringAttribute prmanIndirectRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.indirect.show", activePassLocation);
    const FnAttribute::StringAttribute prmanIndirectRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.indirect.hide", activePassLocation);
    const FnAttribute::StringAttribute prmanTransmissionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.transmission.show", activePassLocation);
    const FnAttribute::StringAttribute prmanTransmissionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.prman.transmission.hide", activePassLocation);

    // We make the currently evaluated location visible to the indirect rays.
    if (prmanIndirectRaysShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, prmanIndirectRaysShowAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.prman.indirect", FnAttribute::IntAttribute(1));
            interface.setAttr("prmanStatements.attributes.visibility.indirect", FnAttribute::IntAttribute(1));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    // We make the currently evaluated location invisible to the indirect rays.
    if (prmanIndirectRaysHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, prmanIndirectRaysHideAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.prman.indirect", FnAttribute::IntAttribute(0));
            interface.setAttr("prmanStatements.attributes.visibility.indirect", FnAttribute::IntAttribute(0));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

    // We make the currently evaluated location visible to the transmission rays.
    if (prmanTransmissionRaysShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, prmanTransmissionRaysShowAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.prman.transmission", FnAttribute::IntAttribute(1));
            interface.setAttr("prmanStatements.attributes.visibility.transmission", FnAttribute::IntAttribute(1));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    // We make the currently evaluated location invisible to the transmission rays.
    if (prmanTransmissionRaysHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, prmanTransmissionRaysHideAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.prman.transmission", FnAttribute::IntAttribute(0));
            interface.setAttr("prmanStatements.attributes.visibility.transmission", FnAttribute::IntAttribute(0));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
}

void PassRays::setPassArnoldRays(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation,
    bool& canMatchChildren)
{

}

void PassRays::setPassDlRays(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation,
    bool& canMatchChildren)
{
    const FnAttribute::StringAttribute dlShadowRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.shadow.show", activePassLocation);
    const FnAttribute::StringAttribute dlShadowRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.shadow.hide", activePassLocation);
    const FnAttribute::StringAttribute dlDiffuseRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.diffuse.show", activePassLocation);
    const FnAttribute::StringAttribute dlDiffuseRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.diffuse.hide", activePassLocation);
    const FnAttribute::StringAttribute dlSpecularRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.specular.show", activePassLocation);
    const FnAttribute::StringAttribute dlSpecularRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.specular.hide", activePassLocation);
    const FnAttribute::StringAttribute dlReflectionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.reflection.show", activePassLocation);
    const FnAttribute::StringAttribute dlReflectionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.reflection.hide", activePassLocation);
    const FnAttribute::StringAttribute dlTransmissionRaysShowAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.transmission.show", activePassLocation);
    const FnAttribute::StringAttribute dlTransmissionRaysHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.rays.dl.transmission.hide", activePassLocation);

    // We make the currently evaluated location visible to the shadow rays.
    if (dlShadowRaysShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, dlShadowRaysShowAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.dl.shadow", FnAttribute::IntAttribute(1));
            interface.setAttr("dlObjectSettings.visibility.shadow", FnAttribute::IntAttribute(1));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    // We make the currently evaluated location invisible to the shadow rays.
    if (dlShadowRaysHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, dlShadowRaysHideAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("passResolve.rays.dl.shadow", FnAttribute::IntAttribute(0));
            interface.setAttr("dlObjectSettings.visibility.shadow", FnAttribute::IntAttribute(0));
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

}

/// Check if the Katana scene is using a specific renderer.
bool PassRays::isCurrentRenderer(Foundry::Katana::GeolibCookInterface& interface,
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
const std::string PassRays::getEnvVar(const std::string& envVarName,
    const std::string& defaultValue)
{
    const char* envVarValue = getenv(envVarName.c_str());

    return (envVarValue != NULL) ? std::string(envVarValue) : defaultValue;
}