import os
import rclpy
from ament_index_python.packages import get_package_share_directory

from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal

from sonia_common_ros2.msg import BatteryVoltage

class BatteryWidget(QWidget):

    BATT_MAX = 28
    BATT_THRESHOLD = 25.6
    psu_received = pyqtSignal(BatteryVoltage)
    cmd_ps_vbatt = 7

    def __init__(self, store_index, internal_node):
        super(BatteryWidget, self).__init__()
        # Give QObjects reasonable names
        self.setObjectName('BatteryWidget')
        self.store_index = store_index
        self.bat_max = 16.8
        self.bat_min = 14.5
        self.bat_warning = 14.8

        ui_file = os.path.join(get_package_share_directory('rqt_toolbar'), 'resource', 'battery.ui')
        loadUi(ui_file, self)
        # TODO: ROS CHANGE
        self._power_supply = internal_node.create_subscription(BatteryVoltage, '/provider_power/battery_voltages', self._power_supply_callback, 10)
        self.psu_received.connect(self._handle_result)
        
        if self.store_index == 8:
            self.battery_label.setText('Bat. 1 :')
        elif self.store_index == 9:
            self.battery_label.setText('Bat. 2 :')       

    def _power_supply_callback(self, data):
        self.psu_received.emit(data)

    def _handle_result(self, msg: BatteryVoltage):
        self.battery_value.setText('{:.2f} V'.format(msg.battery1 if self.store_index == 8 else msg.battery2))
        percentage = ((msg.data[self.store_index] - self.bat_min) / (self.bat_max - self.bat_min)) * 100
        self.progressBar.setValue(percentage)

        if percentage >= 80:
            self.progressBar.setStyleSheet('selection-background-color:green ; background-color:gray ; color:black')
        elif 80 > percentage >= 50:
            self.progressBar.setStyleSheet('selection-background-color:yellow ; background-color:gray ; color:black')
        elif 50 > percentage >= 20:
            self.progressBar.setStyleSheet('selection-background-color:orange ; background-color:gray ; color:black')
        else:
            self.progressBar.setStyleSheet('selection-background-color:red ; background-color:gray ; color:black')

        if msg.data[self.store_index] <= self.bat_warning:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("ATTENTION")
            msg.setStandardButtons(QMessageBox.Close)
            if self.store_index == 8:
                msg.setText('Battery 1 has a very low voltage')
            elif self.store_index == 9:
                msg.setText('Battery 2 has a very low voltage')
            msg.exec_()