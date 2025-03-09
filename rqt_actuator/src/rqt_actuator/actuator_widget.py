import os
from time import sleep
#import rospkg
import rclpy
import threading
from ament_index_python import get_package_share_directory
from sonia_common_ros2.msg import ActuatorDoAction, ActuatorSendReply
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget


# main class inherits from the ui window class
class ActuatorWidget(QWidget):
    def __init__(self, internal_node):
        super(ActuatorWidget, self).__init__()
        #rp = rospkg.RosPack()

        ui_file = os.path.join(get_package_share_directory('rqt_actuator'), 'resource', 'mainWidget.ui')
        loadUi(ui_file, self)

        self.actuatorSubscriber = internal_node.create_subscription("/provider_actuators/do_action_from_actuators", ActuatorSendReply, self.actuatorCallback)
        self.actuatorPublisher = internal_node.create_publisher(ActuatorDoAction,"/provider_actuators/do_action_to_actuators", queue_size=100)
        self.drop_port.clicked.connect(self._handle_drop_port)
        self.drop_starboard.clicked.connect(self._handle_drop_starboard)
        self.torpedo_port.clicked.connect(self._handle_torpedo_port)
        self.torpedo_starboard.clicked.connect(self._handle_torpedo_starboard)
        self.open_arm.clicked.connect(self._handle_open_robotic_arm)
        self.close_arm.clicked.connect(self._handle_close_robotic_arm)

    def _handle_drop_port(self):
        if self.drop_port.styleSheet() == "background-color: yellow":
            return
        self.drop_port.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorDoAction.ELEMENT_DROPPER,ActuatorDoAction.SIDE_PORT,ActuatorDoAction.ACTION_DROPPER_LAUNCH)

    def _handle_drop_starboard(self):
        if self.drop_starboard.styleSheet() == "background-color: yellow":
            return
        self.drop_starboard.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorDoAction.ELEMENT_DROPPER,ActuatorDoAction.SIDE_STARBOARD,ActuatorDoAction.ACTION_DROPPER_LAUNCH)

    def _handle_torpedo_port(self):
        if self.torpedo_port.styleSheet() == "background-color: yellow":
            return
        self.torpedo_port.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorDoAction.ELEMENT_TORPEDO,ActuatorDoAction.SIDE_PORT,ActuatorDoAction.ACTION_TORPEDO_LAUNCH)

    def _handle_torpedo_starboard(self):
        if self.torpedo_starboard.styleSheet() == "background-color: yellow":
            return
        self.torpedo_starboard.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorDoAction.ELEMENT_TORPEDO,ActuatorDoAction.SIDE_STARBOARD,ActuatorDoAction.ACTION_TORPEDO_LAUNCH)

    def _handle_open_robotic_arm(self):
        if self.open_arm.styleSheet() == "background-color: yellow":
            return
        self.open_arm.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorDoAction.ELEMENT_ARM,ActuatorDoAction.ARM_OPEN,ActuatorDoAction.ACTION_ARM_EXEC)

    def _handle_close_robotic_arm(self):
        if self.close_arm.styleSheet() == "background-color: yellow":
            return
        self.close_arm.setStyleSheet("background-color: yellow")
        self.sendMessage(ActuatorDoAction.ELEMENT_ARM,ActuatorDoAction.ARM_CLOSE,ActuatorDoAction.ACTION_ARM_EXEC)

    def sendMessage(self, element, side, action):
        message = ActuatorDoAction()
        message.element = element
        message.side = side
        message.action = action
        self.actuatorPublisher.publish(message)

    def actuatorCallback(self, data):
        button = ""
        if data.element == ActuatorSendReply.ELEMENT_ARM:
            if data.side == ActuatorSendReply.ARM_CLOSE:
                button = self.close_arm
            elif data.side == ActuatorSendReply.ARM_OPEN:
                button = self.open_arm
        elif data.element == ActuatorSendReply.ELEMENT_DROPPER:
            if data.side == ActuatorSendReply.SIDE_PORT:
                button = self.drop_port
            elif data.side == ActuatorSendReply.SIDE_STARBOARD:
                button = self.drop_starboard
        elif data.element == ActuatorSendReply.ELEMENT_TORPEDO:
            if data.side == ActuatorSendReply.SIDE_PORT:
                button = self.torpedo_port
            elif data.side == ActuatorSendReply.SIDE_STARBOARD:
                button = self.torpedo_starboard
        if button == "":
            rclpy.logerr(f"{data} has an invalid side or element")
        else:
            if data.response == ActuatorSendReply.RESPONSE_SUCCESS:
                button.setStyleSheet("background-color: green")
                newThread = Threads(button)
                newThread.start()
            elif data.response == ActuatorSendReply.RESPONSE_TIMED_OUT:
                button.setStyleSheet("background-color: red")
                newThread = Threads(button)
                newThread.start()
            elif data.response == ActuatorSendReply.RESPONSE_FAILURE:
                button.setStyleSheet("background: rgb(88, 8, 24)")
                newThread = Threads(button)
                newThread.start()

    def restore_settings(self, plugin_settings, instance_settings):
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def shutdown_plugin(self):
        self.actuatorSubscriber.unregister()


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
        
