import rclpy
import time
from PyQt5.QtCore import QTimer
from rclpy.node import Node, Client
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
        self.start_time = None
        self.past_list = []
        
        # Connect buttons
        self._mainWindow.recordBtn.clicked.connect(self._recordBtn_action)
        self._mainWindow.stopBtn.clicked.connect(self._stopBtn_action)
        self._mainWindow.pauseBtn.clicked.connect(self._pauseBtn_action)
        
        # Service
        self.record_client: Client = self._internal_node.create_client(RecordBagService, "/bag_server/record")    
        
        # Spin this thread
        self._timer = QTimer()
        self._timer.timeout.connect(self.__fetch_topics)
        self._timer.timeout.connect(self._spin_once)
        self._timer.start(10) 

        self.clock = QTimer()
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self._update_time)
        self.elapsed_sec = 0

    def _record_request_cb(self, resp):
        msg = resp.result().message
        if "Error" in msg:
            self._mainWindow.timerLineEdit.clear()
            self._mainWindow._loadFeedback(msg)
            return
             
        self._mainWindow._enable_disable_ctrls(False)
        self.clock.start()
        self._mainWindow._loadFeedback(msg)

    def _request_callback(self, resp):
        self._mainWindow._loadFeedback(resp.result().message)
        
    def _recordBtn_action(self):
        if not self.record_client.service_is_ready():
            self._mainWindow._loadFeedback("Bag server is not responding...")
        if self.is_paused:
            req = RecordBagService.Request()
            req.cmd = RecordBagService.Request.CMD_RESUME
      
            rep = self.record_client.call_async(req)
            rep.add_done_callback(self._request_callback)
            self.is_paused = False
            self._mainWindow.recordBtn.setEnabled(False)
            self.clock.start()
            return

        if self._mainWindow.bagName.text() != "" and len(self._mainWindow.selectedListModel.stringList()) != 0:
            req = RecordBagService.Request()
            req.cmd = RecordBagService.Request.CMD_START
            req.filename = self._mainWindow.bagName.text()
            req.topic_list = self._mainWindow.selectedListModel.stringList()
            
            rep = self.record_client.call_async(req)
            rep.add_done_callback(self._record_request_cb)
                   
    def _stopBtn_action(self):     
        req = RecordBagService.Request()
        req.cmd = RecordBagService.Request.CMD_STOP
        
        rep = self.record_client.call_async(req)
        rep.add_done_callback(self._request_callback)
        self.is_paused = False 
        self._mainWindow._enable_disable_ctrls(True)
        self._mainWindow.bagName.clear()
        self.clock.stop() 
        self.elapsed_sec = 0   
        
    def _pauseBtn_action(self):
        req = RecordBagService.Request()
        req.cmd = RecordBagService.Request.CMD_PAUSE
        
        rep = self.record_client.call_async(req)
        rep.add_done_callback(self._request_callback)
        self.is_paused = True
        self._mainWindow.recordBtn.setEnabled(True)
        self.clock.stop() 
    
    def _update_time(self):
        self.elapsed_sec +=1

        minutes = int(self.elapsed_sec // 60)
        seconds = int(self.elapsed_sec % 60)

        self._mainWindow._loadTimer(f"{minutes:02}:{seconds:02}")
              
    def __fetch_topics(self):
        list = []
        self.topic_lists = self._internal_node.get_topic_names_and_types(False)

        for name, types in self.topic_lists:
            pub_count = self._internal_node.get_publishers_info_by_topic(name)
            if len(pub_count) > 0:
                list.append(name)
        self._mainWindow._loadListView(list)

    def _spin_once(self):
        if rclpy.ok() and self._internal_node:
            rclpy.spin_once(self._internal_node, timeout_sec=0.0)
            
    def shutdown_plugin(self):   
        self.clock.stop()
        self.clock.timeout.disconnect(self._update_time)
        self._timer.stop()
        self._timer.timeout.disconnect(self._spin_once)
        self._timer.timeout.disconnect(self.__fetch_topics)
        self._stopBtn_action()
        if self._internal_node:
            self._internal_node.destroy_node()