import os
import rclpy
from numpy import uint64

from ament_index_python.packages import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPalette

#from sonia_common_ros2.msg import BottomTracking
from geometry_msgs.msg import TwistStamped


class DvlWidget(QMainWindow, QWidget):

    dvl_received_status = pyqtSignal(int)
    dvl_received_twist = pyqtSignal(TwistStamped)

    def __init__(self, internal_node):
        super(DvlWidget, self).__init__()
        # Give QObjects reasonable names

        ui_file = os.path.join(get_package_share_directory('rqt_dvl'), 'resource', 'Mainwindow.ui')
        loadUi(ui_file, self)

        self.setObjectName('DvlControlWidget')

        #self._dvl_subscriber_status = internal_node.create_subscription('/provider_dvl/dvl_data', BottomTracking, self._dvl_subscriber_status_cb)
        self._dvl_subscriber_twist = internal_node.create_subscription(TwistStamped, '/provider_dvl/dvl_twist', self._dvl_subscriber_twist_cb,10)
        self.dvl_received_status.connect(self._handle_dvl_status)
        self.dvl_received_twist.connect(self._handle_dvl_twist)

        self.green = QPalette()
        self.red = QPalette()

        self.green.setColor(QPalette.WindowText, Qt.green)
        self.red.setColor(QPalette.WindowText, Qt.red)

        self.BeamVel1.setPalette(self.red)
        self.BeamVel2.setPalette(self.red)
        self.BeamVel3.setPalette(self.red)
        self.BeamVel4.setPalette(self.red)

        self.BeamDist1.setPalette(self.red)
        self.BeamDist2.setPalette(self.red)
        self.BeamDist3.setPalette(self.red)
        self.BeamDist4.setPalette(self.red)

        self.BeamFig1.setPalette(self.red)
        self.BeamFig2.setPalette(self.red)
        self.BeamFig3.setPalette(self.red)
        self.BeamFig4.setPalette(self.red)

        self.BeamVelx.setPalette(self.red)
        self.BeamVely.setPalette(self.red)
        self.BeamVelz.setPalette(self.red)

        self.BeamFigx.setPalette(self.red)
        self.BeamFigy.setPalette(self.red)
        self.BeamFigz.setPalette(self.red)

        self.Cap3.setPalette(self.red)
        self.Cap6.setPalette(self.red)
        self.Cap12.setPalette(self.red)

    def _dvl_subscriber_status_cb(self, data):
        self.dvl_received_status.emit(data.status)

    def _dvl_subscriber_twist_cb(self, data):
        self.dvl_received_twist.emit(data)

    def _handle_dvl_twist(self, data):
        self.Velx.setText('%.2f' % data.twist.linear.x)
        self.Vely.setText('%.2f' % data.twist.linear.y)
        self.Velz.setText('%.2f' % data.twist.linear.z)

    def _handle_dvl_status(self, status):
        self._handel_vel_beam(status)
        self._handel_dist_beam(status)
        self._handel_fig_beam(status)
        self._handel_vel_xyz(status)
        self._handel_fig_xyz(status)
        self._handel_capacity(status)

    def _handel_vel_beam(self, status):
        if status & (1 << 0):
            self.BeamVel1.setPalette(self.green)
        else:
            self.BeamVel1.setPalette(self.red)

        if status & (1 << 1):
            self.BeamVel2.setPalette(self.green)
        else:
            self.BeamVel2.setPalette(self.red)

        if status & (1 << 2):
            self.BeamVel3.setPalette(self.green)
        else:
            self.BeamVel3.setPalette(self.red)

        if status & (1 << 3):
            self.BeamVel4.setPalette(self.green)
        else:
            self.BeamVel4.setPalette(self.red)

    def _handel_dist_beam(self, status):
        if status & (1 << 4):
            self.BeamDist1.setPalette(self.green)
        else:
            self.BeamDist1.setPalette(self.red)

        if status & (1 << 5):
            self.BeamDist2.setPalette(self.green)
        else:
            self.BeamDist2.setPalette(self.red)

        if status & (1 << 6):
            self.BeamDist3.setPalette(self.green)
        else:
            self.BeamDist3.setPalette(self.red)

        if status & (1 << 7):
            self.BeamDist4.setPalette(self.green)
        else:
            self.BeamDist4.setPalette(self.red)

    def _handel_fig_beam(self, status):
        if status & (1 << 8):
            self.BeamFig1.setPalette(self.green)
        else:
            self.BeamFig1.setPalette(self.red)

        if status & (1 << 9):
            self.BeamFig2.setPalette(self.green)
        else:
            self.BeamFig2.setPalette(self.red)

        if status & (1 << 10):
            self.BeamFig3.setPalette(self.green)
        else:
            self.BeamFig3.setPalette(self.red)

        if status & (1 << 11):
            self.BeamFig4.setPalette(self.green)
        else:
            self.BeamFig4.setPalette(self.red)

    def _handel_vel_xyz(self, status):
        if status & (1 << 12):
            self.BeamVelx.setPalette(self.green)
        else:
            self.BeamVelx.setPalette(self.red)

        if status & (1 << 13):
            self.BeamVely.setPalette(self.green)
        else:
            self.BeamVely.setPalette(self.red)

        if status & (1 << 14):
            self.BeamVely.setPalette(self.green)
        else:
            self.BeamVely.setPalette(self.red)

    def _handel_capacity(self, status):
        if status & (1 << 12):
            self.BeamVelx.setPalette(self.green)
        else:
            self.BeamVelx.setPalette(self.red)

        if status & (1 << 13):
            self.BeamVely.setPalette(self.green)
        else:
            self.BeamVely.setPalette(self.red)

        if status & (1 << 14):
            self.BeamVely.setPalette(self.green)
        else:
            self.BeamVely.setPalette(self.red)

    def _handel_fig_xyz(self, status):
        if status & (1 << 20):
            self.BeamFigx.setPalette(self.green)
        else:
            self.BeamFigx.setPalette(self.red)

        if status & (1 << 21):
            self.BeamFigy.setPalette(self.green)
        else:
            self.BeamFigy.setPalette(self.red)

        if status & (1 << 22):
            self.BeamFigz.setPalette(self.green)
        else:
            self.BeamFigz.setPalette(self.red)

    def _handle_start_test_triggered(self):
        pass

    def _execute_test(self):
        pass

    def shutdown_plugin(self):
        #self._dvl_subscriber_status.unregister()
        self._dvl_subscriber_twist.unregister()

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass


