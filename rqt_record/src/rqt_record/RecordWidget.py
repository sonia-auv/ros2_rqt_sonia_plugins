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
        
        self.topic_list = []
        self.filted_list = []
        self.left_item = ""
        self.right_item = ""
        
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
        if self.topic_list != data:
            self.listView.setStringList(sorted(data))
            self.topic_list = data
            self.filted_list = data 
               
    def _loadFeedback(self, data):
        self.stateLine.setText(data)
        
    def _loadTimer(self, data):
        self.timerLineEdit.setText(data)

    def __on_text_changed(self, text):
        if text != "":
            list = [ item for item in self.filted_list if text in item]
            self.listView.setStringList(sorted(list))
        else:
            self.listView.setStringList(sorted(self.filted_list))
            
    def __on_left_item_clicked(self, index):
        self.left_item = index.data()
        
    def __on_right_item_clicked(self, index):
        self.right_item = index.data()
             
    def _addBtn_action(self):
        right_list = self.selectedView.stringList()
        left_list = self.listView.stringList()
        if self.left_item != "" and self.left_item not in right_list:
            #add item to the right
            right_list.append(self.left_item)
            self.selectedView.setStringList(sorted(right_list))
            #remove item from the left
            left_list.remove(self.left_item)
            self.filted_list = left_list
            self.listView.setStringList(sorted(left_list))
            self.left_item = ""
        
    def _removeBtn_action(self):
        right_list = self.selectedView.stringList()
        left_list = self.listView.stringList()
        if self.right_item != ""and self.right_item not in left_list:
            #remove item from the right
            right_list.remove(self.right_item)
            self.selectedView.setStringList(sorted(right_list))
            #add item to the left
            left_list.append(self.right_item)
            self.filted_list = left_list
            self.listView.setStringList(sorted(left_list))
            self.right_item = ""

    def _enable_disable_ctrls(self, state):
        self.recordBtn.setEnabled(state)
        self.addBtn.setEnabled(state)
        self.removeBtn.setEnabled(state)
        self.bagName.setEnabled(state)               