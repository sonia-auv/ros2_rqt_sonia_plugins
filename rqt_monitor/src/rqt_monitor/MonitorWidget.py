import os

from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from sonia_common_ros2.msg import NodeStatus

class MonitorWidget(QMainWindow):


    def __init__(self):
        super(MonitorWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('MonitorWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_monitor'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
        
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["Node", "State", "Quality"])
                
        self.monitorTable.setModel(self.model) 
        self.monitorTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)   

    def _table_fill(self, nodes):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Node", "State", "Quality"])
        for m in nodes:
            self.model.appendRow([
                QStandardItem(str(m.node_name)),
                QStandardItem(str(m.state)),
                QStandardItem(str(m.quality))
            ])
   