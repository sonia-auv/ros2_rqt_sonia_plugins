import os
import threading
from time import sleep, time

import math
from rclpy.subscription import Subscription
from rclpy.publisher import Publisher
from rclpy.client import Client
from rclpy.action.client import ActionClient
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QHeaderView, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QBrush, QColor

from std_msgs.msg import Bool
from geometry_msgs.msg import Pose as geoPose
from sonia_common_ros2.msg import MissionTimer, MpcInfo, PoseArray, Pose as soniaPose, MissionStatus, KillStatus

from sonia_common_ros2.srv import ObjectPoseService, SetSimulationAUVService
from sonia_common_ros2.action import MissionControl
from std_srvs.srv import Trigger

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
        self.mission_switch_status= False

        self.sendWaypointButton.setEnabled(False)
        self.sendWaypointButton.setText("Choose a mode")

        self.frameChoice.setCurrentIndex(1)
        #self.missionListDropdown.addItems(["root", "failedTest"])
        
        self.nodeTable.setHorizontalHeaderLabels(["BT Node", "Status"])
        self.nodeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.mission_history =[]       
        
        self.prev_auv = ""
        self.prev_scene = self.sceneChoice.currentText()
        self.prev_run = self.runChoice.currentText()
        
        self.tare_req = Trigger.Request()

        # Subscribers
        self.position_target_subscriber: Subscription = ros_node.create_subscription(geoPose,'/proc_control/current_target', self._position_target_callback,10)
        self.controller_info_subscriber: Subscription = ros_node.create_subscription(MpcInfo, "/proc_control/controller_info", self.set_mpc_info,10)
        self.timeout_subscriber: Subscription = ros_node.create_subscription(MissionTimer,"/sonia_behaviors/timeout", self.timeout_info,10)
        self._mission_switch: Subscription = ros_node.create_subscription(MissionStatus, '/provider_rs485/mission_status', self._mission_switch_callback, 10)

        # Publishers
        self.simulation_start_publisher: Publisher= ros_node.create_publisher(geoPose, "/proc_simulation/start_simulation",10)
        self.single_add_pose_publisher: Publisher = ros_node.create_publisher(soniaPose,"/proc_control/add_pose", 10)
        self.multi_add_pose_publisher: Publisher = ros_node.create_publisher(PoseArray,"/proc_planner/send_pose_array",10)
        self.reset_trajectory_publisher: Publisher = ros_node.create_publisher(Bool, "/proc_control/reset_trajectory", 10)
        self.set_dvl_started_publisher: Publisher = ros_node.create_publisher(Bool, "/provider_dvl/enable_disable_dvl", 10)

        # Services
        self.initial_position_service: Client = ros_node.create_client(ObjectPoseService,"/proc_simulation/auv_pose")
        self.set_auv_service: Client = ros_node.create_client(SetSimulationAUVService, "/proc_simulation/select_auv")
        self.depth_tare_service: Client= ros_node.create_client(Trigger, "/provider_depth/tare")
        self.imu_tare_service: Client= ros_node.create_client(Trigger, "/provider_imu/tare")

        #Actions
        self.mission_client = ActionClient(ros_node, MissionControl, "MissionControl")

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

        # Waypoint tab buttons
        self.resetTrajectory.clicked.connect(self._clear_waypoint)
        self.sendWaypointButton.clicked.connect(self.send_position)

        # Unity tab buttons
        self.updateUnityButton.clicked.connect(self.update_unity)

        # Mission tab buttons
        self.loadMissionBtn.clicked.connect(self._mission_load_action)
        self.refreshBtn.clicked.connect(self._mission_dropdown_refresh)
    
    def timeout_info(self, msg):
        if msg.status == 1:
            self.createLabel.emit(msg)
        else:
            if msg.unique_id in self.listMissionLabels:
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
        self.listMissionLabels[msg.unique_id] = [label1, label2]
        t = threading.Thread(target = self.countdownThread, args=(msg.unique_id, timeout))
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
        label = self.listMissionLabels[msg.unique_id][1]
        label.setStyleSheet("background-color: green")
        label.setText(f"{label.text()} (Completed)")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(msg.unique_id,))
        t.start()
    
    @pyqtSlot(MissionTimer)
    def missionTimeout(self, msg):
        label = self.listMissionLabels[msg.unique_id][1]
        label.setStyleSheet("background-color: red")
        label.setText(f"{0:.1f} (Timed Out)")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(msg.unique_id,))
        t.start()
    
    @pyqtSlot(MissionTimer)
    def missionFailed(self, msg):
        label = self.listMissionLabels[msg.unique_id][1]
        label.setStyleSheet("background-color: red")
        label.setText(f"{label.text()} (Failed)")
        t = threading.Thread(target = self.countdownTillDestroyThread, args=(msg.unique_id,))
        t.start()

    def _reset_depth(self):
        rep = self.depth_tare_service.call_async(self.tare_req)
        rep.add_done_callback(self.tare_callback)
        
    def _tare_imu(self):
        rep=self.imu_tare_service.call_async(self.tare_req)
        rep.add_done_callback(self.tare_callback)
        
    def tare_callback(self, rep):
        try:
            fut= rep.result().message
            print(fut)
        except Exception as e:
            print(e)
            print('not tared.')
    def startDVL(self):
        dvl_state= Bool()
        dvl_state.data=True
        self.set_dvl_started_publisher.publish(dvl_state)

    def stopDVL(self):
        dvl_state= Bool()
        dvl_state.data=False
        self.set_dvl_started_publisher.publish(dvl_state)

    def _mission_load_action(self):
        if self.mission_switch_status:
            self.show_error("The mission switch is pulled, push the switch to load mission")
        else:
            mission = self.missionTextfield.text()
            self.loadMissionBtn.setStyleSheet("background-color: orange;") 
            self.loadMissionBtn.setEnabled(False) 
            check_server=self.mission_future =self._send_goal(mission)
            if check_server:
                self.mission_future.add_done_callback(self._goal_response_callback)            
        
    def _goal_response_callback(self, future):
        goal = future.result()
        if goal.accepted:
            self.loadMissionBtn.setStyleSheet("background-color: green;") 
        else:
            self.loadMissionBtn.setStyleSheet("background-color: red;") 
            
    def _feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        for item in self.mission_history:
            if item['uid'] == fb.uid:
                item['status'] = fb.status
                continue
        ex = any(row['uid']==fb.uid for row in self.mission_history)
        if not ex:        
            self.mission_history.append({'uid': fb.uid, 'name': fb.node_name, 'status': fb.status}) 
        self.nodeTable.setRowCount(len(self.mission_history))
        for i, node in enumerate(self.mission_history):
            color = "gray"
            if node['status'] == "RUNNING":
                color = "orange"
            elif node['status'] == "FAILURE":
               color = "red"
            elif node['status'] == "SUCCESS":
                color = "green"
            item = QTableWidgetItem(node['status'])
            item.setBackground(QBrush(QColor(color)))  
             
            self.nodeTable.setItem(i, 0, QTableWidgetItem(node['name']))
            self.nodeTable.setItem(i, 1, item)
        
    def _mission_dropdown_refresh(self):
        self.loadMissionBtn.setStyleSheet("background-color: None") 
        self.loadMissionBtn.setEnabled(True) 
        self.mission_history.clear()
        self.nodeTable.setRowCount(0)
        print("mission refresh")

    def _send_goal(self, mission):
        goal_msg = MissionControl.Goal()
        goal_msg.mission = mission
        server_ready = self.mission_client.wait_for_server(5)
        if not server_ready:
            self.show_error("Server isn't responding or running")
            return False
        return self.mission_client.send_goal_async(goal_msg, self._feedback_callback)
    def _reset_position(self):
        pose = geoPose()
        pose.position.x = 0.0
        pose.position.y = 0.0
        pose.position.z = 0.0

        pose.orientation.x = 0.0
        pose.orientation.y = 0.0
        pose.orientation.z = 0.0
        pose.orientation.w = 1.0

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
                obj= ObjectPoseService.Request()
                obj.object_name=auv_name
                resp = self.initial_position_service.call_async(obj)
                resp.add_done_callback(self._initial_pos_service_cb) 
            else:
                print('AUV environment variable not properly set.')

        except Exception as e:
            print(e)
            print('Simulation is not started')
            self.show_error('Simulation is not started')

    def _initial_pos_service_cb(self, resp):
        pose = geoPose()
        pose.position.x = resp.result().object_pose.position.x
        pose.position.y = resp.result().object_pose.position.y
        pose.position.z = resp.result().object_pose.position.z

        pose.orientation.x = resp.result().object_pose.orientation.x
        pose.orientation.y = resp.result().object_pose.orientation.y
        pose.orientation.z = resp.result().object_pose.orientation.z
        pose.orientation.w = resp.result().object_pose.orientation.w

        self.simulation_start_publisher.publish(pose)
        print('initial pose sent.')

    def _position_target_callback(self,data):
        self.current_target_received.emit(data)
    def _mission_switch_callback(self, msg: KillStatus):
        self.mission_switch_status= msg.status

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
            obj= SetSimulationAUVService.Request()
            os.environ["AUV"] = self.subChoice.currentText()
            obj._object_name=self.subChoice.currentText()
            self.set_auv_service.call_async(obj)
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
        msgBox.setIcon(QMessageBox.Warning)
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
        self.set_dvl_started_publisher.destroy()
        self.initial_position_service.destroy()
        self.set_auv_service.destroy()
        self.depth_tare_service.destroy()
        self.imu_tare_service.destroy()
