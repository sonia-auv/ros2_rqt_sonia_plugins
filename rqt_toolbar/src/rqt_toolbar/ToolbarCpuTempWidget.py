import os
import rclpy
import rospkg
from ament_index_python.packages import get_package_share_directory
from threading import Thread
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from sensor_msgs.msg import Temperature

class CpuTempWidget(QWidget):
    systemTemperatureReceived = pyqtSignal(Temperature)

    def __init__(self, type, ros_node):
        super(CpuTempWidget, self).__init__()
        self.setObjectName('CpuTempWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_toolbar'), 'resource', 'temp_sensor.ui')
        loadUi(ui_file, self)

        self.temp_label.setText('{}:'.format(type))

        ros_node.create_subscription(Temperature, "/provider_system/temperature", self.system_temperature_callback, 10)
        self.systemTemperatureReceived.connect(self.handle_result)
        self.temp_value.setText("{0} C".format("?"))


    def system_temperature_callback(self, data: Temperature):
        self.systemTemperatureReceived.emit(data)

    def handle_result(self, msg):
        self.temp_value.setText("{:.2f} C".format(msg.temperature))
