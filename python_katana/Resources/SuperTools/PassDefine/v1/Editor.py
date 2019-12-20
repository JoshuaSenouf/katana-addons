import logging

import ScriptActions as SA

from Katana import (
    QT4FormWidgets,
    QtWidgets,
    UI4,
    Utils
)


logger = logging.getLogger("PassDefine.Editor")
logger.setLevel(logging.DEBUG)

update_parameters_list = [
    "passRootLocation"
]


class PassDefineEditor(QtWidgets.QWidget):
    def __init__(self, parent, node):
        logger.debug("PassDefineEditor - __init__()")

        self.__node = node

        QtWidgets.QWidget.__init__(self, parent)
        QtWidgets.QVBoxLayout(self)

        self.__frozen = True
        self.__updateOnIdle = False

        katana_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory

        scenegraph_group = QT4FormWidgets.PythonGroupPolicy("SceneGraph")
        scenegraph_group.getWidgetHints()["hideTitle"] = True
        scenegraph_group.getWidgetHints()["open"] = True

        scenegraph_pass_root_location_policy = UI4.FormMaster.CreateParameterPolicy(
            scenegraph_group, self.__node.getParameter("passRootLocation"))
        scenegraph_group.addChildPolicy(scenegraph_pass_root_location_policy)

        widget_ui = katana_factory.buildWidget(self, scenegraph_group)

        self.layout().addWidget(widget_ui)

        # TODO
        self.create_ui_from_generic_assign("PassDefine", "pass_define_ga")

        # TODO
        self.pass_define_ga_node = SA.get_reference_node(self.__node, "pass_define_ga")
        # TODO
        self.pass_define_ga_update_parameters_list = [
            self.pass_define_ga_node.getParameter("args.PassDefine.definition.type.enable"),
            self.pass_define_ga_node.getParameter("args.PassDefine.definition.prefix.enable"),
            self.pass_define_ga_node.getParameter("args.PassDefine.definition.element.enable"),
            self.pass_define_ga_node.getParameter("args.PassDefine.definition.suffix.enable")
        ]

    def create_ui_from_generic_assign(self, generic_assign_name, node_reference_name):
        logger.debug("PassDefineEditor - create_ui_from_generic_assign()")

        generic_assign_node = SA.get_reference_node(self.__node, node_reference_name)

        group_parameter = generic_assign_node.getParameter("args.{generic_assign_name}".format(
            generic_assign_name=generic_assign_name
        ))

        policy = UI4.FormMaster.CreateParameterPolicy(None, group_parameter)
        widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        widget = widget_factory.buildWidget(self, policy)

        self.layout().addWidget(widget)

    def create_ui_group_from_generic_assign(self, generic_assign_name, node_reference_name, group_name):
        generic_assign_node = SA.get_reference_node(self.__node, node_reference_name)

        group_parameter = generic_assign_node.getParameter("args.{generic_assign_name}.{group_name}".format(
            generic_assign_name=generic_assign_name,
            group_name=group_name
        ))

        policy = UI4.FormMaster.CreateParameterPolicy(None, group_parameter)
        widget_factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        widget = widget_factory.buildWidget(self, policy)

        self.layout().addWidget(widget)

    def showEvent(self, event):
        QtWidgets.QWidget.showEvent(self, event)
        if self.__frozen:
            self.__frozen = False
            self._thaw()

    def hideEvent(self, event):
        QtWidgets.QWidget.hideEvent(self, event)
        if not self.__frozen:
            self.__frozen = True
            self._freeze()

    def _thaw(self):
        self.__setupEventHandlers(True)

    def _freeze(self):
        self.__setupEventHandlers(False)

    def __setupEventHandlers(self, enabled):
        Utils.EventModule.RegisterEventHandler(self.__idle_callback,
            "event_idle", enabled=enabled)
        Utils.EventModule.RegisterCollapsedHandler(self.__updateCB,
            "parameter_finalizeValue", enabled=enabled)

    def __updateCB(self, args):
        logger.debug("PassDefineEditor - __updateCB()")

        if self.__updateOnIdle:
            return

        for arg in args:
            if arg[0] in "parameter_finalizeValue":
                node = arg[2].get("node")
                param = arg[2].get("param")

                if node == self.__node and param.getName() in update_parameters_list:
                    self.__updateOnIdle = True

                    return
                elif node == self.pass_define_ga_node and param in self.pass_define_ga_update_parameters_list:
                    self.__updateOnIdle = True

                    return

    def __idle_callback(self, *args, **kwargs):
        if self.__updateOnIdle:
            self.__updateOnIdle = False

            self.__node.update_pass_location(self.pass_define_ga_node)
            # self.__node.reset_node_network()
