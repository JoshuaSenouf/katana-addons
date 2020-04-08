#include "PassVisibility.h"


void PassVisibility::setup(Foundry::Katana::GeolibSetupInterface& interface)
{
    interface.setThreading(Foundry::Katana::GeolibSetupInterface::ThreadModeConcurrent);
}

void PassVisibility::cook(Foundry::Katana::GeolibCookInterface& interface)
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

    // If everything is fine up until now, we setup the visibility state of the current location according
    // to the active pass configuration.
    setPassVisibility(interface, activePassLocationValue);
}

///
void PassVisibility::setPassVisibility(Foundry::Katana::GeolibCookInterface& interface,
    const std::string& activePassLocation)
{
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
    const FnAttribute::IntAttribute autoHideAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.advanced.autoHide", activePassLocation);
    const FnAttribute::IntAttribute autoPruneAttr = Foundry::Katana::GetGlobalAttr(interface,
        "passDefine.visibility.advanced.autoPrune", activePassLocation);
    const FnAttribute::IntAttribute parentVisibleAttr = interface.getOpArg("parentVisible");

    bool autoHideAttrValue = autoHideAttr.getValue(true, false);
    bool autoPruneAttrValue = autoPruneAttr.getValue(false, false);
    bool parentVisibleAttrValue = parentVisibleAttr.getValue(false, false);
    bool visible = false;
    bool canMatchChildren = false;

    const std::string inputLocationType = FnKat::GetInputLocationType(interface);

    FnGeolibServices::FnGeolibCookInterfaceUtils::MatchesCELInfo matchesCELInfo;

    // We set the main Katana visibility attribute to 0 to all the direct children locations found
    // under "/root/world" by default, before processing any other visibility related states, which should
    // include the current one.
    // This means that if the currently evaluated location is not later set to be visible in the Op, it will
    // be considered as hidden by the used renderer.
    if (autoHideAttrValue)
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo, interface,
            FnAttribute::StringAttribute("((/root/world/*))"));

        if (matchesCELInfo.matches)
        {
            interface.setAttr("visible", FnAttribute::IntAttribute(0));
        }
    }

    // If the user requested for the currently evaluated location, which can technically be of any types, to be
    // considered as either visible or hidden by Katana, and thus the renderer, we set the main Katana visibility
    // attribute to the appropriate value.
    // We also evaluate that if the potential children of the currently evaluated location have at least
    // a chance to be visible too. This information will be used later in the Op, and will be crucial in deciding
    // whether or not we should continue the traversal of the children of this location.
    if (globalVisibilityShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, globalVisibilityShowAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("visible", FnAttribute::IntAttribute(1));
            visible = true;
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    if (globalVisibilityHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, globalVisibilityHideAttr);

        if (matchesCELInfo.matches)
        {
            interface.setAttr("visible", FnAttribute::IntAttribute(0));
            visible = false;
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

    // If the user requested for the currently evaluated location, which has to be of type "camera", to be
    // considered as either visible or hidden by Katana, and thus the renderer, we set the main Katana visibility
    // attribute to the appropriate value.
    // We also evaluate that if the potential children of the currently evaluated location have at least
    // a chance to be visible too. This information will be used later in the Op, and will be crucial in deciding
    // whether or not we should continue the traversal of the children of this location.
    if (camerasVisibilityShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, camerasVisibilityShowAttr);

        if (matchesCELInfo.matches)
        {
            if (inputLocationType == "camera")
            {
                interface.setAttr("visible", FnAttribute::IntAttribute(1));
                visible = true;
            }
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    if (camerasVisibilityHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, camerasVisibilityHideAttr);

        if (matchesCELInfo.matches)
        {
            if (inputLocationType == "camera")
            {
                interface.setAttr("visible", FnAttribute::IntAttribute(0));
                visible = false;
            }
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

    // If the user requested for the currently evaluated location, which has to be either of type "light" or "rig",
    // to be considered as either visible or hidden by Katana, and thus the renderer, we set the main Katana visibility
    // attribute to the appropriate value.
    // We also evaluate that if the potential children of the currently evaluated location have at least
    // a chance to be visible too. This information will be used later in the Op, and will be crucial in deciding
    // whether or not we should continue the traversal of the children of this location.
    if (lightsVisibilityShowAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, lightsVisibilityShowAttr);

        if (matchesCELInfo.matches)
        {
            if (inputLocationType == "light" ||
                inputLocationType == "rig")
            {
                interface.setAttr("visible", FnAttribute::IntAttribute(1));
                visible = true;
            }
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }
    if (lightsVisibilityHideAttr.isValid())
    {
        FnGeolibServices::FnGeolibCookInterfaceUtils::matchesCEL(matchesCELInfo,
            interface, lightsVisibilityHideAttr);

        if (matchesCELInfo.matches)
        {
            if (inputLocationType == "light" ||
                inputLocationType == "rig")
            {
                interface.setAttr("visible", FnAttribute::IntAttribute(0));
                visible = false;
            }
        }
        if (matchesCELInfo.canMatchChildren)
        {
            canMatchChildren = true;
        }
    }

    // If the user requested it, in case the currently evaluated location and its parent
    // are considered not visible, as well as we can be sure that we don't have anymore potentially matching
    // children locations to evaluate, i.e. no more potentially visible locations, we both prune the currently
    // evaluated location and stop the traversal of the children of the location.
    if (autoPruneAttrValue)
    {
        if (!parentVisibleAttrValue &&
            !visible &&
            !canMatchChildren)
        {
            interface.deleteSelf();
            interface.stopChildTraversal();

            return;
        }
    }

    // If we don't have anymore potentially matching children locations to evaluate, i.e. no more potentially
    // visible locations, we stop the traversal of the children of this location.
    if (!canMatchChildren)
    {
        interface.stopChildTraversal();

        return;
    }

    // If the currently evaluated location is considered visible, we pass that information down to the children
    // locations, in order for these to be able to know about their parent visibility state too, which is
    // crucial in order to determine if we should prune a location or not.
    // The reason we do this, instead of simply querying the "visible" global attribute is because it won't
    // be cooked when we will need it, making it unreliable.
    if (visible)
    {
        FnAttribute::GroupBuilder visibilityGroupBuilder;

        visibilityGroupBuilder.update(interface.getOpArg());
        visibilityGroupBuilder.set("parentVisible", FnAttribute::IntAttribute(visible));

        interface.replaceChildTraversalOp("", visibilityGroupBuilder.build());
    }
}

/// Check if the Katana scene is using a specific renderer.
bool PassVisibility::isCurrentRenderer(Foundry::Katana::GeolibCookInterface& interface,
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
const std::string PassVisibility::getEnvVar(const std::string& envVarName,
    const std::string& defaultValue)
{
    const char* envVarValue = getenv(envVarName.c_str());

    return (envVarValue != nullptr) ? std::string(envVarValue) : defaultValue;
}
