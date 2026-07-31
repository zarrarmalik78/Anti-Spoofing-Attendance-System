# Anti-Spoofing (Liveness Detection) Module

## Overview
The anti-spoofing module is a critical security component of the Edge AI Attendance System. It ensures that the face detected by the camera belongs to a real, live person in front of the camera, rather than a printed photograph, a screen playing a video, or a 3D mask.

This module acts as a strict gatekeeper: **If a face is classified as a spoof, the system will not attempt to generate an ArcFace embedding or mark attendance.** This saves computational resources and maintains the integrity of the attendance database.

## Architecture

The system uses **MiniFASNetV2** (Silent-Face-Anti-Spoofing), a highly optimized and lightweight convolutional neural network specifically designed for edge devices.

### Pipeline

1. **Face Detection**: InsightFace (SCRFD) detects the bounding box of the face.
2. **Crop & Expansion**: The bounding box is expanded by a factor of ~2.7x. MiniFASNet relies on contextual clues (like the edges of a phone screen or paper) to detect spoofing, so a tight face crop is insufficient.
3. **Preprocessing**: The expanded crop is resized to `80x80` pixels, converted to BGR format, and normalized.
4. **Inference**: The ONNX model processes the image and outputs a confidence score.
5. **Gating**: If the `liveness_score` falls below the configurable `threshold` (default: `0.90`), the pipeline skips the ArcFace embedding phase.

## Configuration

The anti-spoofing behavior can be configured in `config/config.yaml`:

```yaml
anti_spoofing:
  enabled: true
  threshold: 0.90
  model_path: "models/anti_spoofing/minifasnet_v2.onnx"
```

- `enabled`: Set to `false` to completely disable liveness detection (not recommended for production).
- `threshold`: The minimum confidence (0.0 to 1.0) required to classify a face as "live". Higher values increase security but may cause false rejections in poor lighting.

## Hardware Acceleration (Jetson Nano)

The module uses ONNX Runtime (`onnxruntime`), which executes on the CPU by default in this implementation. However, because MiniFASNet is composed of standard neural network operations, it is fully compatible with **TensorRT**.

When deploying to the NVIDIA Jetson Nano, you can significantly improve inference speed by swapping the execution provider in `src/core/anti_spoofing.py`:

```python
# Change from:
providers = ['CPUExecutionProvider']

# To:
providers = ['TensorrtExecutionProvider', 'CUDAExecutionProvider']
```

This change requires no modification to the business logic or the model file itself.

## Error Handling

The system is designed to be resilient. If the ONNX model file is missing or corrupted, the `AntiSpoofAnalyzer` will log a warning and automatically disable itself, allowing the application to continue running (though without spoof protection). If an exception occurs during inference on a specific frame, the module will "fail closed" by classifying the face as a spoof to maintain security.
