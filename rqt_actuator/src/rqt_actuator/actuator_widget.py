import os
from time import sleep
import rclpy
from rclpy.client import Client
import threading
from ament_index_python import get_package_share_directory
from sonia_common_ros2.srv import ActuatorService
from sonia_common_ros2.srv import Pince
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from functools import partial


# main class inherits from the ui window class
class ActuatorWidget(QWidget):
    def __init__(self, internal_node):
        super(ActuatorWidget, self).__init__()
        
        ui_file = os.path.join(get_package_share_directory('rqt_actuator'), 'resource', 'mainWidget.ui')
        loadUi(ui_file, self)

        self.actuatorClient: Client = internal_node.create_client(ActuatorService, "/provider_actuator/do_action")
        self.req= ActuatorService.Request()
        self.req_arm= ActuatorService.Request()
        # self.armClient: Client = internal_node.create_client(Pince, "/provider_arm/grabber")
        # self.req_arm= Pince.Request()
        self.drop_port.clicked.connect(self._handle_drop_port)
        self.drop_starboard.clicked.connect(self._handle_drop_starboard)
        self.torpedo_port.clicked.connect(self._handle_torpedo_port)
        self.torpedo_starboard.clicked.connect(self._handle_torpedo_starboard)
        self.open_arm.clicked.connect(self._handle_open_robotic_arm)
        self.close_arm.clicked.connect(self._handle_close_robotic_arm)
        self.stop_arm.clicked.connect(self._handle_stop_robotic_arm)

    def _handle_drop_port(self):
        if self.drop_port.styleSheet() == "background-color: yellow":
            return
        self.drop_port.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_DROPPER, ActuatorService.Request.SIDE_PORT, ActuatorService.Request.ACTION_LAUNCH)

    def _handle_drop_starboard(self):
        if self.drop_starboard.styleSheet() == "background-color: yellow":
            return
        self.drop_starboard.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_DROPPER, ActuatorService.Request.SIDE_STARBOARD, ActuatorService.Request.ACTION_LAUNCH)

    def _handle_torpedo_port(self):
        if self.torpedo_port.styleSheet() == "background-color: yellow":
            return
        self.torpedo_port.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_TORPEDO, ActuatorService.Request.SIDE_PORT, ActuatorService.Request.ACTION_LAUNCH)

    def _handle_torpedo_starboard(self):
        if self.torpedo_starboard.styleSheet() == "background-color: yellow":
            return
        self.torpedo_starboard.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_TORPEDO, ActuatorService.Request.SIDE_STARBOARD, ActuatorService.Request.ACTION_LAUNCH)

    def _handle_open_robotic_arm(self):
        if self.open_arm.styleSheet() == "background-color: yellow":
            return
        self.open_arm.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_GRABBER, ActuatorService.Request.SIDE_PORT, ActuatorService.Request.ACTION_OPEN)



    def _handle_close_robotic_arm(self):
        if self.close_arm.styleSheet() == "background-color: yellow":
            return
        self.close_arm.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_GRABBER, ActuatorService.Request.SIDE_PORT, ActuatorService.Request.ACTION_CLOSE)

    def _handle_stop_robotic_arm(self):
        if self.stop_arm.styleSheet() == "background-color: yellow":
            return
        self.stop_arm.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorService.Request.ELEMENT_GRABBER, ActuatorService.Request.SIDE_PORT, ActuatorService.Request.ACTION_STOP)
        
    # def sendArmMessage(self, element, action):
    #     self.req.action=action
    #     self.req.element=element
    #     self.future = self.actuatorClient.call_async(self.req)
    #     self.future.add_done_callback(partial(self.actuatorCallback, element=self.req_arm.element,action=self.req_arm.action,))

    def sendMessage(self, element, side, action):
        self.req.action=action
        self.req.side=side
        self.req.element=element
        self.future = self.actuatorClient.call_async(self.req)
        self.future.add_done_callback(partial(self.actuatorCallback, element=element,side=side,action=action))
        
    #    self.actuatorCallback(element,side,self.future.result())
    
    def actuatorCallback(self, future, element, side,action):
        button = ""
        response=future.result().success
        #if data.element == ActuatorSendReply.ELEMENT_ARM:
            #if data.side == ActuatorSendReply.ARM_CLOSE:
                #button = self.close_arm
            #elif data.side == ActuatorSendReply.ARM_OPEN:
                #button = self.open_arm
        if element == ActuatorService.Request.ELEMENT_DROPPER:
            if side == ActuatorService.Request.SIDE_PORT:
                button = self.drop_port
            elif side == ActuatorService.Request.SIDE_STARBOARD:
                button = self.drop_starboard
        elif element == ActuatorService.Request.ELEMENT_TORPEDO:
            if side == ActuatorService.Request.SIDE_PORT:
                button = self.torpedo_port
            elif side == ActuatorService.Request.SIDE_STARBOARD:
                button = self.torpedo_starboard

        elif element == ActuatorService.Request.ELEMENT_GRABBER:
            if action == ActuatorService.Request.ACTION_OPEN:
                button = self.open_arm
            elif action == ActuatorService.Request.ACTION_CLOSE:
                button = self.close_arm
            else :
                button = self.stop_arm
        if button == "":
            rclpy.logerr(f"{element} has an invalid side or element")
        else:
            if response == True:
                button.setStyleSheet("background-color: green")
                newThread = Threads(button)
                newThread.start()
            
            elif response == None:
                button.setStyleSheet("background: rgb(0, 0, 255)")
                newThread = Threads(button)
                newThread.start()
            else:
                button.setStyleSheet("background-color: red")
                newThread = Threads(button)
                newThread.start()

    def shutdown_plugin(self):
        self.actuatorClient.destroy()
        # self.armClient.destroy()

class Threads(threading.Thread):
    def __init__(self, button):
        super(Threads, self).__init__()
        self.button = button
    
    def run(self):
        for i in range(0,5):
            if self.button.styleSheet() == "background-color: yellow":
                return
            else:
                sleep(1)
        self.button.setStyleSheet("")
        
