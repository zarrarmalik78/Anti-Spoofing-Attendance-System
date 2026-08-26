# Edge AI Anti-Spoofing University Attendance Platform — Master System Overview

This document provides a comprehensive summary of the architecture, design decisions, completed implementation phases, and environment setup for this repository. Any AI agent or developer reading this file can instantly understand the entire codebase state and resume work seamlessly.

---

## 1. Project Goal & High-Level Architecture

The goal of this project is to upgrade an existing AI-based face recognition attendance system into a production-ready, enterprise university attendance platform.

The system uses a **2-tier hybrid architecture**:
1. **Edge Desktop App (Python + CustomTkinter)**: Runs locally on laptop hardware connected to a webcam. Executes face detection (SCRFD), anti-spoofing/liveness verification (MiniFASNet), and face embedding matching (ArcFace). Manages local SQLite storage and asynchronously streams check-in events to Firebase.
2. **Cloud Web Application (React + TypeScript + Vite + Tailwind)**: Multi-role web portal connected to Cloud Firestore and Firebase Authentication. Provides specialized dashboards for Students, Teachers, HODs, Deans, VCs, and System Administrators, along with a real-time live camera monitoring console.

---

## 2. Implemented Phases Summary (Phase 1 – Phase 5)

### 🔹 Phase 1 — AI Pipeline Decoupling & Architecture Refactor
* **Objective**: Decouple the computer vision AI pipeline from attendance marking and database logic without altering existing AI models.
* **Key Components**:
  * `AIEngine` (`src/core/ai_engine.py`): Wraps SCRFD face detection, MiniFASNet anti-spoofing, and ArcFace embedding matcher.
  * `RecognitionEvent` (`src/core/events.py`): Standardized dataclass passed between AI engine and attendance manager. Contains `timestamp`, `bbox`, `event_type`, `student_id`, `student_name`, `recognition_confidence`, `is_live`, `liveness_score`, `camera_id` (`"WEBCAM-01"`), and `device_id` (`"LAPTOP-01"`).
  * `EventType` (`src/core/events.py`): Enum with values `RECOGNIZED`, `UNKNOWN`, `SPOOF`, `NO_FACE`.
  * `AttendanceEngine` (`src/core/attendance_engine.py`): Handles attendance rules. **Only `RECOGNIZED` events mark attendance.** `UNKNOWN` and `SPOOF` events log security events without marking attendance.

### 🔹 Phase 2 — Firebase Integration
* **Objective**: Connect local system to Firebase Cloud Firestore and Authentication using a lightweight HTTP REST wrapper (`requests`), avoiding native C++ SDK dependencies on edge devices.
* **Key Components**:
  * `FirebaseConfig` (`src/firebase/firebase_config.py`): Loads `.env` configuration.
  * `FirebaseService` (`src/firebase/firebase_service.py`): REST API client supporting async background writes to Firestore.
  * Dual-Writing: `AttendanceEngine` logs check-ins to local SQLite `attendance` table AND asynchronously pushes records to Firestore `attendance` and `recognition_events` collections.

### 🔹 Phase 3 — University Data Model & Management Foundation
* **Objective**: Build the core university data model in Firestore supporting scalable hierarchy without deep nested collections.
* **Collections**:
  * `universities`: University metadata.
  * `faculties`: Faculty metadata linked to `universityId`.
  * `departments`: Department metadata linked to `facultyId`.
  * `programs`: Degree programs linked to `departmentId`.
  * `courses`: Academic courses linked to `departmentId`.
  * `teachers`: Faculty staff profiles linked to `departmentId` and `userId`.
  * `classes`: Course offerings containing `courseId`, `teacherId`, `programId`, `semester`, `section`.
  * `students`: Enrolled student profiles containing `programId`, `departmentId`, `section`, and `classIds` array (for O(1) student schedule lookup and `array-contains` class roster queries).
  * `attendance`: Extended with placeholders for `classId`, `courseId`, `teacherId`, `departmentId`.
* **Seed Script**: `src/scripts/seed_firebase.py` populates a mock "Global Tech University" hierarchy.

### 🔹 Phase 4 — Authentication & Role-Based Access Control (RBAC)
* **Objective**: Enforce user roles and access scoping.
* **Roles Supported**: `admin`, `vc`, `dean`, `hod`, `teacher`, `student`.
* **Key Components**:
  * `FirebaseService` Auth Extensions: Implemented `sign_up`, `sign_in` (fetching Firestore `users` profile doc and checking `active: true`), `get_current_role()`, and `get_user_scope()`.
  * Security Rules (`firestore.rules`): Firestore rules enforcing role boundaries (e.g., Students can only read their own attendance; Teachers can only access assigned classes; HODs restricted to department).
  * User Creation Script (`src/scripts/create_user.py`): Creates Firebase Auth accounts, sets up `users/{uid}` profile docs, and links UIDs to entity records (`students`, `teachers`, `departments`, etc.).
  * Python Auth Guard (`src/firebase/auth_guard.py`): Decorator utilities (`@auth_guard.require_hod`) for protecting python routes.

### 🔹 Phase 5 — University Web Application & Role Dashboards
* **Objective**: Build a responsive React + TypeScript web application.
* **Stack**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Firebase JS SDK.
* **Directory**: `web/`
* **Key Components**:
  * `AuthContext.tsx`: Tracks authentication state and user profile role.
  * `ProtectedRoute.tsx`: Client-side route guard ensuring unauthorized roles cannot access forbidden URLs.
  * `Sidebar.tsx`: Dynamic navigation bar rendering links based on logged-in role.
  * `StudentDashboard.tsx`: Displays attendance percentage, missed classes, and recent check-ins.
  * `TeacherDashboard.tsx`: Displays assigned classes, total students, and daily check-ins.
  * `GenericAdminDashboard.tsx`: Hierarchical management view for HOD, Dean, VC, and Admin.
  * `LiveMonitoring.tsx`: Uses Firestore `onSnapshot` real-time listener to stream live face recognition and spoof detection alerts directly from the Edge AI app.
* **Documentation**: `docs/web-application.md`

---

## 3. Environment & Machine Setup Instructions

### Prerequisites
* **Python**: 3.10 or higher
* **Node.js**: v18 or higher (with `npm`)
* **Firebase Project**: A Firebase project with **Email/Password Authentication** and **Cloud Firestore Database** enabled.

---

### Step 1: Environment Variables Setup

1. **Root Environment File (`.env`)**:
   Create a `.env` file in the root directory:
   ```env
   FIREBASE_API_KEY=AIzaSyAC_0TAIKxKvRMvYG4XGZjQAc3bLUDEyuM
   FIREBASE_AUTH_DOMAIN=edge-ai-attendance-system.firebaseapp.com
   FIREBASE_PROJECT_ID=edge-ai-attendance-system
   FIREBASE_STORAGE_BUCKET=edge-ai-attendance-system.firebasestorage.app
   FIREBASE_MESSAGING_SENDER_ID=505945196859
   FIREBASE_APP_ID=1:505945196859:web:74e67decdb2faf84d2cf1e
   FIREBASE_MEASUREMENT_ID=G-88JTDS0VLK
   ```

2. **Web Environment File (`web/.env`)**:
   Create a `.env` file in the `web/` directory:
   ```env
   VITE_FIREBASE_API_KEY=AIzaSyAC_0TAIKxKvRMvYG4XGZjQAc3bLUDEyuM
   VITE_FIREBASE_AUTH_DOMAIN=edge-ai-attendance-system.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=edge-ai-attendance-system
   VITE_FIREBASE_STORAGE_BUCKET=edge-ai-attendance-system.firebasestorage.app
   VITE_FIREBASE_MESSAGING_SENDER_ID=505945196859
   VITE_FIREBASE_APP_ID=1:505945196859:web:74e67decdb2faf84d2cf1e
   VITE_FIREBASE_MEASUREMENT_ID=G-88JTDS0VLK
   ```

---

### Step 2: Python Edge System Setup

```powershell
# Create Virtual Environment
python -m venv .venv

# Activate Virtual Environment (Windows PowerShell)
.venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Seed Firestore Hierarchy
python src/scripts/seed_firebase.py

# Seed Firebase Auth & Firestore Users
python src/scripts/create_user.py

# Launch Local Desktop AI App
python main.py
```

---

### Step 3: Web Portal Setup

```powershell
# Navigate to web directory
cd web

# Install Dependencies
npm install

# Build Verification
npm run build

# Launch Development Server
npm run dev
```
*Access Web Portal at `http://localhost:5173`*

---

## 4. Default Test Credentials

All pre-configured test accounts use password: **`password123`**

| Role | Email | Scope / Dashboard View |
| :--- | :--- | :--- |
| **Admin** | `admin@university.edu` | System-wide full management |
| **VC** | `vc@university.edu` | University-wide stats overview |
| **Dean** | `dean@university.edu` | Faculty of Computing overview |
| **HOD** | `hod@university.edu` | Computer Science Department overview |
| **Teacher** | `ali.khan@university.edu` | Class rosters & attendance tables |
| **Student** | `fa23-bcs-001@university.edu` | Personal attendance % & history |
| **Disabled** | `banned@university.edu` | *Access blocked (`active: false`)* |

---

## 5. File & Directory Sitemap

```text
Anti-Spoofing-Attendance-System/
├── PROJECT_OVERVIEW.md         <-- (THIS FILE) Master System Documentation
├── firestore.rules             <-- Production Security Rules for Firestore
├── main.py                     <-- Desktop GUI Entry Point
├── requirements.txt            <-- Python Dependencies
├── docs/                       <-- Phase Documentation
│   ├── firebase.md
│   └── web-application.md
├── src/
│   ├── core/                   <-- Decoupled AI & Attendance Logic
│   │   ├── ai_engine.py        <-- SCRFD, MiniFASNet, ArcFace Wrapper
│   │   ├── attendance_engine.py<-- Business rules & cloud stream
│   │   ├── events.py           <-- RecognitionEvent data structures
│   │   └── student_registrar.py
│   ├── firebase/               <-- Firebase REST Layer & Auth Guards
│   │   ├── auth_guard.py       <-- Python RBAC decorators
│   │   ├── firebase_config.py  <-- Env config loader
│   │   └── firebase_service.py <-- REST client for Firestore & Auth
│   ├── gui/                    <-- CustomTkinter Desktop UI
│   └── scripts/                <-- Database Utilities
│       ├── create_user.py      <-- Seed Auth Accounts & Roles
│       └── seed_firebase.py    <-- Seed University Hierarchy
└── web/                        <-- React TypeScript Web App
    ├── src/
    │   ├── components/         <-- ProtectedRoute, Sidebar, Topbar, StatCard
    │   ├── context/            <-- AuthContext for user state
    │   ├── firebase/           <-- JS SDK config
    │   └── pages/              <-- Login, Dashboards, LiveMonitoring
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.ts
```
