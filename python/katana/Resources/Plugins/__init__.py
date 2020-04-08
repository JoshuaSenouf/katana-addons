import logging

from Katana import NodegraphAPI


logger = logging.getLogger("PassResolve.Register")
logger.setLevel(logging.WARNING)


try:
    import PassResolve
except Exception, error:
    logger.error("Error importing PassResolve: {error_msg}".format(error_msg=error))
else:
    PassResolve.PassResolve("PassResolve")
    NodegraphAPI.AddNodeFlavor("PassResolve", "Passes")

    logger.info("\"PassResolve\" SuperTool successfully registered.")
