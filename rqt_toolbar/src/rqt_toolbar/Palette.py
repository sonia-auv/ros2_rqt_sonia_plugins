import os
from ament_index_python.packages import get_package_share_directory


from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget


class Palette(QWidget):

    # This is used in toolbar to set the main window palette
    def __init__(self):
        super(Palette, self).__init__()
        ui_file = os.path.join(get_package_share_directory("rqt_toolbar"), "resource", "palette.ui")
        loadUi(ui_file, self)
 