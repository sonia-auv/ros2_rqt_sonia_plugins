import os

from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QHeaderView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

class RecordWidget(QMainWindow):


    def __init__(self):
        super(RecordWidget, self).__init__()
        # Give QObjects reasonable names 
        self.setObjectName('RecordWidget')
               
        ui_file = os.path.join(get_package_share_directory('rqt_record'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)
                