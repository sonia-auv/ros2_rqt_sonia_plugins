import os
from ament_index_python.packages import get_package_share_directory

from python_qt_binding import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from rclpy.client import Client
from rclpy.node import Node
from sonia_common_ros2.srv import AiActivationService

class CameraWidget(QWidget):

    def __init__(self, ros_node: Node):
        super(CameraWidget, self).__init__()
        self.setObjectName('CameraWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_toolbar'), 'resource', 'start_cam.ui')
        loadUi(ui_file, self)
        
        self.activateBtn.setStyleSheet("background-color: green")
        self.activateBtn.setCheckable(True)
        
        # Services
        self.ai_activate_service: Client = ros_node.create_client(AiActivationService,"/proc_vision/ai_activation")

        self.activateBtn.toggled.connect(self.handle_activation_click)

    def handle_activation_click(self, checked):
        if checked:
            server_ready = self.ai_activate_service.wait_for_service(3)
            if not server_ready:
                return
            request = AiActivationService.Request()
            request.model_choice = self.nbModel.value()
            cam = self.cameraPick.currentText()
            if cam == "Front":
                request.camera_choice = 1
            elif cam == "Bottom":
                request.camera_choice = 2
            elif cam == "Both":
                request.camera_choice = 3
            
            rep=self.ai_activate_service.call_async(request)
            rep.add_done_callback(self._activation_cb)
            self.activateBtn.setText("Deactivate")
        else:
            server_ready = self.ai_activate_service.wait_for_service(3)
            if not server_ready:
                return
            request = AiActivationService.Request()
            request.camera_choice = 0
            
            rep=self.ai_activate_service.call_async(request)
            rep.add_done_callback(self._activation_cb)
            self.activateBtn.setText("Activate")
        
    def _activation_cb(self, future):
        self.modelName.setText(future.result().model_name)     
