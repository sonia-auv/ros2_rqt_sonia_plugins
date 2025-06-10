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

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())

        if not args.quiet:
            print('arguments: ', args)
            print('unknowns: ', unknowns)
        if not rclpy.ok():
            rclpy.init()
        self.__internal_node= Node('rqt_thruster_control_node')
        # Create QWidget
        self._mainWindow = ThrusterWidget(self.__internal_node)

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
        if rclpy.ok() and self.__internal_node:
            rclpy.spin_once(self.__internal_node, timeout_sec=0.0)

    def shutdown_plugin(self):
        self._timer.stop()
        self._timer.timeout.disconnect(self._spin_once)
        self._mainWindow.shutdown_plugin()  
        if self.__internal_node:
            self.__internal_node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
             

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog
