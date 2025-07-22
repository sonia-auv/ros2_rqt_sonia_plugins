import os

from ament_index_python import get_package_share_directory
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from std_msgs.msg import Bool
from sonia_common_ros2.msg import BatteryPowerMessages, MotorPowerMessages, MotorFeedback

class PowerWidget(QMainWindow):
    battery_voltage_result_received = pyqtSignal(BatteryPowerMessages)
    motor_voltage_result_received = pyqtSignal(MotorPowerMessages)
    voltage12V_result_received = pyqtSignal(MotorPowerMessages)
    battery_current_result_received = pyqtSignal(BatteryPowerMessages)
    motor_current_result_received = pyqtSignal(MotorPowerMessages)
    battery_temperature_result_received = pyqtSignal(BatteryPowerMessages)
    motor_temperature_result_received = pyqtSignal(MotorPowerMessages)
    motor_feedback_received = pyqtSignal(MotorFeedback)

    CMD_PS_V16_1 = 0
    CMD_PS_V16_2 = 1
    CMD_PS_V12 = 2
    CMD_PS_C16_1 = 3
    CMD_PS_C16_2 = 4
    CMD_PS_C12 = 5
    CMD_PS_temperature = 6
    CMD_PS_VBatt = 7

    check_ps_16v_2 = 21
    check_ps_16v_1 = 20
    check_ps_12v = 19

    def __init__(self, ros_node):
        super(PowerWidget, self).__init__()
        # Give QObjects reasonable names
        self.setObjectName('PowerControlWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_power'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)

        self.setObjectName('MyPowerControlWidget')

        self._battery_voltage_subscriber :Subscription= ros_node.create_subscription(BatteryPowerMessages,"/provider_power/battery_voltages", self._battery_voltage_callback, 10)
        self._motor_voltage_subscriber :Subscription= ros_node.create_subscription(MotorPowerMessages,"/provider_power/motor_voltages", self._motor_voltage_callback, 10)
        self._voltage12V_subscriber:Subscription = ros_node.create_subscription(MotorPowerMessages,"/provider_power/voltage12V", self._voltage12V_callback, 10)
        
        self._battery_current_subscriber: Subscription = ros_node.create_subscription(BatteryPowerMessages,"/provider_power/battery_currents", self._battery_current_callback, 10)
        self._motor_current_subscriber: Subscription = ros_node.create_subscription(MotorPowerMessages,"/provider_power/motor_currents", self._motor_current_callback, 10)
        self._battery_temperature_subscriber: Subscription =ros_node.create_subscription(BatteryPowerMessages,"/provider_power/battery_temperatures",  self._battery_temperature_callback, 10)
        self._motor_temperature_subscriber: Subscription =ros_node.create_subscription(MotorPowerMessages,"/provider_power/motor_temperatures",  self._motor_temperature_callback, 10)
        self._motor_feedback_subscriber: Subscription = ros_node.create_subscription(MotorFeedback,"/provider_power/motor_feedback", self.motor_feedback_callback, 10)

        self.activate_all_motor: Publisher = ros_node.create_publisher(Bool, '/provider_power/activate_motors',100)

        self.battery_voltage_result_received.connect(self.show_battery_Voltage)
        self.motor_voltage_result_received.connect(self.show_motor_Voltage)
        self.battery_current_result_received.connect(self.show_battery_Current)
        self.motor_current_result_received.connect(self.show_motor_Current)
        self.voltage12V_result_received.connect(self.show_12V)
        self.battery_temperature_result_received.connect(self.show_battery_Temperature)
        self.motor_temperature_result_received.connect(self.show_motor_Temperature)
        self.motor_feedback_received.connect(self.show_motor_feedback)

        self.EnableAll.setEnabled(True)
        self.EnableAll.clicked.connect(self._handle_out_enable_all_clicked)

        self.DisableAll.setEnabled(False)
        self.DisableAll.clicked.connect(self._handle_out_disable_all_clicked)


    def _battery_voltage_callback(self, data):
        self.battery_voltage_result_received.emit(data)
    
    def _motor_voltage_callback(self, data):
        self.motor_voltage_result_received.emit(data)

    def _voltage12V_callback(self, data):
        self.voltage12V_result_received.emit(data)

    def _battery_current_callback(self, data):
        self.battery_current_result_received.emit(data)
        
    def _motor_current_callback(self, data):
        self.motor_current_result_received.emit(data)

    def _battery_temperature_callback(self, data):
        self.battery_temperature_result_received.emit(data)
        
    def _motor_temperature_callback(self, data):
        self.motor_temperature_result_received.emit(data)
    
    def motor_feedback_callback(self, data):
        self.motor_feedback_received.emit(data)

    def show_12V(self, msg):
        pass

    def show_battery_Temperature(self, msg: BatteryPowerMessages):
        format_data = '{:.2f}'.format(msg.battery1)
        self.TempB1.display(format_data)
        self.TempB1_2.display(format_data)
        format_data = '{:.2f}'.format(msg.battery2)
        self.TempB2.display(format_data)
        self.TempB2_2.display(format_data)

    def show_motor_Temperature(self, msg: MotorPowerMessages):
        data =[msg.motor1, msg.motor2, msg.motor3, msg.motor4, msg.motor5, msg.motor6, msg.motor7, msg.motor8]
        for i in range(len(data)):
            format_data = '{:.2f}'.format(data[i])
            eval('self.TempM' + str(i+1)).display(format_data)
            eval('self.TempM' + str(i+1) + '_2').display(format_data)
            
    def show_battery_Current(self, msg: BatteryPowerMessages):
        format_data = '{:.2f}'.format(msg.battery1)
        self.CurrentB1.display(format_data)
        self.CurrentB1_2.display(format_data)
        format_data = '{:.2f}'.format(msg.battery2)
        self.CurrentB2.display(format_data)
        self.CurrentB2_2.display(format_data)
        
    def show_motor_Current(self, msg: MotorPowerMessages):
        data =[msg.motor1, msg.motor2, msg.motor3, msg.motor4, msg.motor5, msg.motor6, msg.motor7, msg.motor8]
        for i in range(len(data)):
            format_data = '{:.2f}'.format(data[i])
            eval('self.CurrentM' + str(i+1)).display(format_data)
            eval('self.CurrentM' + str(i+1) + '_2').display(format_data)
            
    def show_battery_Voltage(self, msg: BatteryPowerMessages):
        format_data = '{:.2f}'.format(msg.battery1)
        self.VoltageB1.display(format_data)
        self.VoltageB1_2.display(format_data)
        format_data = '{:.2f}'.format(msg.battery2)
        self.VoltageB2.display(format_data)
        self.VoltageB2_2.display(format_data)
        
    def show_motor_Voltage(self, msg: MotorPowerMessages):
        data =[msg.motor1, msg.motor2, msg.motor3, msg.motor4, msg.motor5, msg.motor6, msg.motor7, msg.motor8]
        for i in range(len(data)):
            format_data = '{:.2f}'.format(data[i])
            eval('self.VoltageM' + str(i+1)).display(format_data)
            eval('self.VoltageM' + str(i+1) + '_2').display(format_data)

    @pyqtSlot(MotorFeedback)
    def show_motor_feedback(self, msg: MotorFeedback):
        data =[msg.motor1, msg.motor2, msg.motor3, msg.motor4, msg.motor5, msg.motor6, msg.motor7, msg.motor8]
        dict_colors = {0:"grey", 1:"green", 2:"yellow", 3:"red", 4:"blue"}
        for i in range(len(data)):
            color = dict_colors[data[i]]
            for j in range(1,5):
                eval(f"self.M{i+1}_{j}").setStyleSheet(f"background-color: {color}")

    def _handle_out_enable_all_clicked(self):
        self.DisableAll.setEnabled(True)
        self.EnableAll.setEnabled(False)
        state=Bool()
        state.data=True
        self.activate_all_motor.publish(state)

    def _handle_out_disable_all_clicked(self):
        self.DisableAll.setEnabled(False)
        self.EnableAll.setEnabled(True)
        state=Bool()
        state.data=False
        self.activate_all_motor.publish(state)

    #def _handle_start_test_triggered(self):
    #    pass

    #def _execute_test(self):
    #    pass

    def shutdown_plugin(self):
        self._battery_voltage_subscriber.destroy()
        self._motor_voltage_subscriber.destroy()
        self._battery_current_subscriber.destroy()
        self._motor_current_subscriber.destroy()
        self._battery_temperature_subscriber.destroy()
        self._motor_temperature_subscriber.destroy()
        self._voltage12V_subscriber.destroy()
        self._motor_feedback_subscriber.destroy()
