import logging

from Katana import (
    FnAttribute,
    FnGeolibServices,
    NodegraphAPI,
    Nodes3DAPI,
    RenderingAPI
)


module_logger = logging.getLogger("katana_addons.Plugins.RendererOutputExport.Node")
module_logger.setLevel(logging.WARNING)


class RendererOutputExport(Nodes3DAPI.NodeTypeBuilder):
    """
    """

    def __init__(self, node_name):
        """
        """
        module_logger.debug("RendererOutputExport - __init__()")

        super(RendererOutputExport, self).__init__(node_name)

        self.setInputPortNames(["in"])
        self.setOutputPortNames(["out"])

        self.setCustomMethod("export_renderer_output", export_renderer_output)

        self.build_node_parameters()

        self.setBuildOpChainFnc(build_renderer_output_export_op_chain)
        self.build()

    def build_node_parameters(self):
        """
        """
        module_logger.debug("RendererOutputExport - build_node_parameters()")

        group_builder = FnAttribute.GroupBuilder()
        # group_builder.set("node_version", 1)
        group_builder.set("filename", "")
        group_builder.set("Export.expandProcedurals", True)
        group_builder.set("Debug.logLevel", 20)
        group_builder.set("exportRendererOutput", "")

        parameters_hints = self.get_parameters_hints()

        for parameter in parameters_hints:
            self.setHintsForParameter(parameter, parameters_hints[parameter])

        self.setParametersTemplateAttr(group_builder.build())

    def get_parameters_hints(self):
        """
        """
        module_logger.debug("RendererOutputExport - get_parameters_hints()")

        # We describe here our Katana parameters and how they should appear/behave
        return {
            "filename": {
                "label": "Filename",
                "help": "The path on disk to the renderer output file we want to export.",
                "widget": "assetIdOutput",
                "fileTypes": "nsi|rib|ass"
            },
            "Export.expandProcedurals": {
                "label": "Expand Procedurals",
                "help": (
                    "Define if we expand the procedurals and store their data into the renderer output file we want "
                    "to export."
                ),
                "widget": "checkBox",
                "constant": True
            },
            "Debug.logLevel": {
                "label": "Log Level",
                "help": "Define the log level of the export process that will be visible in the terminal.",
                "widget": "mapper",
                "options": {
                    "Error": "40",
                    "Warning": "30",
                    "Info": "20",
                    "Debug": "10"
                },
                "constant": True
            },
            "exportRendererOutput": {
                "label": "Export Renderer Output",
                "help": (
                    "Export the state of the SceneGraph up to the point of this node to the file format of the "
                    "chosen renderer."
                ),
                "widget": "scriptButton",
                "buttonText": "Export Renderer Output",
                "scriptText": """node.export_renderer_output()"""
            },
        }


def build_renderer_output_export_op_chain(node, interface):
    """
    """
    module_logger.debug("RendererOutputExport - build_renderer_output_export_op_chain()")

    interface.setMinRequiredInputs(1)


def export_renderer_output(node):
    """
    """
    module_logger.debug("RendererOutputExport - export_renderer_output()")

    export_logger = logging.getLogger("katana_addons.Plugins.RendererOutputExport.Export")
    export_logger.setLevel(int(node.getParameter("Debug.logLevel").getValue(0)))

    from PyUtilModule import NodeDebugOutput

    export_geometry_producer = Nodes3DAPI.GetGeometryProducer(node)
    renderer = (
        export_geometry_producer.getAttribute("renderSettings.renderer").getValue() or
        RenderingAPI.RenderPlugins.GetDefaultRendererPluginName()
    )

    NodeDebugOutput.WriteRenderDebug(
        node=node,
        renderer=renderer,
        filename=node.getParameter("filename").getValue(0),
        expandProcedural=node.getParameter("Export.expandProcedurals").getValue(0),
        openInEditor=False,
        customEditor=None,
        log=export_logger
    )
    # NodeDebugOutput.WriteRenderOutput(
    #     node=node,
    #     renderer=renderer,
    #     filename=node.getParameter("filename").getValue(0),
    #     expandProcedural=node.getParameter("Export.expandProcedurals").getValue(0),
    #     openInEditor=False,
    #     customEditor=None,
    #     log=export_logger
    # )
    # NodeDebugOutput.WriteRenderOutputForRenderMethod(
    #     renderMethodName="batchRender",
    #     node=node,
    #     renderer=renderer,
    #     filename=node.getParameter("filename").getValue(0),
    #     expandProcedural=node.getParameter("Export.expandProcedurals").getValue(0),
    #     log=export_logger,
    #     openInEditor=False,
    #     customEditor=None,
    #     sceneGraphPath=None,
    #     printToConsole=True
    # )
