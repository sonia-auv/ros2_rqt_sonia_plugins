import rclpy
from qt_gui.plugin import Plugin
from .VisionMainWidget import VisionMainWidget
from .ConfigWidget import ConfigWidget


class VisionStarter(Plugin):

    def __init__(self, context):
        super(VisionStarter, self).__init__(context)


        # Give QObjects reasonable names
        self.setObjectName('VisionStarter')
        self.configWidget = None

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
        self.__internal_node= rclpy.create_node('rqt_vision_node')
        self._mainWindow = VisionMainWidget(self.__internal_node)

        self._mainWindow.setWindowTitle(self._mainWindow.windowTitle())
        self.context_serial = context.serial_number()
        if context.serial_number() > 1:
            self._mainWindow.setWindowTitle(self._mainWindow.windowTitle() + (' (%d)' % context.serial_number()))
        self._mainWindow.setPalette(context._handler._main_window.palette())
        self._mainWindow.setAutoFillBackground(True)
        # Add widget to the user interface
        context.add_widget(self._mainWindow)

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        if self.configWidget is not None:
            self.configWidget.close()
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

    def trigger_configuration(self):
        self.configWidget = ConfigWidget(self._mainWindow,self.__internal_node)
        if self.context_serial > 1:
            self.configWidget.setWindowTitle(self.configWidget.windowTitle() + (' (%d)' % self.context_serial))
        self.configWidget.show()

