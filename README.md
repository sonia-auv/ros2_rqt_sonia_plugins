# ros2_rqt_sonia_plugins

The project provides custom made **RQT** plugins used to operate the prototype.

---

## rqt_actuator

---

## rqt_depth_indicator

---

## rqt_dvl

---

## rqt_power

---

## rqt_thruster_control

---

## rqt_thruster_effort

---

## rqt_toolbar

---

## rqt_waypoint

---

## Dependencies

### ROS 2 Distro

* Humble

### ROS 2 Packages

* `ament_python`
* `rclpy`
* `rqt_gui`
* `std_msgs`
* `std_srvs`

### Sonia packages

* `sonia_common_ros2`

---

## Build Instructions
To build all the plugins within the project, the following commands should be run directly from your ROS2 workspace.

```bash
colcon build --paths src/ros2_rqt_sonia_plugins/* --symlink-install
source install/setup.bash
```

---

## Launch Instructions

### Default launch

```bash
rqt
```
Note: if a new plugin is added, the command requires a parameter to fetch the new additions `rqt --force-discover`.

---

## References

* [sonia_common_ros2](https://github.com/sonia-auv/sonia_common_ros2)

---