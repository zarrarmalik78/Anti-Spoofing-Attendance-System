CREATE TABLE IF NOT EXISTS students (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT    NOT NULL,
    roll_number       TEXT    NOT NULL UNIQUE,
    department        TEXT    NOT NULL,
    embedding         BLOB    NOT NULL,    -- float32 bytes, 512-d
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    marked_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id  TEXT     NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_session ON attendance(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date    ON attendance(marked_at);

CREATE TABLE IF NOT EXISTS offline_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    collection  TEXT NOT NULL,
    document_id TEXT,
    data_json   TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

