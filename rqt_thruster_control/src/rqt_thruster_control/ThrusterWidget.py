import os
import time
from ament_index_python.packages import get_package_share_directory
from rclpy.publisher import Publisher
from .ThrusterAction import ThrusterAction
from threading import Thread

from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow

from sonia_common_ros2.msg import MotorPwm
from std_msgs.msg import Bool

class ThrusterWidget(QMainWindow):

    def __init__(self, internal_node):
        super(ThrusterWidget, self).__init__()
        # Give QObjects reasonable names
        self.setObjectName('ThrusterControlWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_thruster_control'), 'resource', 'Mainwindow.ui')
        loadUi(ui_file, self)

        # Subscribe to slot
        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.resetPwmButton.setEnabled(False)
        self.enableButton.clicked[bool].connect(self._handle_enableButton_clicked)
        self.disableButton.clicked[bool].connect(self._handle_disableButton_clicked)
        self.actionDry_motors.triggered.connect(self._handle_dry_motors_triggered)
        self.actionSpin_sequence.triggered.connect(self._handle_spin_sequence_triggered)
        self.resetPwmButton.clicked[bool].connect(self._handle_resetPwmButton_clicked)

        self.thruster_1 = ThrusterAction(self, 0, 'T1')
        self.thruster_2 = ThrusterAction(self, 1, 'T2')
        self.thruster_3 = ThrusterAction(self, 2, 'T3')
        self.thruster_4 = ThrusterAction(self, 3, 'T4')
        self.thruster_5 = ThrusterAction(self, 4, 'T5')
        self.thruster_6 = ThrusterAction(self, 5, 'T6')
        self.thruster_7 = ThrusterAction(self, 6, 'T7')
        self.thruster_8 = ThrusterAction(self, 7, 'T8')

        self.thruster_publisher: Publisher = internal_node.create_publisher(MotorPwm,"/provider_thruster/thruster_pwm", 10)
        self.dry_test_publisher: Publisher = internal_node.create_publisher(Bool,"/telemetry/dry_run",10)

        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.T1_T2.setEnabled(False)
        self.T3_T4.setEnabled(False)
        self.T5_T6.setEnabled(False)
        self.T7_T8.setEnabled(False)
        self.actionDry_motors.setEnabled(False)
        self.actionSpin_sequence.setEnabled(False)

        self.pwms=[1500,1500,1500,1500,1500,1500,1500,1500,1500]
        
        #create dry test threads
        self.spin_sequence_thread= Thread(target=self.spin_sequence, daemon=True)
        self.dry_motors_thread= Thread(target=self.dry_motors, daemon=True)

    def _dry_run_callback(self, msg):
        if msg.data:
            self.enableButton.setEnabled(False)
            self.disableButton.setEnabled(True)
            self.T1_T2.setEnabled(True)
            self.T3_T4.setEnabled(True)
            self.T5_T6.setEnabled(True)
            self.T7_T8.setEnabled(True)
            self.resetPwmButton.setEnabled(True)
            self.actionDry_motors.setEnabled(True)
            self.actionSpin_sequence.setEnabled(True)
        else:
            self.enableButton.setEnabled(True)
            self.disableButton.setEnabled(False)
            self.T1_T2.setEnabled(False)
            self.T3_T4.setEnabled(False)
            self.T5_T6.setEnabled(False)
            self.T7_T8.setEnabled(False)
            self.resetPwmButton.setEnabled(False)
            self.actionDry_motors.setEnabled(False)
            self.actionSpin_sequence.setEnabled(False)
    
    def _handle_resetPwmButton_clicked(self, checked):
        
        self.pwms=[1500,1500,1500,1500,1500,1500,1500,1500,1500]
        self.send_pwms()
        self.thruster_1.handle_thruster_effort1500_clicked(None)
        self.thruster_2.handle_thruster_effort1500_clicked(None)
        self.thruster_3.handle_thruster_effort1500_clicked(None)
        self.thruster_4.handle_thruster_effort1500_clicked(None)
        self.thruster_5.handle_thruster_effort1500_clicked(None)
        self.thruster_6.handle_thruster_effort1500_clicked(None)
        self.thruster_7.handle_thruster_effort1500_clicked(None)
        self.thruster_8.handle_thruster_effort1500_clicked(None)


    def _handle_enableButton_clicked(self, checked):
        self.enableButton.setEnabled(False)
        self.disableButton.setEnabled(True)
        self.T1_T2.setEnabled(True)
        self.T3_T4.setEnabled(True)
        self.T5_T6.setEnabled(True)
        self.T7_T8.setEnabled(True)
        self.resetPwmButton.setEnabled(True)
        self.actionDry_motors.setEnabled(True)
        self.actionSpin_sequence.setEnabled(True)
        state= Bool()
        state.data=True
        self.dry_test_publisher.publish(state)

    def _handle_disableButton_clicked(self, checked):
        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.T1_T2.setEnabled(False)
        self.T3_T4.setEnabled(False)
        self.T5_T6.setEnabled(False)
        self.T7_T8.setEnabled(False)
        self.resetPwmButton.setEnabled(False)
        self.actionDry_motors.setEnabled(False)
        self.actionSpin_sequence.setEnabled(False)
        state= Bool()
        state.data=False
        self.dry_test_publisher.publish(state)

    def set_pwm(self, index, value):
        self.pwms[index] = value

    def send_pwms(self):
        msg=MotorPwm()
        msg.motor1=self.pwms[0]
        msg.motor2=self.pwms[1]
        msg.motor3=self.pwms[2]
        msg.motor4=self.pwms[3]
        msg.motor5=self.pwms[4]
        msg.motor6=self.pwms[5]
        msg.motor7=self.pwms[6]
        msg.motor8=self.pwms[7]     

        self.thruster_publisher.publish(msg)
               
    def _handle_dry_motors_triggered(self):
        self.dry_motors_thread.start()
    def _handle_spin_sequence_triggered(self):
        self.spin_sequence_thread.start()
        
    def spin_sequence(self):
        i = 0
        while i < 8:
            self.set_pwm(i, 1550)
            self.send_pwms()
            time.sleep(3)
            self.set_pwm(i, 1500)
            self.send_pwms()
            time.sleep(1)
            i+=1
        self.spin_sequence_thread = Thread(target=self.spin_sequence, daemon=True)   
    def dry_motors(self):
        i = 0
        while i < 8:
            self.set_pwm(i, 1545)
            i+=1
        self.send_pwms()
        time.sleep(3)
        #reset
        i = 0
        while i < 8:
            self.set_pwm(i, 1500)
            i+=1
        self.send_pwms()
        time.sleep(1)
        self.dry_motors_thread = Thread(target=self.dry_motors, daemon=True)

    def shutdown_plugin(self):
        if self.spin_sequence_thread.is_alive():
            self.spin_sequence_thread.join()
        if self.dry_motors_thread.is_alive():
            self.dry_motors_thread.join()
        self.thruster_publisher.destroy()
        self.dry_test_publisher.destroy()