### Project Context: Autonomous Mobile Robot with Manipulator (ROS2)

**My Background:** 
I am a professional Java/Kotlin developer. I am a beginner in robotics and ROS2. I want to build this project with your guidance as an expert mentor. Please use analogies from the JVM world (Dependency Injection, Interfaces, Lifecycle) where appropriate to explain ROS2 concepts.

**Hardware Stack:**
- **SBC:** Orange Pi 5 Ultra (16GB RAM) — Running Ubuntu 22.04 & ROS2 Humble/Jazzy.
- **SBC:** Orange Pi 4 pro (12GB RAM) — Running Ubuntu 22.04 & ROS2 Humble/Jazzy.

- **Vision:** 
  1. Orbbec Astra S (Depth Camera) for point clouds and SLAM.
  2. MaixCam Pro (AI Camera) for edge-based object detection (YOLO).
- **Actuators:** 
  1. Keyestudio Tracked Platform (DC motors).
  2. Two servo for MaixCam Pro (for horizontal + vertical positioning)
- **Controllers:** Arduino Uno (as an I/O expander for servos and motor drivers).
- **Communication:** USB Serial, Bluetooth modules, signal wires GPIO.

**Goal:** 
Create a modular ROS2 project that integrates CV (object tracking) and a mobile base.

**Your Task:**
1. Propose a **WorkSpace Structure** (folder hierarchy) according to ROS2 best practices.
2. Design a **High-Level Architecture**: 
   - Which nodes should be in C++ (for performance) and which in Python (for CV/Logic)?
   - How should the 'Brain' (Orange Pi) communicate with 'Muscles' (Arduino)? (Recommend: micro-ROS vs Serial Bridge).
3. Suggest a **Communication Graph**: Define key Topics, Services, and Action servers.
4. Explain how to integrate **MoveIt2** for the arm and **Nav2** for the base given my hardware.

**Format:** 
Provide a clear file tree, a list of suggested ROS2 packages, and a step-by-step roadmap for implementation.

**Language Preference:**
Пожалуйста, веди весь наш дальнейший диалог на РУССКОМ языке. 
Объясняй технические термины ROS2, сохраняя их оригинальные названия (например, "Nodes", "Topics", "Action Servers"), но давай подробные комментарии к коду и архитектуре на русском языке.

