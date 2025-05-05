import rclpy
from rclpy.node import Node
from rqt_gui_py.plugin import Plugin
from threading import Thread
from .actuator_widget import ActuatorWidget

class Actuator(Plugin):

    def __init__(self, context):
        super(Actuator, self).__init__(context)
        self.setObjectName('Actuator')

        #rclpy.init(context=context)
        self.__internal_node= Node('rqt_actuator')
        self._widget = ActuatorWidget(self.__internal_node)

        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        self._widget.setPalette(context._handler._main_window.palette())
        self._widget.setAutoFillBackground(True)
        context.add_widget(self._widget)

        self._thread =Thread(target=rclpy.spin, args=[self.__internal_node], daemon=True)
        self._thread.start()

    def save_settings(self, plugin_settings, instance_settings):
        self._widget.save_settings(plugin_settings, instance_settings)

    def restore_settings(self, plugin_settings, instance_settings):
        self._widget.restore_settings(plugin_settings, instance_settings)

    def shutdown_plugin(self):
        rclpy.shutdown()
        self._thread.join()
        self.__internal_node.destroy_node()
        self._widget.shutdown_plugin()
