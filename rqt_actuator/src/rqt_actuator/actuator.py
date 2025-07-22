import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from PyQt5.QtCore import QTimer
from .actuator_widget import ActuatorWidget

class Actuator(Plugin):

    def __init__(self, context):
        super(Actuator, self).__init__(context)
        self.setObjectName('Actuator')

        #rclpy.init(context=context)
        self._internal_node= Node('rqt_actuator')
        self._widget = ActuatorWidget(self._internal_node)

        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        self._widget.setPalette(context._handler._main_window.palette())
        self._widget.setAutoFillBackground(True)
        context.add_widget(self._widget)

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
        self._widget.shutdown_plugin()
        
    def save_settings(self, plugin_settings, instance_settings):
        self._widget.save_settings(plugin_settings, instance_settings)

    def restore_settings(self, plugin_settings, instance_settings):
        self._widget.restore_settings(plugin_settings, instance_settings)