# Edge AI Face Recognition Attendance System

A production-quality, fully offline face recognition attendance system designed for Jetson Nano deployment.
Features a modern CustomTkinter dashboard and an InsightFace-powered recognition pipeline.

## Features
- **Modern UI**: CustomTkinter dashboard with analytics and live camera feeds.
- **Robust Registration**: Captures 10 pose-guided face samples and averages them for high accuracy.
- **Stability Timer**: Prevents false positive attendance from people walking past quickly in the background.
- **Fully Offline**: Models run completely offline (after initial download).
- **TensorRT Ready**: Simply change the execution provider in `config.yaml` to run on Jetson Nano GPUs.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download Models (First time only, requires internet)**:
   ```bash
   python scripts/download_models.py
   ```
   *Note: This will download the InsightFace `buffalo_l` pack (~300MB) to the `models/` directory.*

3. **Run the Application**:
   ```bash
   python main.py
   ```

## Configuration
Edit `config/config.yaml` to tune settings:
- Camera index and resolution
- Detection & recognition thresholds
- Number of registration samples
- Jetson Nano deployment (change `providers` to `["TensorrtExecutionProvider", "CUDAExecutionProvider"]`)

## Jetson Nano Deployment
This system is architected for zero-code-change deployment on NVIDIA Jetson devices.
Ensure you install the `onnxruntime-gpu` wheel provided by NVIDIA JetPack, and update `config.yaml` to use TensorRT.
