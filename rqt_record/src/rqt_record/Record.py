import rclpy
import signal
from PyQt5.QtCore import QTimer
from rclpy.node import Node, Client
from rclpy.task import Future
from qt_gui.plugin import Plugin
from .RecordWidget import RecordWidget

from sonia_common_ros2.srv import RecordBagService

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
        
        self.is_paused = False
        self.is_recording = False
        
        # Connect buttons
        self._mainWindow.recordBtn.clicked.connect(self._recordBtn_action)
        self._mainWindow.stopBtn.clicked.connect(self._stopBtn_action)
        self._mainWindow.pauseBtn.clicked.connect(self._pauseBtn_action)
        
        # Actions
        self.record_client: Client = self._internal_node.create_client(RecordBagService,"/bag_recorder/record")    
        
        # Spin this thread
        self._timer = QTimer()
        self._timer.timeout.connect(self.__fetch_topics)
        self._timer.start(1) 
        
    def _request_callback(self, resp):
        self._mainWindow._loadFeedback(resp.result().state)
        
    def _recordBtn_action(self):
        
        if self.is_paused:
            req = RecordBagService.Request()
            req.cmd = RecordBagService.Request.CMD_RESUME
      
            rep = self.record_client.call_async(req)
            rep.add_done_callback(self._request_callback)
            self.is_paused = False
            self._mainWindow.recordBtn.setEnabled(False) 
            return

        if self._mainWindow.bagName.text() != "":
            req = RecordBagService.Request()
            req.cmd = RecordBagService.Request.CMD_START
            req.filename = self._mainWindow.bagName.text()
            req.topic_list = self._mainWindow.selectedView.stringList()
            
            rep = self.record_client.call_async(req)
            rep.add_done_callback(self._request_callback)
            self._mainWindow._enable_disable_ctrls(False)
                   
    def _stopBtn_action(self):     
        req = RecordBagService.Request()
        req.cmd = RecordBagService.Request.CMD_STOP
        
        rep = self.record_client.call_async(req)
        rep.add_done_callback(self._request_callback)
        self.is_paused = False 
        self._mainWindow._enable_disable_ctrls(True)
        self._mainWindow.bagName.clear()    
        
    def _pauseBtn_action(self):
        req = RecordBagService.Request()
        req.cmd = RecordBagService.Request.CMD_PAUSE
        
        rep = self.record_client.call_async(req)
        rep.add_done_callback(self._request_callback)
        self.is_paused = True
        self._mainWindow.recordBtn.setEnabled(True) 
              
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