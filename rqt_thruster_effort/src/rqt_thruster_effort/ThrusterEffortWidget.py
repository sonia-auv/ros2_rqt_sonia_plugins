import os
import rclpy
import rospkg
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from std_msgs.msg import Int8MultiArray, UInt16MultiArray


class ThrusterEffortWidget(QWidget):

    monitor_thruster_newton_msg = pyqtSignal('PyQt_PyObject')
    monitor_thruster_pwm_msg = pyqtSignal('PyQt_PyObject')

    def __init__(self, internal_node):
        super(ThrusterEffortWidget, self).__init__()

        ui_file = os.path.join(get_package_share_directory('rqt_thruster_effort'), 'resource', 'mainwidget.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Thruster Effort')

        self._thruster_newton_subscriber = internal_node.create_subscription("/telemetry/thruster_newton", Int8MultiArray, self._handle_thruster_newton_msg)
        self._thruster_pwm_subscriber = internal_node.create_subscription("/provider_thruster/thruster_pwm", UInt16MultiArray, self._handle_thruster_pwm_msg)

        self.monitor_thruster_newton_msg.connect(self._received_thruster_newton_msg)
        self.monitor_thruster_pwm_msg.connect(self._received_thruster_pwm_msg)

    def _handle_thruster_newton_msg(self, msg):
        self.monitor_thruster_newton_msg.emit(msg)

    def _handle_thruster_pwm_msg(self, msg):
        self.monitor_thruster_pwm_msg.emit(msg)

    def _received_thruster_newton_msg(self, msg):
        for i in range(0, len(msg.data)):
            self._set_thruster_value(i + 1, msg.data[i])
    
    def _received_thruster_pwm_msg(self, msg):
        for i in range(0, len(msg.data)):
            self._set_pwm_value(i + 1, msg.data[i])

    def _set_thruster_value(self, thruster_id, value):
        eval('self.T' + str(thruster_id) + '_value').setText('{}'.format(int(value)) + ' N')
        eval('self.T' + str(thruster_id) + '_slider').setValue(int(value))
    
    def _set_pwm_value(self, thruster_id, value):
        eval('self.T' + str(thruster_id) + '_pwm').setText('PWM : {}'.format(int(value)))

    def shutdown_plugin(self):
        self._thruster_newton_subscriber.unregister()
        self._thruster_pwm_subscriber.unregister()
