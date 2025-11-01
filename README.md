# ros2_rqt_sonia_plugins

The project provides sonia's custom made **RQT** plugins used to operate the **AUV** prototypes.

---

## rqt_actuator

### Registered Topics / Services / Actions

| Type                  | Name                               | Direction       | Message/Service Type                    | Description                        |
| --------------------- | ---------------------------------- | ----------------| --------------------------------------- | ---------------------------------- |
| Service               | `/provider_actuator/do_action`     | Client Server   | `sonia_common_ros2/srv/ActuatorService` | The service triggers an actuator   |

---

## rqt_depth_indicator

### Registered Topics / Services / Actions

| Type                             | Name                      | Direction       | Message/Service Type    | Description                                 |
| -------------------------------- | ------------------------- | ----------------| ----------------------- | ------------------------------------------- |
| Topic                            | `/provider_depth/depth`   | Subscribed      | `std_msgs/msg/Float32`  | Measured depth data                         |

---

## rqt_dvl

---

## rqt_power

The `rqt_power` .

### Registered Topics / Services / Actions

| Type          | Name                                    | Direction        | Message/Service Type                         | Description                                |
| ------------- | --------------------------------------- | ---------------- | -------------------------------------------- | ------------------------------------------ |
| Topic         | `/provider_power/battery_voltages`      | Subscribed       | `sonia_common_ros2/msg/BatteryPowerMessages` | The measured battery voltages              |
| Topic         | `/provider_power/battery_temperatures`  | Subscribed       | `sonia_common_ros2/msg/BatteryPowerMessages` | The measured battery temperatures          |
| Topic         | `/provider_power/battery_currents`      | Subscribed       | `sonia_common_ros2/msg/BatteryPowerMessages` | The measured battery currents              |
| Topic         | `/provider_power/motor_voltages`        | Subscribed       | `sonia_common_ros2/msg/MotorPowerMessages`   | The measured motor voltages                |
| Topic         | `/provider_power/motor_temperatures`    | Subscribed       | `sonia_common_ros2/msg/MotorPowerMessages`   | The measured motor temperatures            |
| Topic         | `/provider_power/motor_currents`        | Subscribed       | `sonia_common_ros2/msg/MotorPowerMessages`   | The measured motor currents                |
| Topic         | `/provider_power/motor_feedback`        | Subscribed       | `sonia_common_ros2/msg/MotorFeedback`        | Feedback of the motors state               |
| Topic         | `/provider_power/activate_motors`       | Published        | `std_msgs/msg/Bool`                          | Request to activate/deactivate the motors  |

---

## rqt_thruster_control

The `rqt_thruster_control` plugin provides a graphical interface for monitoring and commanding the AUV’s thrusters during testing and operation.

### Registered Topics / Services / Actions

| Type          | Name                                    | Direction       | Message/Service Type                         | Description                                |
| ------------- | --------------------------------------- | --------------- | -------------------------------------------- | ------------------------------------------ |
| Topic         | `/provider_thruster/thruster_pwm`       | Published       | `sonia_common_ros2/msg/MotorPwm`             | Controls the PWM of the motors             |
| Topic         | `/telemetry/dry_run`                    | Published       | `std_msgs/msg/Bool`                          | States if a dry test is picked or not      |

---

## rqt_thruster_effort

### Registered Topics / Services / Actions

| Type          | Name                                    | Direction       | Message/Service Type                    | Description                                       |
| ------------- | --------------------------------------- | --------------- | --------------------------------------- | ------------------------------------------------- |
| Topic         | `/provider_thruster/thruster_pwm`       | Subscribed      | `sonia_common_ros2/msg/MotorPwm`        | Controls the PWM of the motors                    |
| Topic         | `/telemetry/thruster_newton `           | Subscribed      | `std_msgs/msg/Int8MultiArray`           | Contains measured Newton force from the thrusters |

---

## rqt_toolbar

## Registered Topics / Services / Actions

### RS485

| Type                  | Name                             | Direction       | Message/Service Type                    | Description                        |
| --------------------- | -------------------------------- | ----------------| --------------------------------------- | ---------------------------------- |
| Topic                 | `/provider_rs485/mission_status` | Subscribed      | `sonia_common_ros2/msg/KillStatus`      | The status of the mission switch   |
| Topic                 | `/provider_rs485/kill_status`    | Subscribed      | `sonia_common_ros2/msg/MissionStatus`   | The status of the kill switch      |
---

## rqt_waypoint


| Service                          | `/provider_depth/tare`    | Client Server   | `std_srvs/srv/Trigger`  | Resets the depth sensor to current position |
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