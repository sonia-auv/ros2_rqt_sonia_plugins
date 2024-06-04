import os
import math
from rclpy.subscription import Subscription
from ament_index_python.packages import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from nav_msgs.msg import Odometry
#from tf_transformations import euler_from_quaternion


class DepthIndicatorWidget(QWidget):
    odometry_received = pyqtSignal('QString')
    def __init__(self, internal_node):
        super(DepthIndicatorWidget, self).__init__()

        ui_file = os.path.join(get_package_share_directory('rqt_depth_indicator'), 'resource', 'mainwidget.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Depth Indicator')

        self._odom_subscriber:Subscription = internal_node.create_subscription(Odometry,'/proc_nav/auv_states', self._odom_callback,10)

        self.odometry_received.connect(self._handle_result)

    def _odom_callback(self, data):
        self.odometry_received.emit(str(data.pose.pose.position.z))

    def _handle_result(self, z_depth):
        depth = int(float(z_depth) * 10)
        self.depthSlider.setValue(depth)
        self.depthValue.setText(str(depth / 10.0))

    def shutdown_plugin(self):
        self._odom_subscriber.destroy()
