import rclpy
import signal
from PyQt5.QtCore import QTimer
from rclpy.node import Node
from rclpy.task import Future
from qt_gui.plugin import Plugin
from .RecordWidget import RecordWidget
from rclpy.action.client import ActionClient

from sonia_common_ros2.action import BagControl

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
        
        self.goal_handle = None
        
        # Connect buttons
        self._mainWindow.recordBtn.clicked.connect(self._recordBtn_action)
        self._mainWindow.stopBtn.clicked.connect(self._stopBtn_action)
        
        # Actions
        self.record_client = ActionClient(self._internal_node, BagControl, "BagRecord")    
        
        # Spin this thread
        self._timer = QTimer()
        self._timer.timeout.connect(self.__fetch_topics)
        self._timer.start(1)
    
    def _send_goal(self, filename, list):
        goal_msg = BagControl.Goal()
        goal_msg.filename = filename
        goal_msg.topic_list = list
        server_ready = self.record_client.wait_for_server(5)
        if not server_ready:
            self.show_error("Server isn't responding or running")
            return
        self.record_future=self.record_client.send_goal_async(goal_msg, self._feedback_callback)
        self.record_future.add_done_callback(self._goal_response_callback)   
        
    def _goal_response_callback(self, future: Future):
        self.goal_handle = future.result()
        if self.goal_handle.accepted:  
            self._mainWindow._enable_disable_ctrls(True)
    
    def _feedback_callback(self):
        pass
    
    def _recordBtn_action(self):
        topic_list = self._mainWindow.selectedView.stringList()
        if self._mainWindow.bagName.text() != "":
            self._send_goal(self._mainWindow.bagName.text(), topic_list)
            self._mainWindow._enable_disable_ctrls(False)
                   
    def _stopBtn_action(self):            
        cancel_req = self.record_client._cancel_goal_async(self.goal_handle)
        cancel_req.add_done_callback(self._cancel_response_cb)
        
    def _cancel_response_cb(self, resp: Future):            
        cancel_rep = resp.result()
        if(cancel_rep):
            self._mainWindow._enable_disable_ctrls(False)
              
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