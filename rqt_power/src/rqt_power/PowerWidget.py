import os

from ament_index_python import get_package_share_directory
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from std_msgs.msg import Float64MultiArray, Bool, UInt8MultiArray
from sonia_common_ros2.msg import BatteryVoltage, MotorVoltages

class PowerWidget(QMainWindow):
    voltage_result_received = pyqtSignal(BatteryVoltage)
    voltage12V_result_received = pyqtSignal(MotorVoltages)
    current_result_received = pyqtSignal(Float64MultiArray)
    temperature_result_received = pyqtSignal(Float64MultiArray)
    motor_feedback_received = pyqtSignal(UInt8MultiArray)

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

        self._voltage_subscriber :Subscription= ros_node.create_subscription(BatteryVoltage,"/provider_power/voltage", self._voltage_callback, 10)
        self._voltage12V_subscriber:Subscription = ros_node.create_subscription(MotorVoltages,"/provider_power/voltage12V", self._voltage12V_callback, 10)
        self._current_subscriber: Subscription = ros_node.create_subscription(Float64MultiArray,"/provider_power/current", self._current_callback, 10)
        self._temperature_subscriber: Subscription =ros_node.create_subscription(Float64MultiArray,"/provider_power/temperature",  self._temperature_callback, 10)
        self.motor_feedback_subscriber: Subscription = ros_node.create_subscription( UInt8MultiArray,"/proc_fault/motor_feedback", self.motor_feedback_callback, 10)

        self.activate_all_motor: Publisher = ros_node.create_publisher(Bool, '/provider_power/activate_motors',100)

        self.voltage_result_received.connect(self.show_Voltage)
        self.current_result_received.connect(self.show_Current)
        self.voltage12V_result_received.connect(self.show_12V)
        self.temperature_result_received.connect(self.show_Temperature)
        self.motor_feedback_received.connect(self.show_motor_feedback)

        self.EnableAll.setEnabled(True)
        self.EnableAll.clicked.connect(self._handle_out_enable_all_clicked)

        self.DisableAll.setEnabled(False)
        self.DisableAll.clicked.connect(self._handle_out_disable_all_clicked)


    def _voltage_callback(self, data):
        self.voltage_result_received.emit(data)

    def _voltage12V_callback(self, data):
        self.voltage12V_result_received.emit(data)

    def _current_callback(self, data):
        self.current_result_received.emit(data)

    def _temperature_callback(self, data):
        self.temperature_result_received.emit(data)
    
    def motor_feedback_callback(self, data):
        self.motor_feedback_received.emit(data)

    def show_12V(self, msg):
        pass

    def show_Temperature(self, data):
        for i in range(len(data.data)-2):
            format_data = '{:.2f}'.format(data.data[i])
            eval('self.TempM' + str(i+1)).display(format_data)
            eval('self.TempM' + str(i+1) + '_2').display(format_data)

        format_data = '{:.2f}'.format(data.data[len(data.data)-2])
        self.TempB1.display(format_data)
        self.TempB1_2.display(format_data)
        format_data = '{:.2f}'.format(data.data[len(data.data)-1])
        self.TempB2.display(format_data)
        self.TempB2_2.display(format_data)

    def show_Current(self, data):

        for i in range(len(data.data)-4):
            format_data = '{:.2f}'.format(data.data[i])
            eval('self.CurrentM' + str(i+1)).display(format_data)
            eval('self.CurrentM' + str(i+1) + '_2').display(format_data)

        format_data = '{:.2f}'.format(data.data[len(data.data)-2])
        self.CurrentB1.display(format_data)
        self.CurrentB1_2.display(format_data)
        format_data = '{:.2f}'.format(data.data[len(data.data)-1])
        self.CurrentB2.display(format_data)
        self.CurrentB2_2.display(format_data)

    def show_Voltage(self, msg):
        data =[msg.battery1, msg.battery2]
        for i in range(len(data)-2):
            format_data = '{:.2f}'.format(data[i])
            eval('self.VoltageM' + str(i+1)).display(format_data)
            eval('self.VoltageM' + str(i+1) + '_2').display(format_data)

        format_data = '{:.2f}'.format(data[0])
        self.VoltageB1.display(format_data)
        self.VoltageB1_2.display(format_data)
        format_data = '{:.2f}'.format(data[1])
        self.VoltageB2.display(format_data)
        self.VoltageB2_2.display(format_data)

    @pyqtSlot(UInt8MultiArray)
    def show_motor_feedback(self, data):
        dict_colors = {0:"grey", 1:"green", 2:"yellow", 3:"red", 4:"blue"}
        for i in range(len(data.data)):
            color = dict_colors[data.data[i]]
            for j in range(1,5):
                eval(f"self.M{i+1}_{j}").setStyleSheet(f"background-color: {color}")

    def _handle_out_enable_all_clicked(self):
        #self._set_all_bus_state(1)
        self.DisableAll.setEnabled(True)
        self.EnableAll.setEnabled(False)
        state=Bool()
        state.data=True
        self.activate_all_motor.publish(state)

    def _handle_out_disable_all_clicked(self):
        #self._set_all_bus_state(0)
        self.DisableAll.setEnabled(False)
        self.EnableAll.setEnabled(True)
        state=Bool()
        state.data=False
        self.activate_all_motor.publish(state)

    # def _set_all_bus_state(self, state):
    #     activation = activateAllPS()
    #     activation.data = bool(state)
    #     for i in range(0, 4):
    #         activation.slave = i
    #         for j in range(1, 3):
    #             activation.bus = j
    #             self.activate_all_ps.publish(activation)

    def _handle_start_test_triggered(self):
        pass

    def _execute_test(self):
        pass

    def shutdown_plugin(self):
        self._voltage_subscriber.destroy()
        self._current_subscriber.destroy()
        self._voltage12V_subscriber.destroy()
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass


