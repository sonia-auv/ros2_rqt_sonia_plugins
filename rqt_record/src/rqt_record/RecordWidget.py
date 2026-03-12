import os

from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QStringListModel

class RecordWidget(QMainWindow):

    def __init__(self):
        super(RecordWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('RecordWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_record'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
        
        self.listView = QStringListModel()
        self.selectedView = QStringListModel()
        
        self.left_item = ""
        self.right_item = ""
        self.filter_text = ""
        
        # ListView setup 
        self.selectedTopics.setModel(self.selectedView)
        self.allTopics.setModel(self.listView)

        self.allTopics.show()
        self.selectedTopics.show()
        
        # Connect buttons
        self.addBtn.clicked.connect(self._addBtn_action)
        self.removeBtn.clicked.connect(self._removeBtn_action)
        self.allTopics.clicked.connect(self.__on_left_item_clicked)
        self.selectedTopics.clicked.connect(self.__on_right_item_clicked)
        self.topicFilter.textChanged.connect(self.__on_text_changed)
                
    def _loadListView(self, data):
        if self.filter_text != "":
            list = [ s for s in data if self.filter_text in s]
            self.listView.setStringList(list)
        else:
            self.listView.setStringList(data)

    def _loadFeedback(self, data):
        self.stateLine.setText(data)
        
    def _loadTimer(self, data):
        self.timerLine.setText(data)

    def __on_text_changed(self, text):
        self.filter_text = text
            
    def __on_left_item_clicked(self, index):
        self.left_item = index.data()
        
    def __on_right_item_clicked(self, index):
        self.right_item = index.data()
      
    def _enable_disable_ctrls(self, state):
        self.recordBtn.setEnabled(state)
        self.addBtn.setEnabled(state)
        self.removeBtn.setEnabled(state)
        self.bagName.setEnabled(state)
        
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
                