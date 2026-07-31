PRD (Product Requirements Document)
Project Title

Edge AI Face Recognition Attendance System

Objective

Develop a real-time, offline face recognition attendance system capable of identifying registered students using a USB camera. The software will initially run on a laptop and later be deployed to an NVIDIA Jetson Nano with minimal architectural changes.

Functional Requirements
Student Registration
Register a new student with Name, Roll Number, and Department.
Capture one or more facial images from the camera.
Generate a face embedding using the recognition model.
Store the embedding and student information in SQLite.
Real-Time Recognition
Capture live video from a USB camera.
Detect faces in each frame.
Align detected faces.
Generate embeddings.
Compare against registered embeddings using cosine similarity.
Display the student's name and confidence score.
Mark attendance automatically.
Attendance
Prevent duplicate attendance within the same session.
Store timestamp.
Allow attendance history viewing.
Unknown Faces
Display "Unknown" when no match exceeds the threshold.
Do not mark attendance.
Non-Functional Requirements
Fully offline operation.
Modular architecture.
Jetson Nano compatibility.
ONNX model support.
TensorRT-ready design.
Average recognition latency under 200 ms per detected face on target hardware.
Clean, maintainable Python code.
AI Models
Task	Model
Face Detection	SCRFD-500M
Face Alignment	InsightFace
Face Recognition	ArcFace (InsightFace)
Similarity	Cosine Similarity
Technology Stack
Python 3.11
OpenCV
InsightFace
ONNX Runtime
NumPy
SQLite
PyYAML
Logging
Deliverables
Student registration module.
Live recognition module.
Attendance logging.
SQLite database.
Modular source code.
Configuration file.
Deployment-ready project structure for Jetson Nano.