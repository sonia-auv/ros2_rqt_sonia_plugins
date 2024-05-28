import time

class ThrusterAction():
    def __init__(self, mainwindow, thruster_unique_id, thrusterName):
        self.thruster_id = thruster_unique_id
        self.thrusterName = thrusterName
        self.mainwindow = mainwindow

        eval('mainwindow.' + thrusterName + '_effort1100.clicked[bool]').connect(self._handle_thruster_effort1100_clicked)
        eval('mainwindow.' + thrusterName + '_effort1300.clicked[bool]').connect(self._handle_thruster_effort1300_clicked)
        eval('mainwindow.' + thrusterName + '_effort1500.clicked[bool]').connect(self.handle_thruster_effort1500_clicked)
        eval('mainwindow.' + thrusterName + '_effort1700.clicked[bool]').connect(self._handle_thruster_effort1700_clicked)
        eval('mainwindow.' + thrusterName + '_effort1900.clicked[bool]').connect(self._handle_thruster_effort1900_clicked)

        eval('mainwindow.' + thrusterName + 'Slider.valueChanged').connect(self._handle_thruster_slider_valueChanged)

    def _handle_thruster_effort1100_clicked(self, checked):
        self._update_speed_slider(1100)

    def _handle_thruster_effort1300_clicked(self, checked):
        self._update_speed_slider(1300)

    def handle_thruster_effort1500_clicked(self, checked):
        self._update_speed_slider(1500)

    def _handle_thruster_effort1700_clicked(self, checked):
        self._update_speed_slider(1700)

    def _handle_thruster_effort1900_clicked(self, checked):
        self._update_speed_slider(1900)

    def _handle_thruster_slider_valueChanged(self):
        value = eval('self.mainwindow.' + self.thrusterName + 'Slider.value()')
        self.mainwindow.set_pwm(self.thruster_id, value)
        self._update_speed_text(value)
        self.mainwindow.send_pwms()

    def _update_speed_text(self, value):
        eval('self.mainwindow.' + self.thrusterName + 'Speed').setText(str(value))

    def _update_speed_slider(self, value):
        eval('self.mainwindow.' + self.thrusterName + 'Slider').setValue(value)
