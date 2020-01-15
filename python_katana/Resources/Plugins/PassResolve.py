import logging

from Katana import Nodes3DAPI
from Katana import NodegraphAPI
from Katana import FnAttribute


logger = logging.getLogger("PassResolve.Node")
logger.setLevel(logging.WARNING)


class PassResolve(Nodes3DAPI.NodeTypeBuilder):
    def __init__(self, node_name):
        super(PassResolve, self).__init__(node_name)

        self.setInputPortNames(["in"])
        self.setOutputPortNames(["out"])

        self.setCustomMethod("get_existing_render_node", get_existing_render_node)
        self.setCustomMethod("setup_render_node", setup_render_node)

        self.build_node_parameters()

        self.setBuildOpChainFnc(build_pass_resolve_op_chain)
        self.build()

    def build_node_parameters(self):
        group_builder = FnAttribute.GroupBuilder()
        # group_builder.set("nodeVersion", 1)
        group_builder.set("activePassLocation", "")
        group_builder.set("setupRenderNodeScript", "")

        parameters_hints = self.get_parameters_hints()

        for parameter in parameters_hints:
            self.setHintsForParameter(parameter, parameters_hints[parameter])

        self.setParametersTemplateAttr(group_builder.build())

    def get_parameters_hints(self):
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
    interface.setMinRequiredInputs(0)

    frame_time = interface.getGraphState().getTime()
    active_pass_location_param = node.getParameter("activePassLocation")


def get_existing_render_node(node):
    """
    """
    connected_ports = node.getOutputPortByIndex(0).getConnectedPorts()

    if not connected_ports:
        return None

    return (connected_ports[0].getNode() if connected_ports[0].getNode().getType() == "Render" else None)


def setup_render_node(node):
    """
    """
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
