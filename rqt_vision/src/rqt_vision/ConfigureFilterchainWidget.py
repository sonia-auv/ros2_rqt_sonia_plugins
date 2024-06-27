import os
import rospy
import rospkg

from functools import partial
from ament_index_python import get_package_share_directory
from python_qt_binding import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QCheckBox, QSlider,QSpinBox, QDoubleSpinBox, QLineEdit
from sonia_common.srv import GetInformationList, GetFilterchainFilter, GetFilterchainFilterAllParam, SetFilterchainFilterParam, ManageFilterchainFilter, SetFilterchainFilterObserver, SaveFilterchain, SetFilterchainFilterOrder


class ConfigureFilterchainWidget(QWidget):
    def __init__(self, execution_name,filterchain):
        super(ConfigureFilterchainWidget, self).__init__()
        try:
            rospy.wait_for_service('/proc_image_processing/get_information_list', timeout=2)
            rospy.wait_for_service('/proc_image_processing/get_filterchain_filter', timeout=2)
            rospy.wait_for_service('/proc_image_processing/get_filterchain_filter_all_param', timeout=2)
            rospy.wait_for_service('/proc_image_processing/set_filterchain_filter_param', timeout=2)
            rospy.wait_for_service('/proc_image_processing/manage_filterchain_filter', timeout=2)
            rospy.wait_for_service('/proc_image_processing/set_filterchain_filter_observer', timeout=2)
            rospy.wait_for_service('/proc_image_processing/save_filterchain', timeout=2)
            rospy.wait_for_service('/proc_image_processing/set_filterchain_filter_order', timeout=2)
        except rospy.ROSException:
            rospy.loginfo('Services unavailable')
        ui_file = os.path.join(get_package_share_directory('rqt_vision'), 'resource', 'filters_parameter.ui')
        loadUi(ui_file, self)
        self.setWindowTitle('Filters')

        self._current_filter = None
        self._current_execution_name = execution_name
        self._current_filterchain = filterchain.list
        self.filterchain_name.setText(self._current_filterchain)
        self._current_filter_to_add = None

        ##### Service
        
        self._srv_get_information_list = rospy.ServiceProxy('/proc_image_processing/get_information_list', GetInformationList)
        self._srv_get_filterchain_filter = rospy.ServiceProxy('/proc_image_processing/get_filterchain_filter', GetFilterchainFilter)
        self._srv_get_filterchain_filter_all_param = rospy.ServiceProxy('/proc_image_processing/get_filterchain_filter_all_param', GetFilterchainFilterAllParam)
        self._srv_set_filterchain_filter_param = rospy.ServiceProxy('/proc_image_processing/set_filterchain_filter_param', SetFilterchainFilterParam)
        self._srv_manage_filterchain_filter = rospy.ServiceProxy('/proc_image_processing/manage_filterchain_filter', ManageFilterchainFilter)
        self._srv_set_filterchain_filter_observer = rospy.ServiceProxy('/proc_image_processing/set_filterchain_filter_observer', SetFilterchainFilterObserver)
        self._srv_save_filterchain = rospy.ServiceProxy('/proc_image_processing/save_filterchain', SaveFilterchain)
        self._srv_set_filterchain_filter_order = rospy.ServiceProxy('/proc_image_processing/set_filterchain_filter_order', SetFilterchainFilterOrder)

        self.filters.itemSelectionChanged.connect(self.current_filter_index_changed)
        self.all_filters.currentIndexChanged[int].connect(self._current_filter_to_add_selection_changed)
        self.add_button.clicked.connect(self._handle_add_filter)
        self.delete_button.clicked.connect(self._handle_delete_filter)
        self.save_button.clicked.connect(self._handle_save_button)
        self.cancel_button.clicked.connect(self._handle_cancel_button)
        self.move_up_button.clicked.connect(self._handle_move_up_button)
        self.move_down_button.clicked.connect(self._handle_move_down_button)
        self.fill_filters_list()
        self.fill_all_filters()

    def fill_all_filters(self):
        self.all_filters.clear()
        try:
            all_filter = self._srv_get_information_list(4)
        except rospy.ServiceException as err:
            rospy.logerr(err)
        all_filter_list = all_filter.list.split(';')
        if len(all_filter_list) == 0:
            return
        for filter in sorted(all_filter_list):
            if len(filter) > 0:
                self.all_filters.addItem(filter)
        self._current_filter_to_add = all_filter_list[0]

    def _current_filter_to_add_selection_changed(self,index):
        self._current_filter_to_add = self.all_filters.itemText(index)

    def fill_filters_list(self):
        self._current_filter = None
        self.filters.clear()
        self.clear_parameters()
        self.move_up_button.setEnabled(False)
        self.move_down_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        try:
            filters_string = self._srv_get_filterchain_filter(self._current_execution_name, self._current_filterchain)
        except rospy.ServiceException as err:
            rospy.logerr(err)

        filters_list = filters_string.list.split(';')

        if len(filters_list) == 0:
            return
        for filter in filters_list:
            if len(filter) > 0:
                self.filters.addItem(filter)

    def current_filter_index_changed(self):
        if self.filters.currentRow() >= 0:
            self.delete_button.setEnabled(True)
            self.move_up_button.setEnabled(self.filters.currentRow() > 0)
            self.move_down_button.setEnabled(self.filters.currentRow() < self.filters.count() -1)
            filter = self.filters.currentItem()
            self._current_filter = filter.text()
            self.load_filter_parameter()
            try:
                self._srv_set_filterchain_filter_observer(self._current_execution_name, self._current_filterchain,
                                                          self._current_filter)
            except rospy.ServiceException as err:
                rospy.logerr(err)

    def load_filter_parameter(self):
        self.clear_parameters()

        try:
            all_param = self._srv_get_filterchain_filter_all_param(self._current_execution_name,self._current_filterchain,self._current_filter)
            params = all_param.list.split(';')
            for param_index, param in enumerate(params):
                param_tab = param.split('|')
                if len(param_tab) != 6:
                    continue
                param_name = param_tab[0]
                param_type = param_tab[1]
                param_value = param_tab[2]
                param_min = param_tab[3]
                param_max = param_tab[4]
                param_desc = param_tab[5]
                self._load_parameter(param_index,param_name, param_type,param_value,param_min, param_max, param_desc)
        except rospy.ServiceException as err:
            rospy.logerr(err)

    def clear_parameters(self):
        for label in self.parameters.findChildren(QLabel):
            label.setParent(None)
        for label in self.parameters.findChildren(QLineEdit):
                label.setParent(None)
        for label in self.parameters.findChildren(QSpinBox):
            label.setParent(None)
        for label in self.parameters.findChildren(QDoubleSpinBox):
            label.setParent(None)
        for label in self.parameters.findChildren(QCheckBox):
            label.setParent(None)
        for label in self.parameters.findChildren(QSlider):
            label.setParent(None)

    def _load_parameter(self,param_index,param_name, param_type,param_value, param_min, param_max, param_desc):
        x_check = 160
        x ,y ,w ,h = 4,4 + 40 * param_index,150,20
        self.parameters.resize(self.parameters.width(),h + y + 20)
        label = QLabel(param_name,self.parameters)
        label.setGeometry(x,y,w,h)
        label.setToolTip(param_desc)
        label.show()

        if param_type == 'Boolean':
            checkbox = QCheckBox('',self.parameters)
            checkbox.setGeometry(x_check,y,w,h)
            checkbox.setChecked(param_value == '1')
            checkbox.setToolTip(param_desc)
            checkbox.stateChanged.connect(partial(self._handle_bool_param_changed,param_name))
            checkbox.show()
        elif param_type == 'Integer':
            if len(param_min) > 0 and len(param_max) > 0 and int(param_max) < 5:
                slider = QSlider(Qt.Horizontal,self.parameters)
                slider.setMinimum(int(param_min))
                slider.setMaximum(int(param_max))
                slider.setValue(int(param_value))
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setGeometry(x_check,y,w,h)
                slider.setToolTip(param_desc)
                slider.setTickInterval(1)
                slider.setSingleStep(1)
                slider.setPageStep(1)
                slider.valueChanged.connect(partial(self._handle_param_changed,param_name))
                slider.show()
            else:
                spin = QSpinBox(self.parameters)
                if len(param_min) > 0:
                    spin.setMinimum(int(param_min))
                if len(param_max) > 0:
                    spin.setMaximum(int(param_max))
                spin.setValue(int(param_value))
                spin.setToolTip(param_desc)
                spin.setGeometry(x_check,y,w,h)
                spin.valueChanged.connect(partial(self._handle_param_changed,param_name))
                spin.show()
        elif param_type == 'Double':
            spin = QDoubleSpinBox(self.parameters)
            if len(param_min) > 0:
                spin.setMinimum(float(param_min))
            if len(param_max) > 0:
                spin.setMaximum(float(param_max))
            spin.setValue(float(param_value))
            spin.valueChanged.connect(partial(self._handle_param_changed,param_name))
            spin.setGeometry(x_check,y,w,h)
            spin.show()
        elif param_type == 'String':
            lineEdit = QLineEdit(self.parameters)
            lineEdit.setText(param_value)
            lineEdit.setToolTip(param_desc)
            lineEdit.setGeometry(x_check,y,w,h)
            lineEdit.textChanged.connect(partial(self._handle_param_changed,param_name))
            lineEdit.show()

        self.parameters.update()

    def _handle_param_changed(self,param_name,value):
        try:
            self._srv_set_filterchain_filter_param(self._current_execution_name,self._current_filterchain,self._current_filter,param_name,str(value))
        except rospy.ServiceException as err:
            rospy.logerr(err)

    def _handle_bool_param_changed(self,param_name,value):
        if bool(value):
            int_value = 1
        else:
            int_value = 0
        try:
            self._srv_set_filterchain_filter_param(self._current_execution_name,self._current_filterchain,self._current_filter,param_name,str(int_value))
        except rospy.ServiceException as err:
            rospy.logerr(err)

    def _handle_add_filter(self):
        if self._current_filter_to_add is None :
            return;
        try:
            self._srv_manage_filterchain_filter(self._current_execution_name,self._current_filterchain, self._current_filter_to_add, 1)
            self.fill_filters_list()
            self.filters.setCurrentRow(self.filters.count() -1)
        except rospy.ServiceException as err:
            rospy.logerr(err)

    def _handle_delete_filter(self):
        try:
            self._srv_manage_filterchain_filter(self._current_execution_name, self._current_filterchain, self._current_filter, 2)
            self.fill_filters_list()
        except rospy.ServiceException as err:
            rospy.logerr(err)

    def _handle_save_button(self):
        try:
            self._srv_save_filterchain(self._current_execution_name,self._current_filterchain,1)
        except rospy.ServiceException as err:
            rospy.logerr(err)

    def _handle_cancel_button(self):
        try:
            execution_string = self._srv_get_information_list(1)
        except rospy.ServiceException as err:
            rospy.logerr(err)
            self._srv_save_filterchain(self._current_execution_name,self._current_filterchain,2)
        self.fill_filters_list()

    def _handle_move_up_button(self):
        current_index = self.filters.currentRow()
        self._srv_set_filterchain_filter_order(self._current_execution_name,self._current_filterchain,current_index,1 )
        self.fill_filters_list()
        self.filters.setCurrentRow(current_index -1)

    def _handle_move_down_button(self):
        current_index = self.filters.currentRow()
        self._srv_set_filterchain_filter_order(self._current_execution_name,self._current_filterchain,current_index,2 )
        self.fill_filters_list()
        self.filters.setCurrentRow(current_index +1)

