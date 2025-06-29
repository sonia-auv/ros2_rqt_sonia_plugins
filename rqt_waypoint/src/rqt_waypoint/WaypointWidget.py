import os
import threading
from time import sleep, time

import math
import rclpy
import rclpy.logging
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from rclpy.client import Client
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QLabel
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from std_msgs.msg import Bool, Empty as EmptyMsg
from geometry_msgs.msg import Pose as geoPose
from sonia_common_ros2.msg import MissionTimer, MpcInfo, PoseArray, Pose as soniaPose

from sonia_common_ros2.srv import ObjectPoseService, SetSimulationAUVService
from std_srvs.srv import Trigger, Empty

from tf_transformations import euler_from_quaternion

class WaypointWidget(QMainWindow):

    current_target_received = pyqtSignal('PyQt_PyObject')
    createLabel = pyqtSignal(MissionTimer)
    greenLabel = pyqtSignal(MissionTimer)
    redLabel = pyqtSignal(MissionTimer)
    failedLabel = pyqtSignal(MissionTimer)
    listMissionLabels = {}

    def __init__(self, ros_node):
        super(WaypointWidget, self).__init__()
        # Give QObjects reasonable names

        self.setObjectName('WaypointWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_waypoint'), 'resource', 'Mainwindow.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Waypoint')

        self.current_mode_id = 0
        self.z_pose = 0
        self.labelsCreated = 0

        self.sendWaypointButton.setEnabled(False)
        self.sendWaypointButton.setText("Choose a mode")

        self.frameChoice.setCurrentIndex(1)

        self.prev_auv = ""
        self.prev_scene = ""
        self.prev_run = ""

        # Subscribers
        self.position_target_subscriber: Subscription = ros_node.create_subscription(geoPose,'/proc_control/current_target', self._position_target_callback,10)
        self.controller_info_subscriber: Subscription = ros_node.create_subscription(MpcInfo, "/proc_control/controller_info", self.set_mpc_info,10)
        #self.timeout_subscriber: Subscription = ros_node.create_subscription(MissionTimer,"/sonia_behaviors/timeout", self.timeout_info)
        #self.auv_position_subscriber: Subscription= ros_node.create_subscription(Odometry, "/proc_nav/auv_states", self.auv_pose_callback)
        #self.auv_position_subscriber = rospy.Subscriber("/telemetry/auv_states", Odometry, self.auv_pose_callback)

        # Publishers
        self.simulation_start_publisher: Publisher= ros_node.create_publisher(geoPose, "/proc_simulation/start_simulation",10)
        self.single_add_pose_publisher: Publisher = ros_node.create_publisher(soniaPose,"/proc_control/add_pose", 10)
        self.multi_add_pose_publisher: Publisher = ros_node.create_publisher(PoseArray,"/proc_planner/send_pose_array",10)
        self.reset_trajectory_publisher: Publisher = ros_node.create_publisher(Bool, "/proc_control/reset_trajectory", 10)
        self.auv7_tare_publisher: Publisher = ros_node.create_publisher(EmptyMsg, "/provider_dvl/setDepthOffset", 10)
        self.set_dvl_started_publisher: Publisher = ros_node.create_publisher(Bool, "/provider_dvl/enable_disable_dvl", 10)
        #self.set_sonar_started_publisher: Publisher = ros_node.create_publisher(Bool, "/provider_sonar/enable_disable_ping", 10)
        #self.set_initial_position_publisher: Publisher = ros_node.create_publisher(Bool, "/proc_nav/reset_pos", 10)

        # Services
        self.initial_position_service: Client = ros_node.create_client(ObjectPoseService,"/proc_simulation/auv_pose")
        self.set_auv_service: Client = ros_node.create_client(SetSimulationAUVService, "/proc_simulation/select_auv")
        self.depth_tare_service: Client= ros_node.create_client(Empty, "/provider_depth/tare")
        self.imu_tare_service: Client= ros_node.create_client(Trigger, "/provider_imu/tare")

        self.current_target_received.connect(self._current_target_received)
        self.createLabel.connect(self.addButton)
        self.redLabel.connect(self.missionTimeout)
        self.greenLabel.connect(self.missionComplete)
        self.failedLabel.connect(self.missionFailed)

        # Simulation menu
        self.actionStart_Simulation.triggered.connect(self.send_initial_position)
        self.actionReset_Position.triggered.connect(self._reset_position)

        # Sensors menu
        self.actionReset_Depth.triggered.connect(self._reset_depth)
        self.actionTare_IMU.triggered.connect(self._tare_imu)
        self.actionStart_DVL.triggered.connect(self.startDVL)
        self.actionStop_DVL.triggered.connect(self.stopDVL)
        self.actionStart_SONAR.triggered.connect(self.startSonar)
        self.actionStop_SONAR.triggered.connect(self.stopSonar)

        # Waypoint tab buttons
        self.resetTrajectory.clicked.connect(self._clear_waypoint)
        self.sendWaypointButton.clicked.connect(self.send_position)

        # Unity tab buttons
        self.updateUnityButton.clicked.connect(self.update_unity)
    
    def timeout_info(self, msg):
        if msg.status == 1:
            self.createLabel.emit(msg)
        else:
            if msg.uniqueID in self.listMissionLabels:
                if msg.status == 2:
                    self.missionComplete(msg)
                elif msg.status == 3:
                    self.missionTimeout(msg)
                elif msg.status == 4:
                    self.missionFailed(msg)
    
    @pyqtSlot(MissionTimer)
    def addButton(self, msg: MissionTimer):
        label1 = QLabel()
        label1.setText(msg.mission)
        self.missionGrid.addWidget(label1, self.labelsCreated, 0)
        timeout = float(msg.timeout)
        label2 = QLabel()
        label2.setText(f"{timeout:.1f}")
        self.missionGrid.addWidget(label2, self.labelsCreated, 1)
        self.labelsCreated += 1
        self.listMissionLabels[msg.uniqueID] = [label1, label2]
        t = threading.Thread(target = self.countdownThread, args=(msg.uniqueID, timeout))
        t.start()
    
    def countdownThread(self, uniqueID, timeout):
        label = self.listMissionLabels[uniqueID][1]
        startTime = time()
        while (time())-startTime <= timeout:
            sleep(0.1)
            if label.styleSheet() != "":
                return
            label.setText(f"{(timeout-((time())-startTime)):.1f}")
        label.setStyleSheet("background-color: yellow")
        label.setText(f"{0:.1f}")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(uniqueID,))
        t.start()
    
    def countdownTillDestroyThread(self, uniqueID):
        sleep(30)
        try:
            self.listMissionLabels[uniqueID][0].close()
            self.listMissionLabels[uniqueID][1].close()
            del self.listMissionLabels[uniqueID]
        except (RuntimeError, KeyError):
            pass

    @pyqtSlot(MissionTimer)
    def missionComplete(self, msg):
        label = self.listMissionLabels[msg.uniqueID][1]
        label.setStyleSheet("background-color: green")
        label.setText(f"{label.text()} (Completed)")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(msg.uniqueID,))
        t.start()
    
    @pyqtSlot(MissionTimer)
    def missionTimeout(self, msg):
        label = self.listMissionLabels[msg.uniqueID][1]
        label.setStyleSheet("background-color: red")
        label.setText(f"{0:.1f} (Timed Out)")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(msg.uniqueID,))
        t.start()
    
    @pyqtSlot(MissionTimer)
    def missionFailed(self, msg):
        label = self.listMissionLabels[msg.uniqueID][1]
        label.setStyleSheet("background-color: red")
        label.setText(f"{label.text()} (Failed)")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(msg.uniqueID,))
        t.start()

    def _reset_depth(self):
        # Getting AUV name environnment variable.
        auv_name = os.getenv('AUV')
        if auv_name == "AUV7":
            tare = Empty.Request()
            self.auv7_tare_publisher.publish(tare)
        elif auv_name == "AUV8":
            try:
                req = Empty.Request()
                self.depth_tare_service.call(req)
            except Exception as e:
                print(e)
                rclpy.logging.get_logger().info('Provider depth is not started.')
        else:
            rclpy.logging.get_logger().info('AUV environment variable not properly set.')

    def _tare_imu(self):
        try:
            req= Trigger.Request()
            self.imu_tare_service.call_async(req)
        except Exception as e:
            print(e)
            rclpy.logging.get_logger().info('Provider IMU is not started.')

    def startDVL(self):
        dvl_state= Bool()
        dvl_state.data=True
        self.set_dvl_started_publisher.publish(dvl_state)

    def stopDVL(self):
        dvl_state= Bool()
        dvl_state.data=False
        self.set_dvl_started_publisher.publish(dvl_state)

    def startSonar(self):
        #self.set_sonar_started_publisher.publish(True)
        pass

    def stopSonar(self):
        #self.set_sonar_started_publisher.publish(False)
        pass

    def _reset_position(self):

        pose = geoPose()
        pose.position.x = 0
        pose.position.y = 0
        pose.position.z = 0

        pose.orientation.x = 0
        pose.orientation.y = 0
        pose.orientation.z = 0
        pose.orientation.w = 0

        self.simulation_start_publisher.publish(pose)
        # if self.current_mode_id == 0:
        #     self.set_initial_position_publisher.publish(data=True)
        # else:
        #     self.show_error('Control mode must be 0 to reset position')
    
    def set_mpc_info(self, msg: MpcInfo):
        self.current_mode_id = msg.mpc_mode
        if self.current_mode_id != 0:
            self.sendWaypointButton.setText("Send Waypoint")
            self.sendWaypointButton.setEnabled(True)
        else:
            self.sendWaypointButton.setText("Choose a mode")
            self.sendWaypointButton.setEnabled(False)

    # def auv_pose_callback(self, msg):
    #     self.z_pose = float(msg.pose.pose.position.z)
    #     self.z_pose

    def _clear_waypoint(self):
        reset_state= Bool()
        reset_state.data=True
        self.reset_trajectory_publisher.publish(reset_state)

    def send_initial_position(self):
        try:
            auv_name = os.getenv('AUV')
            if auv_name:
                resp = self.initial_position_service.call(object_name=auv_name)
                pose = geoPose()
                pose.position.x = resp.object_pose.position.x
                pose.position.y = resp.object_pose.position.y
                pose.position.z = resp.object_pose.position.z

                pose.orientation.x = resp.object_pose.orientation.x
                pose.orientation.y = resp.object_pose.orientation.y
                pose.orientation.z = resp.object_pose.orientation.z
                pose.orientation.w = resp.object_pose.orientation.w

                self.simulation_start_publisher.publish(pose)
            else:
                rclpy.logging.get_logger().info('AUV environment variable not properly set.')
                #rospy.logerr('AUV environment variable not properly set.')

        except Exception as e:
            print(e)
            rclpy.logging.get_logger().info('Simulation is not started')
            #rospy.logerr('Simulation is not started')
            self.show_error('Simulation is not started')

    def _position_target_callback(self,data):
        self.current_target_received.emit(data)

    def _current_target_received(self, data):
        try:
            self.xPositionCurrent.setText('%.2f' % data.position.x)
            self.yPositionCurrent.setText('%.2f' % data.position.y)
            self.zPositionCurrent.setText('%.2f' % data.position.z)
            self.rollPositionCurrent.setText('%.2f' % math.degrees(euler_from_quaternion([data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w],'szyx')[2]))
            self.pitchPositionCurrent.setText('%.2f' % math.degrees(euler_from_quaternion([data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w],'szyx')[1]))
            self.yawPositionCurrent.setText('%.2f' % math.degrees(euler_from_quaternion([data.orientation.x,data.orientation.y,data.orientation.z,data.orientation.w],'szyx')[0]))
        except ValueError:
            pass

    def reset_commands(self):
        self.xPositionTarget.setText('0.0')
        self.yPositionTarget.setText('0.0')
        self.zPositionTarget.setText('0.0')
        self.rollPositionTarget.setText('0.0')
        self.pitchPositionTarget.setText('0.0')
        self.yawPositionTarget.setText('0.0')
        
        self.speed.setText('0')
        self.fine.setText('0.0')

    def update_unity(self):
        if self.subChoice.currentText() != self.prev_auv:
            os.environ["AUV"] = self.subChoice.currentText()
            self.set_auv_service.call(object_name=self.subChoice.currentText())
            self.prev_auv = self.subChoice.currentText()

        if self.sceneChoice.currentText() != self.prev_scene:
            # self.show_error(self.sceneChoice.currentText())
            self.show_error("Scene choice not implented yet")
            self.prev_scene = self.sceneChoice.currentText()

        if self.runChoice.currentText() != self.prev_run:
            # self.show_error(self.sceneChoice.currentText())
            self.show_error("Run choice not implented yet")
            self.prev_run = self.runChoice.currentText()

    def send_position(self):
        try:
            print("Sending waypoint.")
            z_axis_problem = False
            x_val = float(self.xPositionTarget.text())
            y_val = float(self.yPositionTarget.text())
            z_val = min(float(self.zPositionTarget.text()), 3)
            roll_val = float(self.rollPositionTarget.text())
            pitch_Val = float(self.pitchPositionTarget.text())
            yaw_val = float(self.yawPositionTarget.text())
            frame_val = self.frameChoice.currentIndex()
            speed_val = int(self.speed.text())
            fine_val = float(self.fine.text())
            method_val = self.methodChoice.currentIndex()
            path_val = self.pathLength.isChecked()
            # Verify z-axis
            if frame_val == 0 or frame_val == 2:
                if z_val > 4: z_axis_problem = True
            # else:
            #     if z_val + self.z_pose > 4: z_axis_problem = True  
            if z_axis_problem:
                self.show_error("Depth too low.")
            else:
                if self.current_mode_id == 11:
                    if speed_val <= 0:
                        self.show_error("Speed incorrect.")
                    else:
                        # Send a single waypoint.
                        pose = soniaPose()
                        pose.position.x = x_val
                        pose.position.y = y_val
                        pose.position.z = z_val
                        pose.orientation.x = roll_val
                        pose.orientation.y = pitch_Val
                        pose.orientation.z = yaw_val
                        pose.frame = frame_val
                        pose.speed = speed_val
                        pose.fine = fine_val
                        pose.rotation = path_val

                        self.single_add_pose_publisher.publish(pose)
                        self.reset_commands()

                elif self.current_mode_id == 10:
                    if speed_val < 0 or speed_val > 2:
                        self.show_error("Speed profile incorrect.")
                    else:
                        # Send a multi-waypoint.
                        pose = soniaPose()
                        pose.position.x = x_val
                        pose.position.y = y_val
                        pose.position.z = z_val
                        pose.orientation.x = roll_val
                        pose.orientation.y = pitch_Val
                        pose.orientation.z = yaw_val
                        pose.frame = frame_val
                        pose.speed = speed_val
                        pose.fine = fine_val
                        pose.rotation = path_val

                        multi_pose = PoseArray()
                        multi_pose.poses.append(pose)
                        multi_pose.interpolation_method = method_val

                        self.multi_add_pose_publisher.publish(multi_pose)
                        self.reset_commands()
        except ValueError:
            pass

    def show_error(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.warning)
        msgBox.setText(message)
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    def shutdown_plugin(self):
        self.controller_info_subscriber.destroy()
        self.position_target_subscriber.destroy()
        self.simulation_start_publisher.destroy()
        self.single_add_pose_publisher.destroy()
        self.multi_add_pose_publisher.destroy()
        self.reset_trajectory_publisher.destroy()
        self.auv7_tare_publisher.destroy()
        self.set_dvl_started_publisher.destroy()
        self.initial_position_service.destroy()
        self.set_auv_service.destroy()
        self.depth_tare_service.destroy()
        self.imu_tare_service.destroy()
