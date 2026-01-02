# ROS 2 Communication Contracts

**Feature**: 001-ros2-humanoid-nervous-system
**Date**: 2025-12-15
**Purpose**: Define the interface contracts for ROS 2 communication primitives used in humanoid robot systems

## Contract: Node Interface

**Purpose**: Standard interface for ROS 2 nodes in humanoid robot systems

### Node Creation
- **Method**: `rclpy.create_node(node_name, namespace=None, ...)`
- **Parameters**:
  - `node_name`: string, unique identifier for the node
  - `namespace`: string, optional hierarchical grouping (default: "")
- **Returns**: Node object with standard ROS 2 interfaces
- **Preconditions**: ROS 2 context must be initialized
- **Postconditions**: Node is registered with ROS 2 graph and can create publishers/subscribers

### Node Lifecycle
- **Initialization**: Node becomes active and can communicate
- **Shutdown**: Node cleanly disconnects from ROS 2 graph
- **Error handling**: Node handles shutdown gracefully on exception

## Contract: Publisher Interface

**Purpose**: Interface for publishing messages to ROS 2 topics from Python agents

### Publisher Creation
- **Method**: `node.create_publisher(msg_type, topic_name, qos_profile)`
- **Parameters**:
  - `msg_type`: message type (e.g., std_msgs.msg.String)
  - `topic_name`: string, name of the topic to publish to
  - `qos_profile`: Quality of Service settings
- **Returns**: Publisher object
- **Preconditions**: Valid message type and topic name
- **Postconditions**: Publisher can send messages to the topic

### Publish Operation
- **Method**: `publisher.publish(message)`
- **Parameters**: `message`: instance of msg_type
- **Returns**: None
- **Preconditions**: Valid message instance matching msg_type
- **Postconditions**: Message is sent to topic according to QoS settings

## Contract: Subscriber Interface

**Purpose**: Interface for subscribing to ROS 2 topics in Python agents

### Subscriber Creation
- **Method**: `node.create_subscription(msg_type, topic_name, callback, qos_profile)`
- **Parameters**:
  - `msg_type`: message type (e.g., sensor_msgs.msg.JointState)
  - `topic_name`: string, name of the topic to subscribe to
  - `callback`: function to handle received messages
  - `qos_profile`: Quality of Service settings
- **Returns**: Subscriber object
- **Preconditions**: Valid message type and topic name
- **Postconditions**: Callback will be invoked when messages arrive

### Message Handling
- **Callback signature**: `callback(msg)`
- **Parameters**: `msg`: instance of msg_type
- **Returns**: None
- **Preconditions**: Message received from topic
- **Postconditions**: Application logic processes the message

## Contract: Service Client Interface

**Purpose**: Interface for calling ROS 2 services from Python agents

### Client Creation
- **Method**: `node.create_client(srv_type, srv_name)`
- **Parameters**:
  - `srv_type`: service type (e.g., std_srvs.srv.SetBool)
  - `srv_name`: string, name of the service to call
- **Returns**: Client object
- **Preconditions**: Valid service type and name
- **Postconditions**: Client can make service calls

### Service Call
- **Method**: `client.call(request)`
- **Parameters**: `request`: instance of service request type
- **Returns**: Response object
- **Preconditions**: Service server is available
- **Postconditions**: Request processed, response received

## Contract: Action Client Interface

**Purpose**: Interface for using ROS 2 actions from Python agents

### Action Client Creation
- **Method**: `node.create_action_client(action_type, action_name)`
- **Parameters**:
  - `action_type`: action type (e.g., example_interfaces.action.Fibonacci)
  - `action_name`: string, name of the action server
- **Returns**: Action client object
- **Preconditions**: Valid action type and name
- **Postconditions**: Client can send goals to action server

### Goal Execution
- **Method**: `action_client.send_goal(goal, feedback_callback=None, result_callback=None)`
- **Parameters**:
  - `goal`: instance of action goal type
  - `feedback_callback`: optional function for feedback
  - `result_callback`: function for result handling
- **Returns**: Future object for goal handle
- **Preconditions**: Action server is available
- **Postconditions**: Goal sent, feedback and result callbacks may be invoked

## Contract: Humanoid Robot State Interface

**Purpose**: Standardized interface for humanoid robot state messages

### Joint State Message
- **Type**: `sensor_msgs.msg.JointState`
- **Fields**:
  - `header`: std_msgs.msg.Header (timestamp and frame)
  - `name`: array of strings (joint names)
  - `position`: array of floats (joint positions in radians)
  - `velocity`: array of floats (joint velocities)
  - `effort`: array of floats (joint efforts/torques)
- **Validation**: Arrays must be of equal length, joint names must be valid

### Joint Trajectory Message
- **Type**: `trajectory_msgs.msg.JointTrajectory`
- **Fields**:
  - `header`: std_msgs.msg.Header
  - `joint_names`: array of strings (names of joints to control)
  - `points`: array of JointTrajectoryPoint
- **Validation**: Joint names must exist on robot, trajectory points must be valid

### Joint Trajectory Point
- **Type**: `trajectory_msgs.msg.JointTrajectoryPoint`
- **Fields**:
  - `positions`: array of floats (target positions)
  - `velocities`: array of floats (target velocities)
  - `accelerations`: array of floats (target accelerations)
  - `time_from_start`: builtin_interfaces.msg.Duration
- **Validation**: Arrays must match joint_names length, values within joint limits

## Quality of Service (QoS) Profiles

### Default Profile
- **Reliability**: Best effort for sensor data, reliable for commands
- **Durability**: Volatile
- **History**: Keep last N messages (N=10 for most cases)

### Sensor Data Profile
- **Reliability**: Best effort (may drop messages)
- **History**: Keep last N messages (N=1 for real-time sensors)

### Command Profile
- **Reliability**: Reliable (ensure delivery)
- **History**: Keep last 1 message
- **Durability**: Transient local (for latched topics)

These contracts define the standardized interfaces for ROS 2 communication in humanoid robot systems, ensuring interoperability between different components of the "nervous system".