import logging

import OpScripts as OS
import ScriptActions as SA

from Katana import (
    NodegraphAPI
)


logger = logging.getLogger("PassDefine.Editor")
logger.setLevel(logging.DEBUG)


class PassDefineNode(NodegraphAPI.SuperTool):
    def __init__(self):
        logger.debug("PassDefineNode - __init__()")
        self.addInputPort("pass_input")
        self.addOutputPort("pass_output")

        # TODO
        self.getParameters().createChildString("passRootLocation", "/root/passes")

        # TODO
        self.pass_data = {}
        self.pass_root_location = ""
        self.pass_name = ""
        self.pass_location = ""

        self.__buildDefaultNetwork()

    def __buildDefaultNetwork(self):
        logger.debug("PassDefineNode - __buildDefaultNetwork()")

        # Node(s) creation
        merge_inputs_node = self.create_merge_inputs_node()
        configure_pass_location_opscript_node = self.create_configure_pass_location_opscript_node()
        pass_define_ga_node = self.create_pass_define_ga_node()

        # Node(s) setup and logic
        self.update_pass_data(pass_define_ga_node)

        self.setup_merge_inputs_node(merge_inputs_node)
        self.setup_configure_pass_location_opscript_node(configure_pass_location_opscript_node, pass_define_ga_node)
        self.update_pass_location(pass_define_ga_node)

        # Connection(s) and layout
        self.getSendPort(self.getInputPortByIndex(0).getName()).connect(merge_inputs_node.getInputPortByIndex(0))
        merge_inputs_node.getOutputPortByIndex(0).connect(configure_pass_location_opscript_node.getInputPortByIndex(0))
        configure_pass_location_opscript_node.getOutputPortByIndex(0).connect(pass_define_ga_node.getInputPortByIndex(0))

        SA.change_node_layout(merge_inputs_node)
        SA.change_node_layout(configure_pass_location_opscript_node)
        SA.change_node_layout(pass_define_ga_node)

        # Output(s)
        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(
            pass_define_ga_node.getOutputPortByIndex(0))

    def addParameterHints(self, attrName, inputDict):
        logger.debug("PassDefineNode - addParameterHints()")

        inputDict.update(_node_fields_hints.get(attrName, {}))

    def create_merge_inputs_node(self):
        logger.debug("PassDefineNode - create_merge_inputs_node()")

        merge_inputs_node = NodegraphAPI.CreateNode("Merge", self)
        merge_inputs_node.setName("Merge_Input")

        SA.add_node_reference_param(self, "node_merge", merge_inputs_node)

        return merge_inputs_node

    def create_configure_pass_location_opscript_node(self):
        logger.debug("PassDefineNode - create_configure_pass_location_opscript_node()")

        configure_pass_location_opscript_node = NodegraphAPI.CreateNode("OpScript", self)
        configure_pass_location_opscript_node.setName("OpScript_CreatePassLocation")

        SA.add_node_reference_param(self, "node_opscript_create_pass_location", configure_pass_location_opscript_node)

        return configure_pass_location_opscript_node

    def create_pass_define_ga_node(self):
        logger.debug("PassDefineNode - create_pass_define_ga_node()")

        pass_define_ga_node = NodegraphAPI.CreateNode("PassDefineGA", self)
        pass_define_ga_node.setName("PassDefineGA_PassParameters")

        SA.add_node_reference_param(self, "node_pass_define_ga", pass_define_ga_node)

        return pass_define_ga_node

    def update_pass_data(self, pass_define_ga_node):
        logger.debug("PassDefineNode - update_pass_data()")

        # TODO
        self.pass_data["enablePass"] = {}
        self.pass_data["enablePass"]["value"] = pass_define_ga_node.getParameter(
            "args.PassDefine.enablePass.value"
        ).getValue(0)
        self.pass_data["enablePass"]["enable"] = pass_define_ga_node.getParameter(
            "args.PassDefine.enablePass.enable"
        ).getValue(0)

        if not self.pass_data["enablePass"].get("default"):
            self.pass_data["enablePass"]["default"] = pass_define_ga_node.getParameter(
                "args.PassDefine.enablePass.default"
            ).getValue(0)

        # TODO
        self.pass_data["definition"] = {}
        for child in pass_define_ga_node.getParameter("args.PassDefine.definition").getChildren():
            child_param_name = child.getName()

            if child_param_name == "__hints":
                continue

            self.pass_data["definition"][child_param_name] = {}
            self.pass_data["definition"][child_param_name]["value"] = pass_define_ga_node.getParameter(
                "args.PassDefine.definition.{param_name}.value".format(
                    param_name=child_param_name
                )
            ).getValue(0)
            self.pass_data["definition"][child_param_name]["enable"] = pass_define_ga_node.getParameter(
                "args.PassDefine.definition.{param_name}.enable".format(
                    param_name=child_param_name
                )
            ).getValue(0)

            if not self.pass_data["definition"][child_param_name].get("default"):
                self.pass_data["definition"][child_param_name]["default"] = pass_define_ga_node.getParameter(
                    "args.PassDefine.definition.{param_name}.default".format(
                        param_name=child_param_name
                    )
                ).getValue(0)

    def setup_merge_inputs_node(self, merge_node):
        logger.debug("PassDefineNode - setup_merge_inputs_node()")

        merge_node.addInputPort("input_scene")

    def setup_configure_pass_location_opscript_node(self, opscript_node, pass_define_ga_node):
        logger.debug("PassDefineNode - setup_configure_pass_location_opscript_node()")

        opscript_node.getParameter("script.lua").setValue(OS.configure_pass_location_opscript(), 0)

        configure_pass_location_opscript_usergroup = opscript_node.getParameters().createChildGroup("user")
        configure_pass_location_opscript_usergroup.createChildString("passRootLocation", "")
        configure_pass_location_opscript_usergroup.createChildString("enablePass", "")
        configure_pass_location_opscript_usergroup.createChildString("type", "")
        configure_pass_location_opscript_usergroup.createChildString("prefix", "")
        configure_pass_location_opscript_usergroup.createChildString("element", "")
        configure_pass_location_opscript_usergroup.createChildString("suffix", "")

        opscript_node.getParameter("user.passRootLocation").setExpression(
            ("getParent().getNode().getParameter(\"passRootLocation\").getValue(frame)")
        )
        opscript_node.getParameter("user.enablePass").setExpression(
            ("getParent().getNode().getChild(\"{node_name}\").getParameter(\"args.PassDefine.enablePass" +
            ".value\").getValue(frame) if getParent().getNode().getChild(\"{node_name}\")." +
            "getParameter(\"args.PassDefine.enablePass.enable\").getValue(frame) else " +
            "{default_value}").format(
                node_name=pass_define_ga_node.getName(),
                default_value=self.pass_data["enablePass"]["default"]
            ), True)

        for param_name in self.pass_data["definition"].keys():
            opscript_node.getParameter("user.{param_name}".format(param_name=param_name)).setExpression(
                ("getParent().getNode().getChild(\"{node_name}\").getParameter(\"args.PassDefine.definition" +
                ".{param_name}.value\").getValue(frame) if getParent().getNode().getChild(\"{node_name}\")." +
                "getParameter(\"args.PassDefine.definition.{param_name}.enable\").getValue(frame) else " +
                "\"{default_value}\"").format(
                    node_name=pass_define_ga_node.getName(),
                    param_name=param_name,
                    default_value=self.pass_data["definition"][param_name]["default"]
                ), True)

        opscript_node.getParameter("applyWhen").setValue("immediate", 0)
        opscript_node.getParameter("applyWhere").setValue("at all locations", 0)
        opscript_node.getParameter("inputBehavior").setValue("only valid", 0)

    def update_pass_location(self, pass_define_ga_node):
        logger.debug("PassDefineNode - update_pass_location()")

        # TODO: Use the correct frame time instead
        self.pass_root_location = self.getParameter("passRootLocation").getValue(0)
        self.pass_name = "{type}_{prefix}_{element}_{suffix}".format(
            type=(self.pass_data["definition"]["type"]["value"]
                if self.pass_data["definition"]["type"]["enable"]
                else self.pass_data["definition"]["type"]["default"]),
            prefix=(self.pass_data["definition"]["prefix"]["value"]
                if self.pass_data["definition"]["prefix"]["enable"]
                else self.pass_data["definition"]["prefix"]["default"]),
            element=(self.pass_data["definition"]["element"]["value"]
                if self.pass_data["definition"]["element"]["enable"]
                else self.pass_data["definition"]["element"]["default"]),
            suffix=(self.pass_data["definition"]["suffix"]["value"]
                if self.pass_data["definition"]["suffix"]["enable"]
                else self.pass_data["definition"]["suffix"]["default"])
        )
        self.pass_location = "{pass_root_location}/{pass_name}".format(
            pass_root_location=self.pass_root_location,
            pass_name=self.pass_name
        )

        pass_define_ga_node.getParameters().getChild("CEL").setExpression(
            ("\"{pass_location}\"").format(
                pass_location=self.pass_location
            )
        )

    def reset_node_network(self):
        logger.debug("PassDefineNode - reset_node_network()")

        for child_node in self.getChildren():
            child_node.delete()

        self.__buildDefaultNetwork()


_node_fields_hints = {
    "PassDefine.passRootLocation": {
        "label": "Pass Root Location",
        "help": "Define under which location the \"pass\" location type should be created.",
        "widget": "scenegraphLocation"
    }
}
