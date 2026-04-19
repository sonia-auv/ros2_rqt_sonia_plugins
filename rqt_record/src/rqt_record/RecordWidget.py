import os

from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QStringListModel, QSortFilterProxyModel, Qt
class RecordWidget(QMainWindow):

    def __init__(self):
        super(RecordWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('RecordWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_record'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
        
        self.leftListModel = QStringListModel()
        self.selectedListModel = QStringListModel()
        self.topic_list = []
        
        # filter proxy
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(self.leftListModel)
        self.proxy.setFilterCaseSensitivity(False)
        
        # ListView setup 
        self.selectedTopics.setModel(self.selectedListModel)
        self.allTopics.setModel(self.proxy)
        self.allTopics.show()
        self.selectedTopics.show()
        
        # Connect buttons and textbox
        self.addBtn.clicked.connect(self._addBtn_action)
        self.removeBtn.clicked.connect(self._removeBtn_action)
        self.topicFilter.textChanged.connect(self.proxy.setFilterFixedString)

    def _loadListView(self, data):       
        if self.topic_list != data:
            
            right_list = self.selectedListModel.stringList()
            right_list = [x for x in right_list if x in data]

            #update current viewed list
            self.leftListModel.setStringList(sorted(data))
            self.selectedListModel.setStringList(sorted(right_list))
            self.topic_list = data
               
    def _loadFeedback(self, data):
        self.stateLine.setText(data)
        
    def _loadTimer(self, data):
        self.timerLineEdit.setText(data)
             
    def _addBtn_action(self):
        index = self.allTopics.currentIndex()
        if not index.isValid():
            return
    
        source_index = self.proxy.mapToSource(index)
        item = self.leftListModel.data(source_index, Qt.DisplayRole)

        #Get current lists
        curr_left_list = self.leftListModel.stringList()
        curr_right_list = self.selectedListModel.stringList()

        #verify and add item to the right
        if item not in curr_right_list:
            curr_left_list.remove(item)
            curr_right_list.append(item)
            #update viewed lists
            self.leftListModel.setStringList(curr_left_list)
            self.selectedListModel.setStringList(curr_right_list)
        
    def _removeBtn_action(self):
        index = self.selectedTopics.currentIndex()
        if not index.isValid():
            return

        item = self.selectedListModel.data(index, Qt.DisplayRole)
        curr_left_list = self.leftListModel.stringList()

        if item not in curr_left_list:
            curr_left_list.append(item)
            self.leftListModel.setStringList(sorted(curr_left_list))

        # remove from right
        curr_right_list = self.selectedListModel.stringList()
        curr_right_list.remove(item)
        self.selectedListModel.setStringList(sorted(curr_right_list))

    def _enable_disable_ctrls(self, state):
        self.recordBtn.setEnabled(state)
        self.addBtn.setEnabled(state)
        self.removeBtn.setEnabled(state)
        self.bagName.setEnabled(state)               