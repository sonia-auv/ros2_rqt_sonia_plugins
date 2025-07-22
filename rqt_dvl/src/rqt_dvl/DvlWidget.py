import os

from rclpy.subscription import Subscription
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from sonia_common_ros2.msg import BodyVelocityDVL

class DvlWidget(QMainWindow):

    dvl_velocity_recieved = pyqtSignal(BodyVelocityDVL)

    def __init__(self, ros_node):
        super(DvlWidget, self).__init__()
        # Give QObjects reasonable names
        self.setObjectName('DvlControlWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_dvl'), 'resource', 'mainwindow.ui')
        loadUi(ui_file, self)

        self.setObjectName('MyDvlControlWidget')

        self._dvl_subscriber: Subscription= ros_node.create_subscription(BodyVelocityDVL,"/provider_dvl/dvl_velocity", self._dvl_subscriber_cb, 10)
        
        self.dvl_velocity_recieved.connect(self.show_dvl_velocity)

    def _dvl_subscriber_cb(self, data):
        self.dvl_velocity_recieved.emit(data)

    def show_dvl_velocity(self, msg: BodyVelocityDVL):
        self.xVelTextfield.setText('%.5f' % msg.x_vel_btm)
        self.yVelTextfield.setText('%.5f' % msg.y_vel_btm)
        self.zVelTextfield.setText('%.5f' % msg.z_vel_btm)
        self.eVelTextfield.setText('%.5f' % msg.e_vel_btm)
        
        self.vel1Textfield.setText('%.5f' % msg.velocity1)
        self.vel2Textfield.setText('%.5f' % msg.velocity2)
        self.vel3Textfield.setText('%.5f' % msg.velocity3)
        self.vel4Textfield.setText('%.5f' % msg.velocity4)     
        
    def shutdown_plugin(self):
        self._dvl_subscriber.destroy()