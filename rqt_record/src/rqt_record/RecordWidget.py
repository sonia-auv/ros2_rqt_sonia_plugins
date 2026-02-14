import os

from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.QtCore import QStringListModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

class RecordWidget(QMainWindow):


    def __init__(self):
        super(RecordWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('RecordWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_record'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
        
        self.listView = QStringListModel()
        
        # Connect buttons
        self.recordBtn.clicked.connect(self._recordBtn_action)
        self.stopBtn.clicked.connect(self._stopBtn_action)
        self.addBtn.clicked.connect(self._addBtn_action)
        self.removeBtn.clicked.connect(self._removeBtn_action)
        
    def _loadListView(self, data):
        pass
        self.listView.setStringList(data)
        self.topicListView.setModel(self.listView)
        
    def _recordBtn_action(self):
        print("record")
        
    def _stopBtn_action(self):
        print("stop")
        
    def _addBtn_action(self):
        print("add")
        
    def _removeBtn_action(self):
        print("remove")
                