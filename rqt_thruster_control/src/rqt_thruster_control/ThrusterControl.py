import rclpy
from PyQt5.QtCore import QTimer
from rclpy.node import Node
from qt_gui.plugin import Plugin
from .ThrusterWidget import ThrusterWidget

class ThrusterControl(Plugin):

    def __init__(self, context):
        super(ThrusterControl, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('ThrusterControl')

        if not rclpy.ok():
            rclpy.init()
        self._internal_node= Node('rqt_thruster_control_node')
        # Create QWidget
        self._mainWindow = ThrusterWidget(self._internal_node)

        self._mainWindow.setWindowTitle(self._mainWindow.windowTitle())
        if context.serial_number() > 1:
            self._mainWindow.setWindowTitle(self._mainWindow.windowTitle() + (' (%d)' % context.serial_number()))
        self._mainWindow.setPalette(context._handler._main_window.palette())
        self._mainWindow.setAutoFillBackground(True)
        # Add widget to the user interface
        context.add_widget(self._mainWindow)

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
        self._mainWindow.shutdown_plugin()  
        if self._internal_node:
            self._internal_node.destroy_node()             