import logging

from Katana import (
    FnAttribute,
    FnGeolibServices,
    NodegraphAPI,
    Nodes3DAPI
)


logger = logging.getLogger("PassResolve.Node")
logger.setLevel(logging.WARNING)


class PassResolve(Nodes3DAPI.NodeTypeBuilder):
    def __init__(self, node_name):
        """
        """
        logger.debug("PassResolve - __init__()")

        super(PassResolve, self).__init__(node_name)

        self.setInputPortNames(["in"])
        self.setOutputPortNames(["out"])

        self.setCustomMethod("get_existing_render_node", get_existing_render_node)
        self.setCustomMethod("setup_render_node", setup_render_node)

        self.build_node_parameters()

        self.setBuildOpChainFnc(build_pass_resolve_op_chain)
        self.build()

    def build_node_parameters(self):
        """
        """
        logger.debug("PassResolve - build_node_parameters()")

        group_builder = FnAttribute.GroupBuilder()
        # group_builder.set("node_version", 1)
        group_builder.set("activePassLocation", "")
        group_builder.set("setupRenderNodeScript", "")

        parameters_hints = self.get_parameters_hints()

        for parameter in parameters_hints:
            self.setHintsForParameter(parameter, parameters_hints[parameter])

        self.setParametersTemplateAttr(group_builder.build())

    def get_parameters_hints(self):
        """
        """
        logger.debug("PassResolve - get_parameters_hints()")

        # We describe here our Katana parameters and how they should appear/behave
        return {
            "activePassLocation": {
                "label": "Active Pass Location",
                "help": "Define the location of the pass created using the \"PassDefine\" node that will be resolved.",
                "widget": "scenegraphLocation"
            },
            "setupRenderNodeScript": {
                "label": "Setup Render Node",
                "help": ("Will create a \"Render\" node that will have its \"passName\" parameter "
                    "linked to those of this \"PassResolve\" node, if one such node is not already connected to "
                    "this \"PassResolve\" node."),
                "widget": "scriptButton",
                "buttonText": "Setup Render Node",
                "scriptText": """node.setup_render_node()"""
            },
        }


def build_pass_resolve_op_chain(node, interface):
    """
    """
    logger.debug("PassResolve - build_pass_resolve_op_chain()")

    interface.setMinRequiredInputs(0)

    frame_time = interface.getGraphState().getTime()
    active_pass_location_param = node.getParameter("activePassLocation")

    # Setup the currently active pass in the SceneGraph.
    attribute_set_args_builder = FnGeolibServices.OpArgsBuilders.AttributeSet()

    attribute_set_args_builder.setCEL(["/root"])
    if active_pass_location_param.getValue(frame_time):
        attribute_set_args_builder.setAttr("passResolve.activePassLocation",
            FnAttribute.StringAttribute(active_pass_location_param.getValue(frame_time)))

    interface.appendOp("AttributeSet", attribute_set_args_builder.build())

    # Expose all locations under "/root/world" to the PassVisibility Op that will
    # set the appropriate locations as visible or not, as per the setup of the currently
    # active pass.
    group_builder = FnAttribute.GroupBuilder()
    attribute_set_args_builder = FnGeolibServices.OpArgsBuilders.AttributeSet()

    attribute_set_args_builder.setCEL(["/root/world//*"])
    attribute_set_args_builder.addSubOp("PassVisibility", group_builder.build())

    interface.appendOp("AttributeSet", attribute_set_args_builder.build())

    # Expose all locations under "/root/world" to the PassRays Op that will
    # set the rays related attributes on the appropriate locations, which are renderer dependent,
    # as per the setup of the currently active pass.
    group_builder = FnAttribute.GroupBuilder()
    attribute_set_args_builder = FnGeolibServices.OpArgsBuilders.AttributeSet()

    attribute_set_args_builder.setCEL(["/root/world//*"])
    attribute_set_args_builder.addSubOp("PassRays", group_builder.build())

    interface.appendOp("AttributeSet", attribute_set_args_builder.build())

    # Expose the "/root" location to the PassCollections Op that will
    # create collections attributes on the root location, according the to active pass configuration.
    group_builder = FnAttribute.GroupBuilder()
    attribute_set_args_builder = FnGeolibServices.OpArgsBuilders.AttributeSet()

    attribute_set_args_builder.setCEL(["/root"])
    attribute_set_args_builder.addSubOp("PassCollections", group_builder.build())

    interface.appendOp("AttributeSet", attribute_set_args_builder.build())


def get_existing_render_node(node):
    """
    """
    logger.debug("PassResolve - get_existing_render_node()")

    connected_ports = node.getOutputPortByIndex(0).getConnectedPorts()

    if not connected_ports:
        return None

    return (connected_ports[0].getNode() if connected_ports[0].getNode().getType() == "Render" else None)


def setup_render_node(node):
    """
    """
    logger.debug("PassResolve - setup_render_node()")

    render_node = node.get_existing_render_node()

    if not render_node:
        render_node = NodegraphAPI.CreateNode("Render", node.getParent())
        render_node.getParameter("passName").setExpression((
            """str(getNode("{node_name}").activePassLocation).split("/")[-1]""".format(
                node_name=node.getName()
            )))

    node.getOutputPortByIndex(0).connect(render_node.getInputPortByIndex(0))
    node_pos_x, node_pos_y = NodegraphAPI.GetNodePosition(node)

    NodegraphAPI.SetNodePosition(render_node, (node_pos_x, node_pos_y - 150))
