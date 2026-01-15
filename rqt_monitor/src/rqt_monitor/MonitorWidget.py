import os

from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

class MonitorWidget(QMainWindow):


    def __init__(self):
        super(MonitorWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('MonitorWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_monitor'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
        
        self.auv = os.getenv("AUV")
        if self.auv is None:
            self.auv = "NaN"
        self.auvName.setText(self.auv)       
        self.header = ["Node", "State", "Quality"]
        self.state_list = ["STOPPED", "INITIALIZING", "RUNNING","IDLE"]
        self.quality_list = [["UNKNOWN", "OK", "DEGRADE"], ["#d6d6d6", "#c8f7c5", "#f5c6cb"]]
        
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(self.header)
                
        self.monitorTable.setModel(self.model) 
        self.monitorTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  
        self.monitorTable.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #263A4F; color: white}") 

    def _monitor_display(self, nodes):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.header)
        for m in nodes:
            node_name = QStandardItem(str(m.node_name))
            state = QStandardItem(self.state_list[m.state])
            quality = QStandardItem(self.quality_list[0][m.quality])
            quality.setBackground(QColor(self.quality_list[1][m.quality]))
            
            self.model.appendRow([node_name, state, quality])
   