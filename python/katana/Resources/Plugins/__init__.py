import logging

from Katana import NodegraphAPI


module_logger = logging.getLogger("katana_addons.Plugins.Register")
module_logger.setLevel(logging.WARNING)


try:
    import PassResolve
except Exception, error:
    module_logger.error("Error importing PassResolve: {error_msg}".format(error_msg=error))
else:
    PassResolve.PassResolve("PassResolve")
    NodegraphAPI.AddNodeFlavor("PassResolve", "Passes")

    module_logger.info("\"PassResolve\" SuperTool successfully registered.")

try:
    import RendererOutputExport
except Exception, error:
    module_logger.error("Error importing RendererOutputExport: {error_msg}".format(error_msg=error))
else:
    RendererOutputExport.RendererOutputExport("RendererOutputExport")
    NodegraphAPI.AddNodeFlavor("RendererOutputExport", "Passes")

    module_logger.info("\"RendererOutputExport\" SuperTool successfully registered.")
