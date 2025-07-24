import rclpy
from PyQt5.QtCore import QTimer
from rclpy.node import Node
from qt_gui.plugin import Plugin
from .DvlWidget import DvlWidget
from rclpy.subscription import Subscription

from sonia_common_ros2.msg import BodyVelocityDVL

class ProviderDvl(Plugin):

    def __init__(self, context):
        super(ProviderDvl, self).__init__(context)
        self.setObjectName('ProviderDvl')
    
        if not rclpy.ok():
            rclpy.init()
        self._internal_node = Node('rqt_dvl_node')
        # Create QWidget
        self._mainWindow = DvlWidget()
        # Get path to UI file which should be in the "resource" folder of this package

        self._mainWindow.setWindowTitle(self._mainWindow.windowTitle())
        if context.serial_number() > 1:
            self._mainWindow.setWindowTitle(self._mainWindow.windowTitle() + (' (%d)' % context.serial_number()))
        self._mainWindow.setPalette(context._handler._main_window.palette())
        self._mainWindow.setAutoFillBackground(True)
        # Add widget to the user interface
        context.add_widget(self._mainWindow)

        self._dvl_subscriber: Subscription = self._internal_node.create_subscription(BodyVelocityDVL,"/provider_dvl/dvl_velocity", self._mainWindow._dvl_subscriber_cb, 10)

         # Spin this thread
        self._timer = QTimer()
        self._timer.timeout.connect(self._spin_once)
        self._timer.start(10)
        
    def _spin_once(self):
        if rclpy.ok() and self._internal_node:
            rclpy.spin_once(self._internal_node, timeout_sec=0.0)

    def shutdown_plugin(self):
        self._dvl_subscriber.destroy()
        self._timer.stop()
        self._timer.timeout.disconnect(self._spin_once) 
        if self._internal_node:
            self._internal_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()