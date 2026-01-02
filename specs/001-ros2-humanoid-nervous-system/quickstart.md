# Quickstart: ROS 2 Humanoid Nervous System

**Feature**: 001-ros2-humanoid-nervous-system
**Date**: 2025-12-15

## Overview

This quickstart guide provides a hands-on introduction to ROS 2 as the "nervous system" of humanoid robots. You'll learn about ROS 2 communication primitives, connect Python AI agents to ROS controllers, and create a basic humanoid robot description using URDF.

## Prerequisites

- ROS 2 Humble Hawksbill installed (or Iron Irwini)
- Python 3.8 or higher
- Basic Python programming knowledge
- Familiarity with command line tools

## Setup

### 1. Verify ROS 2 Installation

```bash
# Check ROS 2 installation
source /opt/ros/humble/setup.bash  # or /opt/ros/iron/setup.bash
ros2 --version

# Check Python client library
python3 -c "import rclpy; print('rclpy available')"
```

### 2. Create a Workspace

```bash
mkdir -p ~/ros2_humanoid_ws/src
cd ~/ros2_humanoid_ws
colcon build
source install/setup.bash
```

## Chapter 1: ROS 2 Communication Primitives

### Understanding Nodes, Topics, Services, and Actions

ROS 2 uses a distributed architecture where different processes (nodes) communicate through:

1. **Nodes**: Independent processes that perform computation
2. **Topics**: Asynchronous publish/subscribe communication
3. **Services**: Synchronous request/response communication
4. **Actions**: Goal-oriented communication for long-running tasks

### Example: Simple Publisher/Subscriber

Create a simple publisher that sends "hello" messages:

```python
# publisher_example.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Run the publisher in one terminal:
```bash
python3 publisher_example.py
```

In another terminal, listen to the topic:
```bash
ros2 topic echo /topic std_msgs/msg/String
```

## Chapter 2: Connecting Python AI Agents with rclpy

### Creating the AI-to-ROS Bridge

Python AI agents can connect to ROS controllers using rclpy. Here's a simple example that demonstrates the bridge:

```python
# ai_ros_bridge.py
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import random

class AIBridge(Node):
    def __init__(self):
        super().__init__('ai_bridge')

        # Subscribe to sensor data
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.listener_callback,
            10)

        # Publisher for motion commands
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10)

        # Timer to send commands periodically
        self.timer = self.create_timer(1.0, self.send_motion_command)

        self.get_logger().info('AI Bridge initialized')

    def listener_callback(self, msg):
        self.get_logger().info(f'Received joint states: {msg.name}')

    def send_motion_command(self):
        # Create a simple motion command
        traj_msg = JointTrajectory()
        traj_msg.joint_names = ['joint1', 'joint2', 'joint3']  # Replace with actual joint names

        point = JointTrajectoryPoint()
        point.positions = [random.uniform(-1.0, 1.0) for _ in range(3)]
        point.velocities = [0.0] * 3
        point.time_from_start.sec = 1
        point.time_from_start.nanosec = 0

        traj_msg.points = [point]

        self.publisher.publish(traj_msg)
        self.get_logger().info(f'Sent motion command: {point.positions}')

def main(args=None):
    rclpy.init(args=args)
    ai_bridge = AIBridge()

    try:
        rclpy.spin(ai_bridge)
    except KeyboardInterrupt:
        pass
    finally:
        ai_bridge.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Run the AI bridge:
```bash
python3 ai_ros_bridge.py
```

## Chapter 3: Humanoid Robot Description using URDF

### Basic Humanoid URDF Structure

Here's a simple URDF file for a basic humanoid robot:

```xml
<!-- basic_humanoid.urdf -->
<?xml version="1.0"?>
<robot name="basic_humanoid">
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.2 0.1 0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.2 0.1 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0.0" ixz="0.0" iyy="0.01" iyz="0.0" izz="0.01"/>
    </inertial>
  </link>

  <!-- Head -->
  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
      <material name="white">
        <color rgba="1 1 1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.0005" ixy="0.0" ixz="0.0" iyy="0.0005" iyz="0.0" izz="0.0005"/>
    </inertial>
  </link>

  <joint name="head_joint" type="fixed">
    <parent link="base_link"/>
    <child link="head"/>
    <origin xyz="0 0 0.1" rpy="0 0 0"/>
  </joint>

  <!-- Left Arm -->
  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.2" radius="0.02"/>
      </geometry>
      <material name="red">
        <color rgba="1 0 0 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.2" radius="0.02"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.3"/>
      <inertia ixx="0.001" ixy="0.0" ixz="0.0" iyy="0.001" iyz="0.0" izz="0.0001"/>
    </inertial>
  </link>

  <joint name="left_shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.15 0 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>
</robot>
```

### Visualizing the URDF

To visualize your URDF in RViz:

```bash
# Launch robot state publisher
ros2 run robot_state_publisher robot_state_publisher --ros-args -p robot_description:='$(cat basic_humanoid.urdf)'

# Launch RViz
ros2 run rviz2 rviz2
```

In RViz, add a RobotModel display and set the Fixed Frame to "base_link".

## Running the Examples

1. Save the Python files in your workspace
2. Make sure your ROS 2 environment is sourced
3. Run each example in separate terminals
4. Use ROS 2 command-line tools to monitor communication:

```bash
# List active topics
ros2 topic list

# Echo messages on a topic
ros2 topic echo /topic std_msgs/msg/String

# List active nodes
ros2 node list
```

## Next Steps

After completing this quickstart, you should:
1. Understand how ROS 2 acts as the "nervous system" of humanoid robots
2. Know how to create Python agents that communicate with ROS controllers
3. Be able to create basic URDF files for humanoid robots
4. Explore more complex examples in the full educational content

This quickstart provides the foundation for the more detailed chapters that will expand on each of these concepts.