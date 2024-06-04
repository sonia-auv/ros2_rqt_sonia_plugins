import rospy
from tkinter import Tk
import tkinter.messagebox

class PowerCardButtonAction():
    def __init__(self, mainwindow, card_name):
        # self.slave_number = card_name
        self.mainwindow = mainwindow

        # self.result = 'no'

        # self.outdisable12 = eval('mainwindow.OutDisable12' + card_name)
        # self.outdisable12.setEnabled(False)
        # self.outdisable12.clicked.connect(self._handle_out_disable_12_clicked)

        # self.outdisable161 = eval('mainwindow.OutDisable161' + card_name)
        # self.outdisable161.setEnabled(False)
        # self.outdisable161.clicked.connect(self._handle_out_disable_16v1_clicked)

        # self.outdisable162 = eval('mainwindow.OutDisable162' + card_name)
        # self.outdisable162.setEnabled(False)
        # self.outdisable162.clicked.connect(self._handle_out_disable_16v2_clicked)

        # self.outenable12 = eval('mainwindow.OutEnable12' + card_name)
        # self.outenable12.setEnabled(True)
        # self.outenable12.clicked.connect(self._handle_out_enable_12_clicked)

        # self.outenable161 = eval('mainwindow.OutEnable161' + card_name)
        # self.outenable161.setEnabled(True)
        # self.outenable161.clicked.connect(self._handle_out_enable_16v1_clicked)

        # self.outenable162 = eval('mainwindow.OutEnable162' + card_name)
        # self.outenable162.setEnabled(True)
        # self.outenable162.clicked.connect(self._handle_out_enable_16v2_clicked)

        #self.manage_power_supply_srv = rospy.ServiceProxy('/provider_power/manage_power_supply_bus', ManagePowerSupplyBus)

    # def _handle_out_disable_12_clicked(self):
    #     root = Tk()
    #     root.withdraw()
    #     self.result = tkinter.tkmessagebox.askquestion("ATTENTION", 'Are you sure, this action should be shutdown PC!!')
    #     if self.result == 'yes':
    #         self.outenable12.setEnabled(True)
    #         self.outdisable12.setEnabled(False)
    #         self._set_bus_state(0, 0)
    #     pass

    # def _handle_out_disable_16v1_clicked(self):
    #     self.outenable161.setEnabled(True)
    #     self.outdisable161.setEnabled(False)
    #     self._set_bus_state(1, 0)
    #     pass

    # def _handle_out_disable_16v2_clicked(self):
    #     self.outenable162.setEnabled(True)
    #     self.outdisable162.setEnabled(False)
    #     self._set_bus_state(2, 0)
    #     pass

    # def _handle_out_enable_12_clicked(self):
    #     self.outdisable12.setEnabled(True)
    #     self.outenable12.setEnabled(False)
    #     self._set_bus_state(0, 1)
    #     pass

    # def _handle_out_enable_16v1_clicked(self):
    #     self.outdisable161.setEnabled(True)
    #     self.outenable161.setEnabled(False)
    #     self._set_bus_state(1, 1)
    #     pass

    # def _handle_out_enable_16v2_clicked(self):
    #     self.outdisable162.setEnabled(True)
    #     self.outenable162.setEnabled(False)
    #     self._set_bus_state(2, 1)
    #     pass

    def _set_bus_state(self, bus, state):
        try:
            self.manage_power_supply_srv(int(self.slave_number), bus, state)
        except rospy.ServiceException as e:
            rospy.logerr('Service call failed to manage bus')
