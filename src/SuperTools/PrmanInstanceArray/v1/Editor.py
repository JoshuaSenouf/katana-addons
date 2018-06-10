from Katana import QtCore
from Katana import QtGui
from Katana import UI4
from Katana import QT4Widgets
from Katana import QT4FormWidgets
from Katana import FormMaster

from Katana import NodegraphAPI
from Katana import Utils

resetParametersList = ["abcScatterPath", "abcGeoPaths"]


class PrmanInstanceArrayEditor(QtGui.QWidget):
    def __init__(self, parent, node):        
        self.__node = node

        QtGui.QWidget.__init__(self, parent)
        QtGui.QVBoxLayout(self)

        self.__frozen = True
        self.__updateOnIdle = False

        factory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory

        scenegraphGroup = QT4FormWidgets.PythonGroupPolicy("SceneGraph")
        scenegraphGroup.getWidgetHints()["hideTitle"] = True
        scenegraphGroup.getWidgetHints()["open"] = True

        instanceArrayLocPolicy = UI4.FormMaster.CreateParameterPolicy(
            scenegraphGroup, self.__node.getParameter("instanceArrayLoc"))
        scenegraphGroup.addChildPolicy(instanceArrayLocPolicy)
        instanceSourcesLocPolicy = UI4.FormMaster.CreateParameterPolicy(
            scenegraphGroup, self.__node.getParameter("instanceSourcesLoc"))
        scenegraphGroup.addChildPolicy(instanceSourcesLocPolicy)
        abcScatterPathPolicy = UI4.FormMaster.CreateParameterPolicy(
            scenegraphGroup, self.__node.getParameter("abcScatterPath"))
        scenegraphGroup.addChildPolicy(abcScatterPathPolicy)
        abcGeoPathsPolicy = UI4.FormMaster.CreateParameterPolicy(
            scenegraphGroup, self.__node.getParameter("abcGeoPaths"))
        scenegraphGroup.addChildPolicy(abcGeoPathsPolicy)
        loadingModePolicy = UI4.FormMaster.CreateParameterPolicy(
            scenegraphGroup, self.__node.getParameter("loadingMode"))
        scenegraphGroup.addChildPolicy(loadingModePolicy)

        widgetUI = factory.buildWidget(self, scenegraphGroup)
        self.layout().addWidget(widgetUI)


        scatterGroup = QT4FormWidgets.PythonGroupPolicy("Scatter")
        scatterGroup.getWidgetHints()["open"] = True

        scatterDensityPolicy = UI4.FormMaster.CreateParameterPolicy(
            scatterGroup, self.__node.getParameter("scatterDensity"))
        scatterGroup.addChildPolicy(scatterDensityPolicy)

        widgetUI = factory.buildWidget(self, scatterGroup)
        self.layout().addWidget(widgetUI)


        primvarsGroup = QT4FormWidgets.PythonGroupPolicy("Primvars")
        primvarsGroup.getWidgetHints()["open"] = True

        positionPrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("positionPrimvar"))
        primvarsGroup.addChildPolicy(positionPrimvarPolicy)
        rotationPrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("rotationPrimvar"))
        primvarsGroup.addChildPolicy(rotationPrimvarPolicy)
        scalePrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("scalePrimvar"))
        primvarsGroup.addChildPolicy(scalePrimvarPolicy)
        protoIndicesPrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("protoIndicesPrimvar"))
        primvarsGroup.addChildPolicy(protoIndicesPrimvarPolicy)
        idsPrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("idsPrimvar"))
        primvarsGroup.addChildPolicy(idsPrimvarPolicy)
        velocityPrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("velocityPrimvar"))
        primvarsGroup.addChildPolicy(velocityPrimvarPolicy)
        angularVelocityPrimvarPolicy = UI4.FormMaster.CreateParameterPolicy(
            primvarsGroup, self.__node.getParameter("angularVelocityPrimvar"))
        primvarsGroup.addChildPolicy(angularVelocityPrimvarPolicy)

        widgetUI = factory.buildWidget(self, primvarsGroup)
        self.layout().addWidget(widgetUI)


        motionBlurGroup = QT4FormWidgets.PythonGroupPolicy("MotionBlur")
        motionBlurGroup.getWidgetHints()["open"] = True

        useMotionBlurPolicy = UI4.FormMaster.CreateParameterPolicy(
            motionBlurGroup, self.__node.getParameter("useMotionBlur"))
        motionBlurGroup.addChildPolicy(useMotionBlurPolicy)
        intensityMultiplierPolicy = UI4.FormMaster.CreateParameterPolicy(
            motionBlurGroup, self.__node.getParameter("intensityMultiplier"))
        motionBlurGroup.addChildPolicy(intensityMultiplierPolicy)

        widgetUI = factory.buildWidget(self, motionBlurGroup)
        self.layout().addWidget(widgetUI)

    def showEvent(self, event):
        QtGui.QWidget.showEvent(self, event)
        if self.__frozen:
            self.__frozen = False
            self._thaw()
    
    def hideEvent(self, event):
        QtGui.QWidget.hideEvent(self, event)
        if not self.__frozen:
            self.__frozen = True
            self._freeze()
    
    def _thaw(self):
        self.__setupEventHandlers(True)
    
    def _freeze(self):
        self.__setupEventHandlers(False)

    def __setupEventHandlers(self, enabled):
        Utils.EventModule.RegisterEventHandler(self.__idle_callback,
            'event_idle', enabled=enabled)
        Utils.EventModule.RegisterCollapsedHandler(self.__updateCB,
            'parameter_finalizeValue', enabled=enabled)

    def __updateCB(self, args):
        if self.__updateOnIdle:
            return

        for arg in args:
            if arg[0] in "parameter_finalizeValue":
                node = arg[2].get("node")
                param = arg[2].get("param")
                if node == self.__node and param.getName() in resetParametersList:
                    self.__updateOnIdle = True
                    return

    def __idle_callback(self, *args, **kwargs):
        if self.__updateOnIdle:
            self.__updateOnIdle = False
            self.__node.resetNetwork()
