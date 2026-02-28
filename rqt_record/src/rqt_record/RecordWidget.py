import os

from pathlib import Path
import subprocess
import signal
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.QtCore import QStringListModel

class RecordWidget(QMainWindow):

    def __init__(self):
        super(RecordWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('RecordWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_record'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)

        self.envList = {
            'LOCAL' : str(Path.home())+'/bags/',
            'AUV8' : '/home/sonia/ssd/bags/',
            'LITE1' : '/home/sonia/ssd/bags/'}
        
        self.listView = QStringListModel()
        self.selectedView = QStringListModel()
        self.topicList = []
        self.proc = None
        self.left_item = ""
        self.right_item = ""
        
        self.subprocess = subprocess.run
        
        # ListView setup 
        self.selectedTopics.setModel(self.selectedView)
        self.allTopics.setModel(self.listView)
        self.allTopics.show()
        self.selectedTopics.show()
        
        # Connect buttons
        self.recordBtn.clicked.connect(self._recordBtn_action)
        self.stopBtn.clicked.connect(self._stopBtn_action)
        self.addBtn.clicked.connect(self._addBtn_action)
        self.removeBtn.clicked.connect(self._removeBtn_action)
        self.allTopics.clicked.connect(self.__on_left_item_clicked)
        self.selectedTopics.clicked.connect(self.__on_right_item_clicked)
                
    def _loadListView(self, data):
        if self.topicList != data:
            self.listView.setStringList(data)
            self.topicList = data
            
    def __on_left_item_clicked(self, index):
        self.left_item = index.data()
        
    def __on_right_item_clicked(self, index):
        self.right_item = index.data()
    
    def _recordBtn_action(self):
        print(self.envList[self.envChoice.currentText()])
        topic_list = self.selectedView.stringList()
        if self.bagName.text() != "":
            dir = self.envList[self.envChoice.currentText()]+self.bagName.text()
            self.proc = subprocess.Popen(["ros2","bag","record","-o", dir, *topic_list])
            
            self.recordBtn.setEnabled(False)
            self.addBtn.setEnabled(False)
            self.removeBtn.setEnabled(False)
            self.bagName.setEnabled(False)
                  
    def _stopBtn_action(self):
        if self.proc != None:
            self.proc.send_signal(signal.SIGINT)
            self.proc.wait()
            self.proc = None
            
            self.recordBtn.setEnabled(True)
            self.addBtn.setEnabled(True)
            self.removeBtn.setEnabled(True)
            self.bagName.setEnabled(True)
        
    def _addBtn_action(self):
        current_list = self.selectedView.stringList()
        if self.left_item != "" and self.left_item not in current_list:
            current_list.append(self.left_item)
            self.selectedView.setStringList(current_list)
            self.left_item = ""
        
    def _removeBtn_action(self):
        if self.right_item != "":
            current_list = self.selectedView.stringList()
            current_list.remove(self.right_item)
            self.selectedView.setStringList(current_list)
            self.right_item = ""
                