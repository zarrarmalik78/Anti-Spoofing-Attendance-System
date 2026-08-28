import sqlite3
import os
import numpy as np
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import datetime

from src.utils.logger import get_logger
from src.utils.time_utils import get_current_time, get_current_time_str

logger = get_logger(__name__)

@dataclass
class StudentRecord:
    id: int
    name: str
    roll_number: str
    department: str
    embedding: np.ndarray
    registration_date: str

@dataclass
class AttendanceRecord:
    id: int
    student_id: int
    name: str
    roll_number: str
    department: str
    marked_at: str
    session_id: str

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure the directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        """Initializes the database schema using schema.sql"""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not os.path.exists(schema_path):
            logger.error(f"Schema file not found at {schema_path}")
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()

            with self._get_connection() as conn:
                conn.executescript(schema_sql)
                logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def insert_student(self, name: str, roll_number: str, department: str, embedding: np.ndarray) -> int:
        """Inserts a new student into the database."""
        # Convert embedding to bytes for BLOB storage
        embedding_bytes = embedding.astype(np.float32).tobytes()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO students (name, roll_number, department, embedding) VALUES (?, ?, ?, ?)",
                    (name, roll_number, department, embedding_bytes)
                )
                student_id = cursor.lastrowid
                logger.info(f"Registered student {name} ({roll_number}) with ID {student_id}")
                return student_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to insert student {name}. Roll number {roll_number} might already exist. Error: {e}")
            raise ValueError(f"Roll number {roll_number} already exists.")
        except Exception as e:
            logger.error(f"Failed to insert student {name}: {e}")
            raise

    def student_exists(self, roll_number: str) -> bool:
        """Checks if a student with the given roll number exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM students WHERE roll_number = ?", (roll_number,))
            return cursor.fetchone() is not None

    def update_student_embedding(self, roll_number: str, name: str, department: str, embedding: np.ndarray) -> int:
        """Updates embedding vector and details for an existing student by roll number."""
        embedding_bytes = embedding.astype(np.float32).tobytes()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET name = ?, department = ?, embedding = ? WHERE roll_number = ?",
                (name, department, embedding_bytes, roll_number)
            )
            cursor.execute("SELECT id FROM students WHERE roll_number = ?", (roll_number,))
            row = cursor.fetchone()
            student_id = row['id'] if row else 1
            logger.info(f"Updated embedding for student {name} ({roll_number}) with ID {student_id}")
            return student_id

    def get_all_students(self) -> List[StudentRecord]:
        """Retrieves all registered students."""
        students = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students")
                rows = cursor.fetchall()
                
                for row in rows:
                    embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                    students.append(StudentRecord(
                        id=row['id'],
                        name=row['name'],
                        roll_number=row['roll_number'],
                        department=row['department'],
                        embedding=embedding,
                        registration_date=row['registration_date']
                    ))
        except Exception as e:
            logger.error(f"Failed to retrieve students: {e}")
        return students

    def get_student_by_id(self, student_id: int) -> Optional[StudentRecord]:
        """Retrieves a specific student by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
                row = cursor.fetchone()
                
                if row:
                    embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                    return StudentRecord(
                        id=row['id'],
                        name=row['name'],
                        roll_number=row['roll_number'],
                        department=row['department'],
                        embedding=embedding,
                        registration_date=row['registration_date']
                    )
        except Exception as e:
            logger.error(f"Failed to retrieve student ID {student_id}: {e}")
        return None

    def insert_attendance(self, student_id: int, session_id: str) -> None:
        """Marks attendance for a student in a specific session."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                now_str = get_current_time_str()
                cursor.execute(
                    "INSERT INTO attendance (student_id, session_id, marked_at) VALUES (?, ?, ?)",
                    (student_id, session_id, now_str)
                )
                logger.info(f"Marked attendance for student ID {student_id} (Session: {session_id})")
        except Exception as e:
            logger.error(f"Failed to mark attendance for student ID {student_id}: {e}")
            raise

    def delete_student(self, student_id: int) -> bool:
        """Deletes a student and all their attendance records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                logger.info(f"Deleted student ID {student_id} and their attendance records.")
                return True
        except Exception as e:
            logger.error(f"Failed to delete student ID {student_id}: {e}")
            return False

    def get_today_attendance(self) -> List[AttendanceRecord]:
        """Retrieves attendance records for the current day."""
        today = get_current_time().strftime('%Y-%m-%d')
        records = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT a.id, a.student_id, s.name, s.roll_number, s.department, a.marked_at, a.session_id
                    FROM attendance a
                    JOIN students s ON a.student_id = s.id
                    WHERE date(a.marked_at) = ?
                    ORDER BY a.marked_at DESC
                """
                cursor.execute(query, (today,))
                rows = cursor.fetchall()
                
                for row in rows:
                    records.append(AttendanceRecord(
                        id=row['id'],
                        student_id=row['student_id'],
                        name=row['name'],
                        roll_number=row['roll_number'],
                        department=row['department'],
                        marked_at=row['marked_at'],
                        session_id=row['session_id']
                    ))
        except Exception as e:
            logger.error(f"Failed to retrieve today's attendance: {e}")
        return records

    def get_session_attendance(self, session_id: str) -> List[AttendanceRecord]:
        """Retrieves attendance records for a specific session."""
        records = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT a.id, a.student_id, s.name, s.roll_number, s.department, a.marked_at, a.session_id
                    FROM attendance a
                    JOIN students s ON a.student_id = s.id
                    WHERE a.session_id = ?
                    ORDER BY a.marked_at DESC
                """
                cursor.execute(query, (session_id,))
                rows = cursor.fetchall()
                
                for row in rows:
                    records.append(AttendanceRecord(
                        id=row['id'],
                        student_id=row['student_id'],
                        name=row['name'],
                        roll_number=row['roll_number'],
                        department=row['department'],
                        marked_at=row['marked_at'],
                        session_id=row['session_id']
                    ))
        except Exception as e:
            logger.error(f"Failed to retrieve session attendance: {e}")
        return records

    def get_total_student_count(self) -> int:
        """Returns the total number of registered students."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(id) FROM students")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get student count: {e}")
            return 0

    def enqueue_offline_item(self, collection: str, data_dict: dict, document_id: Optional[str] = None) -> bool:
        """Buffers a failed cloud document write locally for automatic retry when online."""
        try:
            import json
            data_json = json.dumps(data_dict)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO offline_queue (collection, document_id, data_json) VALUES (?, ?, ?)",
                    (collection, document_id, data_json)
                )
                logger.info(f"Enqueued offline item for collection '{collection}'")
                return True
        except Exception as e:
            logger.error(f"Failed to enqueue offline item: {e}")
            return False

    def get_offline_items(self, limit: int = 50) -> List[dict]:
        """Retrieves pending offline documents to flush to Cloud Firestore."""
        items = []
        try:
            import json
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, collection, document_id, data_json, retry_count FROM offline_queue ORDER BY id ASC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                for row in rows:
                    items.append({
                        "id": row["id"],
                        "collection": row["collection"],
                        "document_id": row["document_id"],
                        "data": json.loads(row["data_json"]),
                        "retry_count": row["retry_count"]
                    })
        except Exception as e:
            logger.error(f"Failed to fetch offline queue items: {e}")
        return items

    def delete_offline_item(self, item_id: int) -> bool:
        """Deletes a successfully synced item from the offline queue."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM offline_queue WHERE id = ?", (item_id,))
                return True
        except Exception as e:
            logger.error(f"Failed to delete offline queue item {item_id}: {e}")
            return False

