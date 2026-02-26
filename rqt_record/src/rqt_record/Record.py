import rclpy
from PyQt5.QtCore import QTimer
from rclpy.node import Node
from qt_gui.plugin import Plugin
from .RecordWidget import RecordWidget
from rclpy.subscription import Subscription

class Record(Plugin):

    def __init__(self, context):
        super(Record, self).__init__(context)
        self.setObjectName('BagRecord')
    
        if not rclpy.ok():
            rclpy.init()
        self._internal_node = Node('rqt_record_node')
        # Create QWidget
        self._mainWindow = RecordWidget()
        # Get path to UI file which should be in the "resource" folder of this package

        self._mainWindow.setWindowTitle(self._mainWindow.windowTitle())
        if context.serial_number() > 1:
            self._mainWindow.setWindowTitle(self._mainWindow.windowTitle() + (' (%d)' % context.serial_number()))
        self._mainWindow.setPalette(context._handler._main_window.palette())
        self._mainWindow.setAutoFillBackground(True)
        # Add widget to the user interface
        context.add_widget(self._mainWindow)       
        
        # Spin this thread
        self._timer = QTimer()
        self._timer.timeout.connect(self.__fetch_topics)
        self._timer.start(1)
        
    #def _spin_once(self):
       #if rclpy.ok() and self._internal_node:
        #    rclpy.spin_once(self._internal_node, timeout_sec=0.0)
    def __fetch_topics(self):
        list = []
        self.topic_lists = self._internal_node.get_topic_names_and_types(False)
        for name, types in self.topic_lists:
            list.append(name)
        self._mainWindow._loadListView(list)
            
    def shutdown_plugin(self):
        self._timer.stop()
        #self._timer.timeout.disconnect(self._spin_once) 
        if self._internal_node:
            self._internal_node.destroy_node()