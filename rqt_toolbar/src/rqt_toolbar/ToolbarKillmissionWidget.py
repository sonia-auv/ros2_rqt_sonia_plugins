import os
import rclpy
from sonia_common_ros2.msg import MissionStatus, KillStatus
from ament_index_python.packages import get_package_share_directory
from threading import Thread
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QAction, QMenu, QWidget, QActionGroup
from PyQt5.QtCore import pyqtSignal, Qt

from std_msgs.msg import Bool

class KillMissionWidget(QWidget):
    mission_received = pyqtSignal(MissionStatus)
    kill_received = pyqtSignal(KillStatus)

    def __init__(self, ros_node):
        super(KillMissionWidget, self).__init__()
        # Give QObjects reasonable names
        self.setObjectName('KillMissionWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_toolbar'), 'resource', 'KillMission.ui')
        loadUi(ui_file, self)

        self._mission_switch = ros_node.create_subscription(MissionStatus, '/provider_mission/status', self._mission_switch_callback, 10)
        self.mission_received.connect(self._handle_mission_result)

        self.kill_switch = ros_node.create_subscription(KillStatus, '/provider_kill/status', self._kill_switch_callback, 10)
        self.kill_received.connect(self._handle_kill_result)



    def _mission_switch_callback(self, data):
        self.mission_received.emit(data)

    def _kill_switch_callback(self, data):
        self.kill_received.emit(data)

    def _handle_mission_result(self, msg: MissionStatus):
        if msg.status:
            self.MissionSwitch_label.setPalette(self.paletteChecked.palette())
        else:
            self.MissionSwitch_label.setPalette(self.paletteUnchecked.palette())

    def _handle_kill_result(self, msg: KillStatus):
        if msg.status:
            self.KillSwitch_label.setPalette(self.paletteChecked.palette())
        else:
            self.KillSwitch_label.setPalette(self.paletteUnchecked.palette())

    def shutdown_plugin(self):
        self._mission_switch.unregister()
        self.kill_switch.unregister()