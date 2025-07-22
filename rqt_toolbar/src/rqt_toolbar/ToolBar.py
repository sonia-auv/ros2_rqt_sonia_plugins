import os
from rclpy.node import Node
import rclpy

from qt_gui.plugin import Plugin
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtCore import QTimer

from .ToolbarSetControlMode import SetModeControlWidget
from .ToolbarBatteryWidget import BatteryWidget
from .ToolbarCpuTempWidget import CpuTempWidget
from .ToolbarKillmissionWidget import KillMissionWidget
from .ToolbarCameraWidget import CameraWidget


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
        if not rclpy.ok():
            rclpy.init()
        self._internal_node = Node('rqt_toolbar_node')

        self._toolbar = QToolBar()
        # self._palette = Palette()
        self._setControlModeWidget = SetModeControlWidget(self._internal_node)
        # self._warnings = WarningsWidget()
        self._camera = CameraWidget()
        # context._handler._main_window.setPalette(self._palette.palette())
        self._batteryWidget1 = BatteryWidget(1, self._internal_node)
        self._batteryWidget2 = BatteryWidget(2, self._internal_node)
        self._killMissionWidget = KillMissionWidget(self._internal_node)
        self._tempWidget1 = CpuTempWidget(os.getenv("AUV", "AUV"), self._internal_node)

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
        self._timer = QTimer()
        self._timer.timeout.connect(self._spin_once)
        self._timer.start(10)

    def _spin_once(self):
        if rclpy.ok() and self._internal_node:
            rclpy.spin_once(self._internal_node, timeout_sec=0.0)
    
    def shutdown_plugin(self):
        self._timer.stop()
        self._timer.timeout.disconnect(self._spin_once)
        if self._internal_node:
            self._internal_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()             
