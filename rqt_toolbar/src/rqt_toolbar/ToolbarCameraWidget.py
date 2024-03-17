import os
from ament_index_python.packages import get_package_share_directory

from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class CameraWidget(QWidget):

    def __init__(self):
        super(CameraWidget, self).__init__()
        self.setObjectName('CameraWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_toolbar'), 'resource', 'start_cam.ui')
        loadUi(ui_file, self)

        self.btnBottom.clicked.connect(self.handle_bottom_click)
        self.btnFront.clicked.connect(self.handle_front_click)

        # TODO: We must to implement the ON/OFF cameras.
        self.btnBottom.setEnabled(False)
        self.btnFront.setEnabled(False)

    def handle_bottom_click(self):
        pass

    def handle_front_click(self):
        pass
