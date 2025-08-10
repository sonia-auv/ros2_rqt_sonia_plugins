import os
from ament_index_python import get_package_share_directory
from rclpy.subscription import Subscription
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from sonia_common_ros2.msg import MotorPwm
from std_msgs.msg import Int8MultiArray


class ThrusterEffortWidget(QWidget):

    monitor_thruster_newton_msg = pyqtSignal('PyQt_PyObject')
    monitor_thruster_pwm_msg = pyqtSignal(MotorPwm)

    def __init__(self, internal_node):
        super(ThrusterEffortWidget, self).__init__()

        ui_file = os.path.join(get_package_share_directory('rqt_thruster_effort'), 'resource', 'mainwidget.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Thruster Effort')

        qos_rel = QoSProfile(depth=10)
        qos_rel.reliability= ReliabilityPolicy.RELIABLE
        
        self._thruster_newton_subscriber: Subscription = internal_node.create_subscription(Int8MultiArray, "/telemetry/thruster_newton" , self._handle_thruster_newton_msg,10)
        self._thruster_pwm_subscriber: Subscription = internal_node.create_subscription(MotorPwm, "/provider_thruster/thruster_pwm", self._handle_thruster_pwm_msg, qos_rel)

        self.monitor_thruster_newton_msg.connect(self._received_thruster_newton_msg)
        self.monitor_thruster_pwm_msg.connect(self._received_thruster_pwm_msg)

    def _handle_thruster_newton_msg(self, msg:MotorPwm):
        self.monitor_thruster_newton_msg.emit(msg)

    def _handle_thruster_pwm_msg(self, msg):
        self.monitor_thruster_pwm_msg.emit(msg)

    def _received_thruster_newton_msg(self, msg):
        print(msg)
        for i in range(0, len(msg.data)):
            self._set_thruster_value(i + 1, msg.data[i])
    
    def _received_thruster_pwm_msg(self, msg:MotorPwm):   
        self._set_pwm_value(1, msg.motor1)
        self._set_pwm_value(2, msg.motor2)
        self._set_pwm_value(3, msg.motor3)
        self._set_pwm_value(4, msg.motor4)
        self._set_pwm_value(5, msg.motor5)
        self._set_pwm_value(6, msg.motor6)
        self._set_pwm_value(7, msg.motor7)
        self._set_pwm_value(8, msg.motor8)

    def _set_thruster_value(self, thruster_id, value):
        eval('self.T' + str(thruster_id) + '_value').setText('{}'.format(int(value)) + ' N')
        eval('self.T' + str(thruster_id) + '_slider').setValue(int(value))
    
    def _set_pwm_value(self, thruster_id, value):
        eval('self.T' + str(thruster_id) + '_pwm').setText('PWM : {}'.format(int(value)))

    def shutdown_plugin(self):
        self._thruster_newton_subscriber.destroy()
        self._thruster_pwm_subscriber.destroy()
    