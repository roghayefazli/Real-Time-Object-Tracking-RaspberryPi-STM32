# Real-Time-Object-Tracking-RaspberryPi-STM32

# 🎯 Real-Time Human Tracking and Distance Estimation using YOLOv8-Seg on Raspberry Pi 5

A real-time embedded AI system that detects, segments, and tracks humans using **YOLOv8-Seg** on a **Raspberry Pi 5**, estimates the person's distance from the camera, and communicates motion commands to an **STM32 microcontroller** via UART.

This project combines Computer Vision, Embedded AI, Robotics, and Real-Time Systems into a complete autonomous tracking framework.

---

# 📌 Project Overview

The system continuously captures video from a Raspberry Pi Camera, detects human instances using YOLOv8 segmentation, computes the person's centroid, estimates the distance to the camera, and sends navigation commands to an STM32 controller.

The project is designed for robotic navigation, autonomous vehicles, and smart surveillance applications.

---

# 🚀 Features

- ✅ Real-time human detection
- ✅ Instance segmentation
- ✅ Human centroid estimation
- ✅ Distance estimation
- ✅ Bounding box visualization
- ✅ Segmentation mask visualization
- ✅ Raspberry Pi Camera support
- ✅ UART communication with STM32
- ✅ Real-time FPS monitoring

---

# 🧠 System Pipeline

```
        Raspberry Pi Camera
                 │
                 ▼
          YOLOv8 Segmentation
                 │
                 ▼
          Human Detection
                 │
                 ▼
       Centroid Calculation
                 │
                 ▼
      Distance Estimation
                 │
                 ▼
       UART Communication
                 │
                 ▼
             STM32 Robot
```

---


# ⚙️ Algorithm

1. Capture frames using PiCamera2.
2. Detect humans using YOLOv8-Seg.
3. Extract the segmentation mask.
4. Compute the centroid of the detected person.
5. Estimate the person's distance from the camera.
6. Display detection results.
7. Send navigation commands to STM32 through UART.

---

# 🛠 Technologies

- Python
- PyTorch
- YOLOv8-Seg
- OpenCV
- NumPy
- Raspberry Pi 5
- PiCamera2
- STM32
- UART Communication

---

# 📊 Output

The application displays:

- Human segmentation mask
- Bounding box
- Human centroid
- Estimated distance
- Current FPS
- UART commands

---

# Installation

```bash
git clone https://github.com/roghayefazli/Real-Time-Human-Tracking-RaspberryPi.git

cd Real-Time-Human-Tracking-RaspberryPi

pip install -r requirements.txt
```

---

# Example Output



<img width="50%" alt="Screenshot 2026-06-28 at 10 19 21 AM" src="https://github.com/user-attachments/assets/fae01e3a-0920-4bc6-945c-def292c5c05e" />

<img width="50%" alt="Screenshot 2026-06-28 at 10 22 29 AM" src="https://github.com/user-attachments/assets/cf021c13-10f0-48f8-8e8b-114425ee896a" />

---

# Future Improvements

- DeepSORT Tracking
- ByteTrack Integration
- TensorRT Optimization
- ROS2 Integration
- Multi-person Tracking
- NVIDIA Jetson Deployment
- Stereo Camera Support

---


# Author

**Roghayeh Fazli**

GitHub: https://github.com/roghayefazli
