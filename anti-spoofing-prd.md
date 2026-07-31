Implement AI Anti-Spoofing (Liveness Detection) Module

We are building an Edge AI Face Recognition Attendance System with the following pipeline:

Camera
↓
Face Detection (SCRFD)
↓
Face Alignment
↓
Anti-Spoofing (NEW)
↓
Face Recognition (ArcFace)
↓
Cosine Similarity Matching
↓
Attendance

The anti-spoofing module is a mandatory security component and must be implemented before the face recognition stage.

Objective

Implement a modular, production-quality anti-spoofing system that determines whether a detected face belongs to a real live person or a spoof attack before face recognition is performed.

The implementation must work completely offline and be designed for deployment on NVIDIA Jetson Nano.

Model Selection

Use a lightweight ONNX-compatible anti-spoofing model suitable for edge devices.

Preferred choice:

MiniFASNet (Silent Face Anti-Spoofing)

Requirements:

ONNX model
Lightweight
Real-time inference
TensorRT compatible
Works with a normal RGB USB camera
No cloud APIs

Do not use heavy models that are unsuitable for Jetson Nano.

Desired Pipeline

For every detected face:

OpenCV Frame

↓

SCRFD detects face

↓

Align face to 112×112

↓

MiniFASNet

↓

Output:

Live Score

Fake Score

↓

If Live Score > Threshold

↓

Continue to ArcFace Recognition

Else

↓

Reject Recognition

↓

Display "Spoof Detected"

↓

Do NOT mark attendance

Recognition should never execute if anti-spoofing fails.


Input

Input to MiniFASNet:

Aligned RGB Face

112×112

float32

Normalized

NCHW

Use the correct preprocessing required by the selected model.

Output

The model should return:

Live Score

Fake Score

Convert the scores into:

is_live

live_score

fake_score

using a configurable threshold.

Store threshold inside:

config/config.yaml

Example:

anti_spoofing:

    enabled: true

    threshold: 0.90

    model_path: models/minifasnet.onnx
Registration

Anti-spoofing must also run during student registration.

Registration flow:

Capture Face

↓

Detect Face

↓

Align Face

↓

Anti-Spoofing

↓

If Live

↓

Generate Embedding

↓

Store Student

Else

↓

Reject Registration

↓

Show Message

"Live face required for registration."

Do not allow registration using:

printed photographs
phone screens
replay videos
Live Recognition

Recognition flow:

Camera Frame

↓

Face Detection

↓

Alignment

↓

Anti-Spoofing

↓

LIVE ?

↓

YES

↓

ArcFace

↓

Recognition

↓

Attendance

NO

↓

Red Bounding Box

↓

Label:

Spoof Detected

↓

Skip Recognition
GUI Requirements

Display anti-spoofing status in real time.

Examples:

Recognized:

Ali

LIVE

97.6%

Unknown:

Unknown

LIVE


Spoof:

Spoof Detected

FAKE

92.3%

Bounding box colors:

Green → Live + Recognized

Yellow → Live + Unknown

Red → Spoof

Performance

The anti-spoofing module must:

process every detected face independently
avoid blocking the recognition pipeline
reuse loaded ONNX sessions
avoid loading the model repeatedly
target real-time performance suitable for Jetson Nano
Logging

Log events such as:

AntiSpoof model loaded

Spoof detected

Live face verified

Inference failed

Do not log every frame.

Only important events.

Future TensorRT Compatibility

Design the module so the inference backend can later be replaced by TensorRT without changing application logic.

Separate model loading from business logic.

Do not hardcode ONNX Runtime throughout the project.

Error Handling

Gracefully handle:

missing model file
corrupted model
inference exceptions
invalid input size
empty face crop

The application should continue running even if anti-spoofing temporarily fails.

Documentation

Create:

docs/AntiSpoofing.md

Explain:

Why anti-spoofing is required.
Common spoof attacks (photo, replay video, phone screen, printed image).
Why MiniFASNet was selected.
How the pipeline works.
How TensorRT can replace ONNX Runtime later.
Code Quality

Requirements:

Python type hints
SOLID principles
Modular architecture
Proper exception handling
Comprehensive docstrings
Configurable parameters
No hardcoded paths
Reusable classes

The implementation should be production-ready, easily maintainable, and optimized for future deployment on NVIDIA Jetson Nano.