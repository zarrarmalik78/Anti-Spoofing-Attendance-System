import os
import sys
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTIONS_TO_CLEAR = [
    "attendance",
    "recognition_events",
    "students",
    "classes",
    "courses",
    "teachers",
    "programs",
    "departments",
    "faculties",
    "universities",
    "_system_tests"
]

def clear_collection(firebase: FirebaseService, collection_name: str) -> int:
    """Deletes all documents in a collection in parallel."""
    docs = firebase.list_documents(collection_name)
    if not docs:
        logger.info(f"Collection '{collection_name}' is already empty.")
        return 0

    doc_ids = [d.get("_id") for d in docs if d.get("_id")]
    logger.info(f"Deleting {len(doc_ids)} document(s) from '{collection_name}'...")

    deleted_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(firebase.delete_document_sync, collection_name, doc_id)
            for doc_id in doc_ids
        ]
        for f in futures:
            if f.result():
                deleted_count += 1

    logger.info(f"Cleared {deleted_count}/{len(doc_ids)} from '{collection_name}'.")
    return deleted_count

def clear_all_demo_data():
    logger.info("=" * 60)
    logger.info("STARTING FIREBASE DEMO DATA CLEANUP")
    logger.info("=" * 60)

    firebase = FirebaseService()
    if not firebase.config.is_valid():
        logger.error("Firebase config is invalid. Check .env file.")
        return

    total_deleted = 0
    summary = {}

    for col in COLLECTIONS_TO_CLEAR:
        count = clear_collection(firebase, col)
        summary[col] = count
        total_deleted += count

    logger.info("=" * 60)
    logger.info("CLEANUP COMPLETED SUMMARY:")
    for col, count in summary.items():
        logger.info(f"  - {col}: {count} records removed")
    logger.info(f"Total documents deleted: {total_deleted}")
    logger.info("=" * 60)

if __name__ == "__main__":
    clear_all_demo_data()
