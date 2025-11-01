# ros2_rqt_sonia_plugins

*description*

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

* `ament_cmake`
* `rclcpp`
* `std_msgs`
* `std_srvs`

### Sonia packages

* `sonia_common_cpp`

### External packages

* `Boost`

---

## Build Instructions
To build the project, the following commands should be run directly from your ROS2 workspace.

```bash
colcon build --packages-select depth_port_manager --symlink-install
source install/setup.bash
```

---

## Launch Instructions

### Default launch

```bash
rqt
```
Note: if a new plugin is added, the command requires a parameter to fetch the new additions `rqt --force-discover`

---

## References

* [sonia_common_ros2](https://github.com/sonia-auv/sonia_common_ros2)

---