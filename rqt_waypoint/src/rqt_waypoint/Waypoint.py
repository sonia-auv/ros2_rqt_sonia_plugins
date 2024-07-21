import os
#import rospy
#import rospkg
import rclpy

from threading import Thread
from qt_gui.plugin import Plugin
import rclpy.executors

from .WaypointWidget import WaypointWidget


class Waypoint(Plugin):

    def __init__(self, context):
        super(Waypoint, self).__init__(context)


        # Give QObjects reasonable names
        self.setObjectName('WaypointWidget')

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
        self.__internal_node = rclpy.create_node('rqt_waypoint_node')
        self._mainWindow = WaypointWidget(self.__internal_node)

        self._mainWindow.setWindowTitle(self._mainWindow.windowTitle())
        if context.serial_number() > 1:
            self._mainWindow.setWindowTitle(self._mainWindow.windowTitle() + (' (%d)' % context.serial_number()))
        self._mainWindow.setPalette(context._handler._main_window.palette())
        self._mainWindow.setAutoFillBackground(True)
        # Add widget to the user interface
        context.add_widget(self._mainWindow)
        #Thread(target=rclpy.spin, args=[self.__internal_node], daemon=True).start()

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        self._mainWindow.shutdown_plugin()
        pass

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
