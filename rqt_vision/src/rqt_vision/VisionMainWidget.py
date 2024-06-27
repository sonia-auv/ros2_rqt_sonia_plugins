import os
import rospy
import rclpy
import rospkg
import cv2
import time

from rclpy.client import Client
from rclpy.service import Service
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QMenu, QAction, QWidget
from sensor_msgs.msg import CompressedImage as SensorCompressedImage
from sonia_common.msg import VisionTarget
from sonia_common.srv import GetFilterchainFromExecution, GetMediaFromExecution, ExecuteCmd, Republish
from cv_bridge import CvBridge, CvBridgeError
from .ConfigureFilterchainWidget import ConfigureFilterchainWidget
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

from sonia_common.srv import GetInformationList


class VisionMainWidget(QWidget):
    result_change = pyqtSignal('QString')
    image_change = pyqtSignal('PyQt_PyObject')

    def __init__(self, internal_node):
        super(VisionMainWidget, self).__init__()
        ###try:
            #rospy.wait_for_service('/proc_image_processing/get_information_list', timeout=2)
            ##rospy.wait_for_service('/proc_image_processing/get_filterchain_from_execution', timeout=2)
            #rospy.wait_for_service('/proc_image_processing/get_media_from_execution', timeout=2)
            #rospy.wait_for_service('/proc_image_processing/execute_cmd', timeout=2)
        #except rospy.ROSException:
            #rospy.loginfo('Services unavailable')
        ui_file = os.path.join(get_package_share_directory('rqt_vision'), 'resource', 'mainwidget.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Vision UI')

        self._current_execution = None
        self._current_execution_subscriber = None
        self._current_execution_subscriber_result = None
        self._image_seq = 0
        self._filterchain = None
        self._is_recording = False
        self._video_writer = None
        self._cv_image = None
        self._widget = None
        self.bridge = CvBridge()
        self.result_change.connect(self._handle_result)
        self.image_change.connect(self._handle_new_image)
        ##### Service
        self._srv_get_information_list = internal_node.create_client(GetInformationList, '/proc_image_processing/get_information_list')
        while not self._srv_get_information_list.wait_for_service(2.0):
            internal_node.get_logger().info('se')
        self._srv_get_information_list = rospy.ServiceProxy('/proc_image_processing/get_information_list',
                                                            GetInformationList)
        self._srv_get_filterchain_from_execution = rospy.ServiceProxy(
            '/proc_image_processing/get_filterchain_from_execution', GetFilterchainFromExecution)
        self._srv_get_media_from_execution = rospy.ServiceProxy('/proc_image_processing/get_media_from_execution',
                                                                GetMediaFromExecution)
        self._srv_execute_cmd = rospy.ServiceProxy('/proc_image_processing/execute_cmd', ExecuteCmd)

        self._srv_start_republisher = rospy.ServiceProxy('//image_republisher_node/republish', Republish)
        ###
        self.image_frame_mouse_release_event_original = self.imageFrame.mouseReleaseEvent
        self.imageFrame.mouseReleaseEvent = self.image_frame_mouse_release_event

        self.refresh_button.clicked[bool].connect(self.fill_execution_list)
        self.current_execution.currentIndexChanged[int].connect(self.current_execution_index_changed)
        self.image_paint_event_original = self.imageFrame.paintEvent
        self.imageFrame.paintEvent = self.image_paint_event
        self.fill_execution_list()
        self._define_menu()

    def _define_menu(self):
        self._menu = QMenu(self.imageFrame)

        configureAction = QAction("Configure ...", self.imageFrame, triggered=self.configure_filterchain_action)
        self._menu.addAction(configureAction)
        self._menu.addSeparator()
        self._recordAction = QAction("Record ...", self.imageFrame, triggered=self.record_execution_action)
        self._menu.addAction(self._recordAction)
        self._stop_recordAction = QAction("Stop Record", self.imageFrame, triggered=self.stop_record_execution_action)
        self._stop_recordAction.setEnabled(False)
        self._menu.addAction(self._stop_recordAction)
        self._menu.addSeparator()

        deleteAction = QAction(self.imageFrame.tr("Delete this execution"), self.imageFrame,
                               triggered=self.delete_current_execution)
        self._menu.addAction(deleteAction)

    def fill_execution_list(self):
        self._refresh_clean()
        self._current_execution = None
        self.current_execution.clear()

        try:
            execution_string = self._srv_get_information_list(1)
            execution_list = execution_string.list.split(';')
            if len(execution_list) == 0:
                return
            self._current_execution = execution_list[0]
            for execution in execution_list:
                if len(execution) > 0:
                    self.current_execution.addItem(execution)

        except rospy.ServiceException as err:
            rospy.logerr(err)

    def current_execution_index_changed(self, index):
        self._refresh_clean()

        new_execution = self.current_execution.itemText(index)
        self._current_execution = new_execution

        try:
            self._filterchain = self._srv_get_filterchain_from_execution(self._current_execution)
        except rospy.ServiceException as err:
            rospy.logerr(err)
        
        topic_name = "/proc_image_processing/{}_image/compressed".format(new_execution)
        
        try:
            self._srv_start_republisher('/proc_image_processing/' + new_execution + '_image', 1)
            ip = os.getenv('ROS_IP', '127.0.0.1')
            topic_name = '/proc_image_processing/{}_image_{}'.format(new_execution, ip.replace('.', ''))
            self._current_execution_subscriber = rospy.Subscriber(topic_name,
                                                                  SensorCompressedImage, self.current_execution_callback)
            print('subscribe ', topic_name)
        except:
            rospy.logerr('Republisher node is not stated !')
            self._current_execution_subscriber = rclpy.Subscriber(topic_name,
                                                                  SensorCompressedImage, self.current_execution_callback)
            

        self._current_execution_subscriber_result = rospy.Subscriber(
            '/proc_image_processing/' + new_execution + '_result',
            VisionTarget,
            self.current_execution_result_callback)

    def _refresh_clean(self):
        if self._current_execution_subscriber is not None:
            self._current_execution_subscriber.unregister()

        if self._current_execution_subscriber_result is not None:
            self._current_execution_subscriber_result.unregister()

        self.result_text.setText('')
        self._cv_image = None
        self._image_seq = 0
        self.imageFrame.update()

    def current_execution_callback(self, img):
        self.image_change.emit(img)

    def _handle_new_image(self, img):
        try:
            if self._image_seq < img.header.seq:
                cv_image = self.bridge.compressed_imgmsg_to_cv2(img, desired_encoding="rgb8")
                self._image_seq = img.header.seq
                height, width, channel = cv_image.shape
                bytesPerLine = 3 * width
                self._cv_image = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_RGB888)

                if self._is_recording:
                    if self._video_writer is None:
                        four_cc = cv2.VideoWriter_fourcc(*'HFYU')
                        self._video_writer = cv2.VideoWriter(self._recording_file_name, four_cc, float(15),
                                                             (width, height))
                    temp = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
                    self._video_writer.write(temp)
        except CvBridgeError as e:
            print(e)
        self.imageFrame.update()

    def image_paint_event(self, data):
        self.image_paint_event_original(data)
        if self._cv_image is None:
            return;
        img = self._cv_image

        painter = QPainter(self.imageFrame)
        painter.drawImage(data.rect(), img)
        painter.end()

    def current_execution_result_callback(self, visionTarget):
        result = 'X:{}, Y:{}, width:{:.2f}, height:{:.2f}, angle:{:.2f}, desc_1:{}, desc_2:{}'.format(visionTarget.x,
                                                                                                      visionTarget.y,
                                                                                                      visionTarget.width,
                                                                                                      visionTarget.height,
                                                                                                      visionTarget.angle,
                                                                                                    #   visionTarget.distance,
                                                                                                      visionTarget.desc_1,
                                                                                                      visionTarget.desc_2)
        self.result_change.emit(result)

    def _handle_result(self, result):
        self.result_text.setText(result)

    def image_frame_mouse_release_event(self, event):
        if event.button() == Qt.RightButton:
            self._menu.exec_(self.imageFrame.mapToGlobal(event.pos()))

    def delete_current_execution(self):

        if self._current_execution is None or self._filterchain is None:
            return

        try:
            media = self._srv_get_media_from_execution(self._current_execution)
            self._srv_execute_cmd(self._current_execution, self._filterchain.list, media.list, 2)
        except rospy.ServiceException as err:
            rospy.logerr(err)

        self.fill_execution_list()

    def configure_filterchain_action(self):
        if self._filterchain is None:
            return
        self._widget = ConfigureFilterchainWidget(self._current_execution, self._filterchain)
        self._widget.show()

    def shutdown_plugin(self):
        if self._current_execution_subscriber is not None:
            self._current_execution_subscriber.unregister()
            self._current_execution_subscriber_result.unregister()
        if self._widget is not None:
            self._widget.close()

    def record_execution_action(self):
        Tk().withdraw()
        filename = asksaveasfilename(defaultextension='.avi')
        self._recording_file_name = filename
        if len(self._recording_file_name) > 0:
            self._is_recording = True
            self._recordAction.setEnabled(False)
            self._stop_recordAction.setEnabled(True)

    def stop_record_execution_action(self):
        self._is_recording = False
        time.sleep(0.1)
        self._video_writer.release()
        self._video_writer = None
        self._recordAction.setEnabled(True)
        self._stop_recordAction.setEnabled(False)
