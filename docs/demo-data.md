# University Demo Data & Attendance Simulation Guide (Phase 6)

This document provides complete instructions for seeding, clearing, and validating the realistic demo dataset for the **Edge AI Anti-Spoofing University Attendance Platform**.

---

## 1. Overview

To ensure the web application behaves like a production-ready university deployment rather than an empty prototype, Phase 6 provides automated utilities that generate a high-density, interconnected dataset adhering to the existing Phase 3 & 4 Firestore schema.

### Key Data Metrics
* **University**: 1 (Global Tech University - `univ-tech-01`)
* **Faculties**: 4 (Computing & IT, Engineering, Management Sciences, Social Sciences)
* **Departments**: 12 (CS, SE, AI & DS, Cyber Security, Electrical Eng, Mechanical Eng, Civil Eng, BBA, Accounting & Finance, Economics, Media Studies, Psychology)
* **Degree Programs**: 18 (BS & MS level programs)
* **Courses**: 60 (Department-aligned academic courses with credit hours)
* **Teachers**: 36 (3 faculty members per department with realistic profiles and employee codes)
* **Classes (Course Offerings)**: 54 (Assigned schedules, rooms, sections, instructors)
* **Students**: 280 (Unique roll numbers, enrolled in multi-course cohorts)
* **Historical Attendance**: ~3,500 Records (Spanning past 45 weekdays with realistic present/late/early leave/absent distributions)
* **AI Security Events**: 120 (Recognized faces, unknown subjects, and blocked spoof attacks)

---

## 2. Quick Start Commands

### Clear All Demo Data
Removes existing demo records from Firestore collections to start fresh:
```powershell
python src/scripts/clear_demo_data.py
```

### Seed Full Demo Dataset
Populates the complete university hierarchy, courses, teachers, classes, students, historical attendance, and recognition logs:
```powershell
python src/scripts/seed_demo_data.py
```

### Initialize Demo Auth Accounts
Ensures all standard Firebase Auth demo accounts exist and are linked to their corresponding Firestore profiles:
```powershell
python src/scripts/create_user.py
```

---

## 3. Demo User Accounts Matrix

All accounts use default password: **`password123`**

| Role | Login Email | Assigned Entity / Name | Scope & Accessible View |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@university.edu` | Super Admin | System-wide complete university statistics, all 12 departments, security logs |
| **VC** | `vc@university.edu` | Prof. Dr. Muhammad VC | University-level overview across all 4 faculties, student totals, campus attendance % |
| **Dean** | `dean@university.edu` | Prof. Dr. Tariq Dean | Faculty of Computing & IT scope (CS, SE, AI, Cyber Security departments) |
| **HOD** | `hod@university.edu` | Dr. Kamran Malik | Department of Computer Science scope (CS students, CS staff, CS attendance) |
| **Teacher** | `ali.khan@university.edu` | Dr. Ali Khan | Instructor portal (Assigned sections: AI 6A, Web Eng 6A, student rosters) |
| **Student** | `fa23-bcs-001@university.edu` | Darrell Steward | Personal student portal (BSCS 6A, enrolled courses, attendance streak, check-in history) |
| **Disabled** | `banned@university.edu` | Banned User | *Access denied (`active: false`)* |

---

## 4. Historical Attendance Simulation Logic

The seeder generates realistic check-in / check-out records spanning 45 weekdays:

1. **Schedule Filtering**: Only classes scheduled on that specific weekday (e.g. "Mon/Wed", "Tue/Thu", "Fri") are simulated.
2. **Realistic Status Distribution**:
   - **Present (~85%)**: Check-in 1–8 minutes before class starts. Check-out around class end (80–95 minutes duration).
   - **Late (~8%)**: Check-in 5–15 minutes after class starts. Check-out around class end.
   - **Early Leave (~3%)**: Check-in on time. Check-out 35–45 minutes into the class.
   - **Absent (~4%)**: No attendance record generated for that day.
3. **Hardware Telemetry**:
   - Camera IDs: `Main Gate Camera`, `CS Dept Camera`, `Lab 1 Camera`, `Lab 2 Camera`, `WEBCAM-01`.
   - Cosine Similarity Confidence: `0.88 - 0.98`
   - MiniFASNet Liveness Score: `0.92 - 0.99`

---

## 5. Dashboard Verification Checklist

1. **Login as VC (`vc@university.edu`)**:
   - Verify `Enrolled Students` shows ~280 verified students.
   - Verify `Faculty Members` shows 36 teachers.
   - Verify `Active Departments` displays all 12 operational departments.
   - Verify `Campus Attendance` reflects computed overall average (~86–88%).
2. **Login as Dean (`dean@university.edu`)**:
   - Verify view is scoped to the 4 Computing & IT departments (CS, SE, AI, Cyber Security).
   - Verify faculty-specific student and teacher counts.
3. **Login as HOD (`hod@university.edu`)**:
   - Verify view is scoped to the Computer Science department.
4. **Login as Teacher (`ali.khan@university.edu`)**:
   - Verify assigned course sections (AI 6A, Web Engineering 6A, etc.) are rendered.
   - Click a section to inspect the real student roster, individual attendance percentages, and today's status.
   - Verify the Weekly Attendance Trend chart reflects dynamic calculated heights.
5. **Login as Student (`fa23-bcs-001@university.edu`)**:
   - Verify student name `Darrell Steward`, program `BS Computer Science`, and roll number `FA23-BCS-001`.
   - Verify enrolled course cards (AI, Web Engineering, Computer Networks, Information Security) display calculated attendance progress bars.
   - Check the **My Attendance History** table with full date, check-in time, and facial AI verification metrics.
6. **Open Live Security Console (`/dashboard/monitoring`)**:
   - Inspect the real-time stream of 120+ AI detection events including `RECOGNIZED` students, `UNKNOWN` visitors, and flagged `SPOOF` photo attack blocks.
