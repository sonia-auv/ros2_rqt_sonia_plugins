import os
from rclpy.subscription import Subscription
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from std_msgs.msg import Float32

class DepthIndicatorWidget(QWidget):
    odometry_received = pyqtSignal('PyQt_PyObject')
    def __init__(self, internal_node):
        super(DepthIndicatorWidget, self).__init__()
        ui_file = os.path.join(get_package_share_directory('rqt_depth_indicator'), 'resource', 'mainwidget.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Depth Indicator')

        self._odom_subscriber:Subscription = internal_node.create_subscription(Float32,'/provider_depth/depth', self._odom_callback, 100)

        self.odometry_received.connect(self._handle_result)

    def _odom_callback(self, msg):
        self.odometry_received.emit(msg)

    def _handle_result(self, z_depth):
        
        depth = int(z_depth.data * 10)
        self.depthSlider.setValue(depth)
        self.depthValue.setText(str(depth / 10.0))

    def shutdown_plugin(self):
        self._odom_subscriber.destroy()