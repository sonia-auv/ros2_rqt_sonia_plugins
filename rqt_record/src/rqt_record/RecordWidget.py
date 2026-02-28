import os

from pathlib import Path
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.QtCore import Qt, QStringListModel, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

class RecordWidget(QMainWindow):

    def __init__(self):
        super(RecordWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('RecordWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_record'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
        home = Path.home()
        self.envList = {
            'LOCAL' : str(home)+'/bags/',
            'AUV8' : '/home/sonia/ssd/bags/',
            'LITE1' : '/home/sonia/ssd/bags/'}
        
        self.listView = QStringListModel()
        self.selectedView = QStringListModel()
        self.topicList = []
        self.left_item = ""
        self.right_item = ""
        
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
        if self.bagName != "":
            topic_list = self.selectedView.stringList()
  
        
    def _stopBtn_action(self):
        print("stop")
        
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
                