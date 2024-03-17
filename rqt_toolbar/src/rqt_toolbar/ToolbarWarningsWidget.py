import os
import rclpy
import rospkg
import threading

from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from std_msgs.msg import UInt8MultiArray
# from sonia_common.msg import FaultWarning


class WarningsWidget(QWidget):

    def __init__(self):
        super(WarningsWidget, self).__init__()
        self.setObjectName('WarningsWidget')
        ui_file = os.path.join(rospkg.RosPack().get_path('rqt_toolbar'), 'resource', 'warnings.ui')
        loadUi(ui_file, self)
        self.__internal_node = rclpy.create_node("warning_widget")
        # TODO: ROS CHANGE
        self.motor_feedback_subscriber = self.__internal_node.create_subscription(UInt8MultiArray,"/proc_fault/motor_feedback", self.motor_feedback_callback, 10)
        # self.other_feedback_subscriber = rospy.Subscriber("/proc_fault/control_checker_fault_warning", FaultWarning, self.other_feedback_callback)
        self.motorIndicator.setEnabled(True)
        self.motorIndicator.clicked.connect(self.openMotorMenu)
        self.dvlIndicator.setEnabled(True)
        self.dvlIndicator.clicked.connect(self.openDvlMenu)
        self.imuIndicator.setEnabled(True)
        self.imuIndicator.clicked.connect(self.openImuMenu)

    def openMotorMenu(self):
        def command():
            os.system("rqt --standalone rqt_power")
        
        # for t in threading.enumerate():
        #     if t.name=="Motor Windows":
        #         return
        # newThread = threading.Thread(target=command, name="Motor Windows")
        # newThread.start()

    def openDvlMenu(self):
        def command():
            os.system("rqt --standalone rqt_dvl")
        
        # for t in threading.enumerate():
        #     if t.name=="DVL Windows":
        #         return
        # newThread = threading.Thread(target=command, name="DVL Windows")
        # newThread.start()
    
    def openImuMenu(self):
        pass #TODO: change it once an IMU widget has been created
        # def command():
        #     os.system("rqt --standalone rqt_power")
        
        # for t in threading.enumerate():
        #     if t.name=="IMU Windows":
        #         return
        # newThread = threading.Thread(target=command, name="IMU Windows")
        # newThread.start()

    def motor_feedback_callback(self, data):
        dict_colors = {0:"grey", 1:"green", 2:"yellow", 3:"red", 4:"blue"}
        dict_motors = {"red":[], "blue":[], "yellow":[], "grey":[], "green":[]}
        tooltip = ""
        if 3 in data.data:
            self.motorIndicator.setStyleSheet("background-color: red")
        elif 4 in data.data:
            self.motorIndicator.setStyleSheet("background-color: blue")
        elif 2 in data.data:
            self.motorIndicator.setStyleSheet("background-color: yellow")
        elif 0 in data.data:
            self.motorIndicator.setStyleSheet("background-color: grey")
        else:
            self.motorIndicator.setStyleSheet("background-color: green")
        for i in range(len(data.data)):
            dict_motors[dict_colors[data.data[i]]].append(i+1)
        if len(dict_motors["green"]) == 8:
            tooltip = "All motors OK"
        elif len(dict_motors["grey"]) == 8:
            tooltip = "All motors OFF"
        else:
            if len(dict_motors["red"]) != 0:
                if len(dict_motors["red"]) == 1:
                    tooltip += f"Motor {dict_motors['red'][0]} is critical"
                else:
                    tooltip += f"Motors {', '.join(str(x) for x in dict_motors['red'])} are critical"
            if len(dict_motors["blue"]) != 0:
                if tooltip != "":
                    tooltip += "; "
                if len(dict_motors["blue"]) == 1:
                    tooltip += f"Motor {dict_motors['blue'][0]} is restarting"
                else:
                    tooltip += f"Motors {', '.join(str(x) for x in dict_motors['blue'])} are restarting"
            if len(dict_motors["yellow"]) != 0:
                if tooltip != "":
                    tooltip += "; "
                if len(dict_motors["yellow"]) == 1:
                    tooltip += f"Motor {dict_motors['yellow'][0]} is over-current"
                else:
                    tooltip += f"Motors {', '.join(str(x) for x in dict_motors['yellow'])} are over-current"
            if len(dict_motors["grey"]) != 0:
                if tooltip != "":
                    tooltip += "; "
                if len(dict_motors["grey"]) == 1:
                    tooltip += f"Motor {dict_motors['grey'][0]} is off"
                else:
                    tooltip += f"Motors {', '.join(str(x) for x in dict_motors['grey'])} are off"
        if tooltip != self.motorIndicator.toolTip():
            self.motorIndicator.setToolTip(tooltip)
    
    def other_feedback_callback(self, data):
        if data.Module == "DVL":
            self.dvlIndicator.setToolTip(data.Msg)
            if data.Severity == 4:
                self.dvlIndicator.setStyleSheet("background-color: green")
            elif data.Severity == 0:
                self.dvlIndicator.setStyleSheet("background: rgb(214, 232, 101)")
            elif data.Severity == 1:    
                self.dvlIndicator.setStyleSheet("background-color: yellow")
            elif data.Severity == 2:
                self.dvlIndicator.setStyleSheet("background-color: red")
            elif data.Severity == 3:
                self.dvlIndicator.setStyleSheet("""QPushButton{background: rgb(88, 8, 24);}
                                                   QToolTip{background: rgb(88, 8, 24);
                                                            color: white;}""")
        elif data.Module == "IMU":
            self.imuIndicator.setToolTip(data.Msg)
            if data.Severity == 4:
                self.imuIndicator.setStyleSheet("background-color: green")
            elif data.Severity == 0:
                self.imuIndicator.setStyleSheet("background: rgb(214, 232, 101)")
            elif data.Severity == 1:
                self.imuIndicator.setStyleSheet("background-color: yellow")
            elif data.Severity == 2:
                self.imuIndicator.setStyleSheet("background-color: red")
            elif data.Severity == 3:
                self.imuIndicator.setStyleSheet("""QPushButton{background: rgb(88, 8, 24);}
                                                   QToolTip{background: rgb(88, 8, 24);
                                                            color: white;}""")

    def shutdown_plugin(self):
        self.motor_feedback_subscriber.unregister()
        self.other_feedback_subscriber.unregister()