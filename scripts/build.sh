#!/usr/bin/env bash

# Usage: ./scripts/build.sh [DOCKER_CI_DIR]

set -e
set -o pipefail

DOCKER_CI_DIR=$1

sudo apt update
sudo apt install -y ros-humble-std-srvs \
	ros-humble-tf-transformations \
	ros-humble-std-msgs ros-humble-rqt-gui \
	ros-humble-rclpy

source /opt/ros/humble/setup.bash

$DOCKER_CI_DIR/scripts/build.sh sonia_common_ros2

cd ros2_rqt_sonia_plugins

source /build/sonia_common_ros2/INSTALL_BASE/setup.sh

colcon build --cmake-force-configure --install INSTALL_BASE
