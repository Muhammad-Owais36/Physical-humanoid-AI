# Data Model: ROS 2 Humanoid Nervous System

**Feature**: 001-ros2-humanoid-nervous-system
**Date**: 2025-12-15
**Purpose**: Define the conceptual data structures for ROS 2 communication and humanoid robot representation

## Entity: ROS 2 Communication Primitives

**Description**: Core concepts that enable distributed robot communication in ROS 2

### Node
- **Purpose**: Independent process that performs computation using ROS 2 client libraries
- **Attributes**:
  - node_name: string (unique identifier within the system)
  - namespace: string (optional hierarchical grouping)
  - parameters: key-value pairs for configuration
- **Relationships**: Contains publishers, subscribers, services, and actions
- **Validation**: Node name must be unique within namespace

### Topic
- **Purpose**: Asynchronous data stream using publish/subscribe pattern
- **Attributes**:
  - topic_name: string (unique identifier)
  - message_type: string (e.g., std_msgs/msg/String, sensor_msgs/msg/JointState)
  - qos_profile: Quality of Service settings (reliability, durability, etc.)
- **Relationships**: Connected to multiple publishers and subscribers
- **Validation**: Message type must conform to ROS 2 message specification

### Service
- **Purpose**: Synchronous request/response communication
- **Attributes**:
  - service_name: string (unique identifier)
  - service_type: string (e.g., std_srvs/srv/SetBool)
  - request_type: message definition for request
  - response_type: message definition for response
- **Relationships**: Connected to service clients and service servers
- **Validation**: Request/response types must be compatible

### Action
- **Purpose**: Goal-oriented communication for long-running tasks with feedback
- **Attributes**:
  - action_name: string (unique identifier)
  - action_type: string (e.g., example_interfaces/action/Fibonacci)
  - goal_type: message definition for goal
  - result_type: message definition for result
  - feedback_type: message definition for feedback
- **Relationships**: Connected to action clients and action servers
- **Validation**: All three message types must be properly defined

## Entity: Python AI Agent Interface

**Description**: Structure for connecting Python-based AI agents to ROS 2 controllers

### Publisher
- **Purpose**: Enables Python agents to send messages to ROS 2 topics
- **Attributes**:
  - topic_name: string (destination topic)
  - message_type: string (ROS 2 message type)
  - publisher_handle: internal reference to ROS 2 publisher
  - qos_profile: Quality of Service settings
- **Relationships**: Associated with a Node, sends to a Topic
- **Validation**: Message type must match the destination topic

### Subscriber
- **Purpose**: Enables Python agents to receive messages from ROS 2 topics
- **Attributes**:
  - topic_name: string (source topic)
  - message_type: string (ROS 2 message type)
  - callback_function: function to process received messages
  - subscriber_handle: internal reference to ROS 2 subscriber
- **Relationships**: Associated with a Node, receives from a Topic
- **Validation**: Callback function must be properly defined

### Service Client
- **Purpose**: Enables Python agents to call ROS 2 services
- **Attributes**:
  - service_name: string (destination service)
  - service_type: string (ROS 2 service type)
  - client_handle: internal reference to ROS 2 service client
- **Relationships**: Associated with a Node, calls a Service
- **Validation**: Service must be available before making calls

## Entity: Humanoid Robot Model

**Description**: Structure representation of a humanoid robot using URDF

### Link
- **Purpose**: Represents a rigid body in the robot structure
- **Attributes**:
  - link_name: string (unique identifier)
  - visual: visual representation (geometry, material, origin)
  - collision: collision representation (geometry, origin)
  - inertial: mass, inertia properties
- **Relationships**: Connected to other Links via Joints
- **Validation**: Must have valid geometry and proper physical properties

### Joint
- **Purpose**: Defines connection between two links with degrees of freedom
- **Attributes**:
  - joint_name: string (unique identifier)
  - joint_type: string (revolute, continuous, prismatic, fixed, etc.)
  - parent_link: string (name of parent link)
  - child_link: string (name of child link)
  - origin: position and orientation relative to parent
  - axis: rotation axis for revolute joints
  - limits: min/max position, velocity, effort for revolute/prismatic joints
- **Relationships**: Connects two Links in a parent-child relationship
- **Validation**: Joint type must be supported, limits must be physically reasonable

### Sensor
- **Purpose**: Represents sensor attached to a link
- **Attributes**:
  - sensor_name: string (unique identifier)
  - sensor_type: string (camera, imu, lidar, etc.)
  - parent_link: string (link to which sensor is attached)
  - origin: position and orientation relative to parent link
  - parameters: sensor-specific configuration
- **Relationships**: Attached to a Link
- **Validation**: Sensor parameters must be valid for the sensor type

## Entity: Motion Command

**Description**: Structure for commands sent from Python AI agents to robot controllers

### Joint Command
- **Purpose**: Commands for individual joints or groups of joints
- **Attributes**:
  - joint_names: array of strings (names of joints to control)
  - positions: array of floats (target positions in radians or meters)
  - velocities: array of floats (target velocities)
  - efforts: array of floats (target efforts/torques)
  - time_from_start: duration (time to reach target)
- **Relationships**: Sent via Publisher to joint controllers
- **Validation**: Arrays must be of equal length, values must be within joint limits

### Action Command
- **Purpose**: Higher-level commands for complex behaviors
- **Attributes**:
  - action_name: string (name of action server to call)
  - goal: structured data defining the goal
  - feedback_callback: function to handle feedback
  - result_callback: function to handle completion
- **Relationships**: Sent via Action Client to action servers
- **Validation**: Goal must conform to action server specification

## State Transitions

### Node State
- Uninitialized → Initialized (when node is created)
- Initialized → Active (when node starts processing)
- Active ↔ Error (when error occurs or is resolved)
- Active → Shutdown (when node is properly terminated)

### Communication State
- Disconnected → Connecting (when establishing connection)
- Connecting → Connected (when connection is established)
- Connected → Error (when communication error occurs)
- Error → Connected (when reconnection succeeds)
- Connected → Disconnected (when connection is closed)

This data model provides the conceptual foundation for understanding ROS 2 as the "nervous system" of humanoid robots, with clear relationships between communication primitives, AI agents, and robot structure.