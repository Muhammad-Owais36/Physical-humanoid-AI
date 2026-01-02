---
sidebar_position: 3
title: Troubleshooting
---

# Troubleshooting Guide

This guide provides solutions to common issues encountered when working with Physical AI & Humanoid Robotics systems.

## ROS 2 Issues

### Nodes not communicating across machines

**Problem**: ROS 2 nodes on different machines cannot discover each other.

**Solutions**:
1. Check network connectivity: `ping <other_machine_ip>`
2. Verify ROS_DOMAIN_ID is the same on both machines: `echo $ROS_DOMAIN_ID`
3. Check firewall settings - ensure ports 11811-11911 are open
4. Set RMW_IMPLEMENTATION if using specific middleware: `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`
5. Try setting ROS_LOCALHOST_ONLY=0 if using localhost: `export ROS_LOCALHOST_ONLY=0`

### High latency in message transmission

**Problem**: Messages are experiencing significant delay.

**Solutions**:
1. Check network bandwidth and congestion
2. Use QoS settings appropriate for your use case:
   ```bash
   # For real-time systems, use reliable QoS
   ros2 topic echo /topic_name --qos-reliability reliable --qos-durability transient_local
   ```
3. Monitor CPU and memory usage on publisher/subscriber nodes
4. Consider using intraprocess communication for nodes in the same process

### Service calls timing out

**Problem**: ROS 2 service calls are failing with timeout errors.

**Solutions**:
1. Verify the service server is running: `ros2 service list`
2. Check if the service name matches exactly
3. Ensure both client and server use compatible message types
4. Increase timeout values if the service takes longer to process
5. Check for network issues if client and server are on different machines

## Simulation Issues

### Gazebo simulation running slowly

**Problem**: Gazebo simulation has low frame rate or poor performance.

**Solutions**:
1. Reduce the complexity of models in the simulation environment
2. Adjust physics parameters in the world file:
   ```xml
   <physics type="ode">
     <max_step_size>0.01</max_step_size>  <!-- Increase for better performance -->
     <real_time_update_rate>100</real_time_update_rate>  <!-- Reduce for better performance -->
   </physics>
   ```
3. Disable unnecessary sensors or reduce their update rates
4. Use simpler collision models instead of visual models where possible
5. Check system resources and close other applications if needed

### Robot falling through the ground

**Problem**: Robot model falls through the ground plane in simulation.

**Solutions**:
1. Check if the ground plane model is properly defined with static="true"
2. Verify collision properties are properly defined in the URDF
3. Check physics engine parameters (step size, solver iterations)
4. Ensure the robot's center of mass is properly calculated
5. Verify that the robot model has proper collision geometry

### Sensors returning incorrect data

**Problem**: Camera, LiDAR, or other sensors return unexpected values.

**Solutions**:
1. Check sensor configuration in the URDF/URDF.xacro file
2. Verify sensor mounting position and orientation
3. Check sensor parameters like range, resolution, noise parameters
4. Validate that the sensor plugin is loaded correctly
5. Test sensor in isolation before integrating with the full robot

## NVIDIA Isaac Issues

### Isaac Sim not launching

**Problem**: NVIDIA Isaac Sim fails to start or crashes immediately.

**Solutions**:
1. Verify GPU compatibility and drivers: `nvidia-smi`
2. Check CUDA version compatibility with Isaac Sim
3. Ensure sufficient VRAM is available
4. Verify Isaac Sim installation and dependencies
5. Check system requirements are met (RAM, storage, etc.)

### Perception pipeline not detecting objects

**Problem**: Isaac ROS perception nodes fail to detect objects in images.

**Solutions**:
1. Verify camera calibration parameters are correct
2. Check that input image topics are being published
3. Validate that perception model files are properly loaded
4. Check lighting conditions in the environment
5. Verify image format and encoding match expectations
6. Adjust detection thresholds if necessary

### High GPU memory usage

**Problem**: GPU memory consumption is excessive during operation.

**Solutions**:
1. Reduce image resolution or sensor update rates
2. Use smaller neural network models if available
3. Implement proper memory management in your code
4. Monitor GPU memory usage: `nvidia-smi -l 1`
5. Consider using model quantization to reduce memory footprint

## Control Issues

### Robot joints moving erratically

**Problem**: Robot joints exhibit unstable or oscillating behavior.

**Solutions**:
1. Check controller parameters (PID gains) - they may be too high
2. Verify that the robot's dynamic parameters (mass, inertia) are correct
3. Check for sensor noise or delay that might affect control
4. Ensure control loop runs at consistent frequency
5. Verify that joint limits are properly set

### Robot losing balance during walking

**Problem**: Humanoid robot cannot maintain balance during locomotion.

**Solutions**:
1. Verify center of mass calculation and sensor calibration
2. Check balance controller parameters
3. Validate that ZMP (Zero-Moment Point) is within support polygon
4. Check if control frequency is adequate for balance
5. Verify that the robot model accurately represents the physical robot

### Inverse kinematics failing to find solution

**Problem**: IK solver cannot find joint angles for desired end-effector pose.

**Solutions**:
1. Verify the target pose is within the robot's reachable workspace
2. Check if joint limits are too restrictive
3. Use different IK solver parameters or algorithm
4. Consider using redundant DOFs if available
5. Verify URDF kinematic chain is properly defined

## Build and Installation Issues

### Package installation failures

**Problem**: ROS 2 packages fail to install or build.

**Solutions**:
1. Update package lists: `sudo apt update` (Ubuntu) or equivalent
2. Check for dependency conflicts
3. Verify ROS 2 distribution and package compatibility
4. Try installing packages individually instead of all at once
5. Check disk space and permissions

### CMake build errors

**Problem**: C++ packages fail to build with CMake errors.

**Solutions**:
1. Verify all required dependencies are installed
2. Check CMake version compatibility
3. Clean build directory and rebuild: `rm -rf build/ install/ log/ && colcon build`
4. Check for missing header files or libraries
5. Verify compiler compatibility and flags

## Performance Issues

### High CPU usage

**Problem**: Robot software consumes excessive CPU resources.

**Solutions**:
1. Profile code to identify bottlenecks: `htop`, `perf`, or ROS 2 tools
2. Optimize algorithms and data structures
3. Reduce update rates for non-critical processes
4. Use multithreading where appropriate
5. Consider hardware upgrade if software optimization is insufficient

### Memory leaks

**Problem**: Memory usage increases over time.

**Solutions**:
1. Use memory profiling tools: `valgrind`, `heaptrack`
2. Ensure proper cleanup of dynamically allocated memory
3. Check for circular references in object management
4. Monitor memory usage: `ros2 lifecycle list` for lifecycle nodes
5. Implement proper node cleanup and shutdown procedures

## Debugging Strategies

### Enable detailed logging

Add logging to your nodes for debugging:
```cpp
RCLCPP_INFO(get_logger(), "Processing data: %f", value);
RCLCPP_DEBUG(get_logger(), "Detailed debug info");
RCLCPP_ERROR(get_logger(), "Error occurred: %s", error_msg);
```

### Use ROS 2 tools for diagnosis

```bash
# Check system status
ros2 topic list
ros2 node list
ros2 lifecycle list

# Monitor topics
ros2 topic echo /topic_name
ros2 topic info /topic_name

# Analyze performance
ros2 bag record /topic_name
ros2 run topic_tools relay /input_topic:=/output_topic
```

### Visualization for debugging

Use RViz2 to visualize robot state, sensor data, and trajectories:
1. Load appropriate display configurations
2. Monitor TF frames to verify transforms
3. Visualize sensor data (point clouds, images, etc.)
4. Check robot model and joint states

## Hardware-Specific Issues

### Sensor calibration problems

**Problem**: Physical sensors don't match simulation data.

**Solutions**:
1. Perform proper sensor calibration procedures
2. Verify mounting positions and orientations
3. Check for sensor drift and environmental effects
4. Validate sensor data against known references
5. Implement runtime calibration if needed

### Actuator limitations

**Problem**: Robot joints cannot achieve desired positions/speeds.

**Solutions**:
1. Check joint limits and actuator capabilities
2. Verify power supply adequacy
3. Consider dynamic limitations (acceleration, jerk)
4. Implement smooth trajectory generation
5. Check for mechanical binding or wear

## Getting Additional Help

If the above solutions don't resolve your issue:

1. Search the ROS 2 Answers forum: https://answers.ros.org/
2. Check the NVIDIA Isaac forums: https://forums.developer.nvidia.com/
3. Look for similar issues in GitHub repositories
4. Create a minimal reproducible example to isolate the problem
5. Provide detailed information including error messages, system configuration, and steps to reproduce