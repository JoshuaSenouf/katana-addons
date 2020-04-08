import Katana
import v1 as PassDefine


if PassDefine:
    PluginRegistry = [
        ("SuperTool", 2, "PassDefine",
            (PassDefine.PassDefineNode, PassDefine.GetEditor)),
    ]
