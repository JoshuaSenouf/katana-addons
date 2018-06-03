import Katana
import v1 as PrmanInstanceArray

if PrmanInstanceArray:
    PluginRegistry = [
        ("SuperTool", 2, "PrmanInstanceArray",
                (PrmanInstanceArray.PrmanInstanceArrayNode,
                        PrmanInstanceArray.GetEditor)),
    ]
