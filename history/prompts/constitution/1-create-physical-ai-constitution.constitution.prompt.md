---
id: 1
title: Create-Physical-AI-Constitution
stage: constitution
date: 2025-12-15
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: /sp.constitution
labels: [constitution,physical-ai,robotics]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Project: Physical AI & Humanoid Robotics – AI Systems in the Physical World

Core principles:

Accuracy: All technical claims (robotics, sensors, physics, AI methods) must be verified with primary sources or official documentation.

Clarity: Suitable for readers with robotics, AI, or computer science background.

Reproducibility: Methods and experiments in Gazebo, Unity, ROS 2, and NVIDIA Isaac must be traceable and explainable.

Rigor: Prefer peer-reviewed papers, official technical documentation, and authoritative robotics resources.

Key standards:

All factual claims must cite sources (journals, conference papers, official docs).

Citation format: APA style.

Minimum 50% of sources must be peer-reviewed.

Plagiarism tolerance: 0% before submission.

Writing clarity: Flesch-Kincaid grade 10–12.

Constraints:

Word count: 5,000–7,000 words

Minimum 15 sources

Format: PDF with embedded citations

Success criteria:

All claims verified against sources

Zero plagiarism detected

Passes fact-checking review

Reader can understand the bridge between AI algorithms and physical robot behavior, including sensors, physics simulations, and humanoid control

Module-based focus (for chapters):

Module 1: The Robotic Nervous System (ROS 2)

Focus: Middleware for robot control

ROS 2 nodes, topics, and services

Python agent integration with ROS controllers via rclpy

URDF modeling for humanoid robots

Module 2: The Digital Twin (Gazebo & Unity)

Focus: Physics simulation and environment building

Simulating physics, gravity, and collisions in Gazebo

High-fidelity rendering and human-robot interaction in Unity

Sensor simulation: LiDAR, Depth Cameras, IMUs

Module 3: The AI-Robot Brain (NVIDIA Isaac™)

Focus: Advanced perception and training

Photorealistic simulation and synthetic data generation in Isaac Sim

Hardware-accelerated VSLAM and navigation via Isaac ROS

Nav2 path planning for bipedal humanoid robots

Module 4: Vision-Language-Action (VLA)

Focus: Integrating LLMs with robotics for cognitive planning

Voice-to-Action commands with OpenAI Whisper

Translating natural language into ROS 2 action sequences

Capstone: Autonomous humanoid performing object recognition, navigation, and manipulation based on voice commands

Not building:

Full implementation of unrelated AI algorithms outside Physical AI

Ethical or societal impact discussion (separate paper)

Commercial robotics product comparisons

Low-level hardware programming details

## Response snapshot

Created a comprehensive constitution file for the Physical AI & Humanoid Robotics project based on the user's specifications. The constitution includes:

1. Core principles focusing on accuracy, clarity, reproducibility, rigor, citation integrity, and modularity
2. Additional standards and constraints covering documentation requirements, module-based development focus, and technology stack requirements
3. Development workflow and quality standards with fact-checking, success criteria, and prohibited activities
4. Governance section outlining compliance requirements

The constitution addresses all four modules: ROS 2 as the robotic nervous system, simulation environments (Gazebo & Unity) as the digital twin, NVIDIA Isaac as the AI-robot brain, and Vision-Language-Action integration. It incorporates requirements for peer-reviewed sources, APA citations, and technical accuracy while maintaining focus on physical AI applications.

## Outcome

- ✅ Impact: Created foundational governance document for Physical AI & Robotics project
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md created
- 🔁 Next prompts: Module-specific specs for ROS 2, simulation, Isaac, and VLA
- 🧠 Reflection: Constitution provides clear guidelines for technical accuracy and reproducibility in robotics research

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS - all requirements met
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin module-specific feature specifications