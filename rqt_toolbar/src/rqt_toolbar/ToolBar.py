import imp
import os
from threading import Thread
import rclpy

from qt_gui.plugin import Plugin
from PyQt5.QtWidgets import QMainWindow, QToolBar

from .ToolbarSetControlMode import SetModeControlWidget
from .ToolbarBatteryWidget import BatteryWidget
from .ToolbarCpuTempWidget import CpuTempWidget
from .ToolbarKillmissionWidget import KillMissionWidget
from .ToolbarCameraWidget import CameraWidget
from .Palette import Palette
from .ToolbarWarningsWidget import WarningsWidget


class ToolBar(Plugin):

    def __init__(self, context):
        super(ToolBar, self).__init__(context)

        # Give QObjects reasonable namesBatteryWidget
        self.setObjectName("EnableAxis")

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser

        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument(
            "-q", "--quiet", action="store_true", dest="quiet", help="Put plugin in silent mode"
        )
        args, unknowns = parser.parse_known_args(context.argv())

        if not args.quiet:
            print("arguments: ", args)
            print("unknowns: ", unknowns)

        self.__internal_node = rclpy.create_node('rqt_toolbar_node')

        self._toolbar = QToolBar()
        # self._palette = Palette()
        self._setControlModeWidget = SetModeControlWidget(self.__internal_node)
        # self._warnings = WarningsWidget()
        self._camera = CameraWidget()
        # context._handler._main_window.setPalette(self._palette.palette())
        self._batteryWidget1 = BatteryWidget(1, self.__internal_node)
        self._batteryWidget2 = BatteryWidget(2, self.__internal_node)
        self._killMissionWidget = KillMissionWidget(self.__internal_node)
        self._tempWidget1 = CpuTempWidget(os.getenv("AUV", "AUV"), self.__internal_node)

        # Add widget to the user interface
        self._toolbar.addWidget(self._setControlModeWidget)
        # self._toolbar.addWidget(self._warnings)
        self._toolbar.addWidget(self._camera)
        self._toolbar.addWidget(self._tempWidget1)
        self._toolbar.addWidget(self._batteryWidget1)
        self._toolbar.addWidget(self._batteryWidget2)
        self._toolbar.addWidget(self._killMissionWidget)

        context.add_toolbar(self._toolbar)

        # Spin this thread
        self._thread3 = Thread(target=rclpy.spin, name="rqt_toolbar", args=[self.__internal_node], daemon=True)
        self._thread3.start()
    
    def shutdown_plugin(self):   
        if(self._thread3.getName=="rqt_toolbar"):
            self._thread3.join()

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(EnableAxisWidgetk)
        pass

    # def trigger_configuration(self):
    # Comment in to signal that the plugin has a way to configure
    # This will enable a setting button (gear icon) in each dock widget title bar
    # Usually used to open a modal configuration dialog
