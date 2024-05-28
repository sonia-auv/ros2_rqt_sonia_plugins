import os
import rclpy
import rospkg
import threading
from ament_index_python.packages import get_package_share_directory
from .ThrusterAction import ThrusterAction

from python_qt_binding import loadUi
from PyQt5.QtWidgets import QMainWindow


from sonia_common_ros2.msg import MotorMessages
from std_msgs.msg import Bool
from std_srvs.srv import Empty

class ThrusterWidget(QMainWindow):

    def __init__(self, internal_node):
        super(ThrusterWidget, self).__init__()
        # Give QObjects reasonable names
        self.setObjectName('ThrusterControlWidget')

        ui_file = os.path.join(get_package_share_directory('rqt_thruster_control'), 'resource', 'Mainwindow.ui')
        loadUi(ui_file, self)

        self.setObjectName('MyThrusterControlWidget')

        # Subscribe to slot
        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.resetPwmButton.setEnabled(False)
        self.enableButton.clicked[bool].connect(self._handle_enableButton_clicked)
        self.disableButton.clicked[bool].connect(self._handle_disableButton_clicked)
        self.actionStart_test.triggered.connect(self._handle_start_test_triggered)
        self.resetPwmButton.clicked[bool].connect(self._handle_resetPwmButton_clicked)

        self.thruster_1 = ThrusterAction(self, 0, 'T1')
        self.thruster_2 = ThrusterAction(self, 1, 'T2')
        self.thruster_3 = ThrusterAction(self, 2, 'T3')
        self.thruster_4 = ThrusterAction(self, 3, 'T4')
        self.thruster_5 = ThrusterAction(self, 4, 'T5')
        self.thruster_6 = ThrusterAction(self, 5, 'T6')
        self.thruster_7 = ThrusterAction(self, 6, 'T7')
        self.thruster_8 = ThrusterAction(self, 7, 'T8')

        self.thruster_publisher = internal_node.create_publisher(MotorMessages,"/provider_thruster/thruster_pwm", 10)
        #self.dry_test_publisher = rospy.Publisher("/telemetry/dry_run", Bool, queue_size=10, latch=True)
        #self.dry_test_service = rospy.ServiceProxy('/provider_thruster/dry_test', Empty)

        #self.dry_test_subscriber = rospy.Subscriber("/telemetry/dry_run", Bool, self._dry_run_callback)

        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.T1_T2.setEnabled(False)
        self.T3_T4.setEnabled(False)
        self.T5_T6.setEnabled(False)
        self.T7_T8.setEnabled(False)
        self.actionStart_test.setEnabled(False)

        self.pwms = [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]

    def _dry_run_callback(self, msg):
        if msg.data:
            self.enableButton.setEnabled(False)
            self.disableButton.setEnabled(True)
            self.T1_T2.setEnabled(True)
            self.T3_T4.setEnabled(True)
            self.T5_T6.setEnabled(True)
            self.T7_T8.setEnabled(True)
            self.resetPwmButton.setEnabled(True)
            self.actionStart_test.setEnabled(True)
        else:
            self.enableButton.setEnabled(True)
            self.disableButton.setEnabled(False)
            self.T1_T2.setEnabled(False)
            self.T3_T4.setEnabled(False)
            self.T5_T6.setEnabled(False)
            self.T7_T8.setEnabled(False)
            self.resetPwmButton.setEnabled(False)
            self.actionStart_test.setEnabled(False)
    
    def _handle_resetPwmButton_clicked(self, checked):
        self.pwms = [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
        self.send_pwms()
        self.thruster_1.handle_thruster_effort1500_clicked(None)
        self.thruster_2.handle_thruster_effort1500_clicked(None)
        self.thruster_3.handle_thruster_effort1500_clicked(None)
        self.thruster_4.handle_thruster_effort1500_clicked(None)
        self.thruster_5.handle_thruster_effort1500_clicked(None)
        self.thruster_6.handle_thruster_effort1500_clicked(None)
        self.thruster_7.handle_thruster_effort1500_clicked(None)
        self.thruster_8.handle_thruster_effort1500_clicked(None)

    def _handle_enableButton_clicked(self, checked):
        self.enableButton.setEnabled(False)
        self.disableButton.setEnabled(True)
        self.T1_T2.setEnabled(True)
        self.T3_T4.setEnabled(True)
        self.T5_T6.setEnabled(True)
        self.T7_T8.setEnabled(True)
        self.resetPwmButton.setEnabled(True)
        self.actionStart_test.setEnabled(True)
        self.dry_test_publisher.publish(data = True)

    def _handle_disableButton_clicked(self, checked):
        self.enableButton.setEnabled(True)
        self.disableButton.setEnabled(False)
        self.T1_T2.setEnabled(False)
        self.T3_T4.setEnabled(False)
        self.T5_T6.setEnabled(False)
        self.T7_T8.setEnabled(False)
        self.resetPwmButton.setEnabled(False)
        self.actionStart_test.setEnabled(False)
        self.dry_test_publisher.publish(data = False)

    def set_pwm(self, index, value):
        self.pwms[index] = value

    def send_pwms(self):
        self.thruster_publisher.publish(data = self.pwms)

    #def _handle_start_test_triggered(self):
        #newThread = Threads(self.dry_test_service)
        #newThread.start()

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog
#class Threads(threading.Thread):
    #def __init__(self, dryTestService):
        #super(Threads, self).__init__()
        #self.dryTestService = dryTestService
    
    #def run(self):
       # try:
            #self.dryTestService.call()
        #except rospy.ServiceException as e:
            #print(e)
            #rospy.logerr('Provider Thruster Node is not started')