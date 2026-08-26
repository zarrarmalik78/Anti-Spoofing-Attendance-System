# Firebase Integration (Phase 2)

This document describes the Firebase integration for the Edge AI Attendance System.

## Project Setup

1. Go to the Firebase Console and create a project (e.g., `edge-ai-attendance-system`).
2. Enable **Authentication** (Email/Password).
3. Enable **Cloud Firestore**.
4. Set Firestore Security Rules to allow development access (or require auth):
   ```text
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /{document=**} {
         allow read, write: if true; // Or 'if request.auth != null'
       }
     }
   }
   ```

## Required Configuration

Create a `.env` file in the root of the project using the provided `.env.example` as a template. You must include your Web API keys.

```env
FIREBASE_API_KEY=your_api_key_here
FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project_id.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id
```

*Note: Do not commit `.env` to source control. It is already in `.gitignore`.*

## Firestore Collections

The application automatically creates and writes to the following collections:

- **`students`**: Stores basic information (`studentId`, `name`, `rollNumber`, `department`, `email`).
- **`attendance`**: Stores attendance records (`studentId`, `studentName`, `timestamp`, `eventType`, `cameraId`, `confidence`, `livenessScore`, `sessionId`).
- **`recognition_events`**: Stores AI events for auditing, such as `SPOOF` and `UNKNOWN` detections, as well as `RECOGNIZED` events.
- **`users`**: (Placeholder for Phase 3 RBAC).
- **`_system_tests`**: Used internally on startup to verify Firebase connectivity.

## How to Run the Application with Firebase

1. Ensure the `.env` file is properly configured.
2. Ensure you have installed the required dependencies (`pip install -r requirements.txt` / `pip install python-dotenv`).
3. Run `python main.py`.

The application will attempt to connect to Firebase in the background and run a read/write test to the `_system_tests` collection.
If Firebase is unavailable or the configuration is invalid, the AI pipeline and local SQLite attendance will continue to function normally without crashing.

## How to Test the Connection

When `main.py` starts, check the console logs. You should see:
```text
INFO - Firebase connected successfully via REST API.
INFO - Running Firebase Read/Write test...
INFO - Firebase Read/Write test SUCCESSFUL.
```
If you encounter errors, verify your `.env` configuration and network access.
