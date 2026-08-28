import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import time
import threading
from typing import Dict, Any, Optional, List

from src.firebase.firebase_config import FirebaseConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FirebaseService:
    """
    Lightweight wrapper for Firebase Authentication and Cloud Firestore REST APIs.
    Designed for development use without requiring full Admin SDK service accounts.
    """
    def __init__(self):
        self.config = FirebaseConfig
        self.auth_url = "https://identitytoolkit.googleapis.com/v1"
        self.firestore_url = f"https://firestore.googleapis.com/v1/projects/{self.config.PROJECT_ID}/databases/(default)/documents"
        
        self.current_user: Optional[Dict[str, Any]] = None
        self.id_token: Optional[str] = None
        
        # Setup persistent session with pooling and retries
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        self.is_connected = False
        self._test_connection()

    def _test_connection(self):
        """Tests the connection to Firebase via a simple REST call."""
        if not self.config.is_valid():
            logger.warning("Firebase configuration is invalid or missing.")
            return

        def _run_test():
            for attempt in range(3):
                try:
                    # Basic connection test
                    response = self.session.get(f"{self.firestore_url}?key={self.config.API_KEY}", timeout=15)
                    self.is_connected = True
                    logger.info("Firebase connected successfully via REST API.")
                    
                    # Full Read/Write Test
                    logger.info("Running Firebase Read/Write test...")
                    test_doc_id = "test_connection_doc"
                    test_data = {"status": "success", "timestamp": str(threading.get_ident())}
                    
                    # Write (using PATCH to allow overwriting)
                    firestore_data = self._to_firestore_format(test_data)
                    url = f"{self.firestore_url}/_system_tests/{test_doc_id}?key={self.config.API_KEY}"
                    self.session.patch(url, json=firestore_data, timeout=15)
                    
                    # Read
                    get_url = f"{self.firestore_url}/_system_tests/{test_doc_id}?key={self.config.API_KEY}"
                    get_resp = self.session.get(get_url, timeout=15)
                    if get_resp.status_code == 200:
                        read_data = self._from_firestore_format(get_resp.json())
                        if read_data.get("status") == "success":
                            logger.info("Firebase Read/Write test SUCCESSFUL.")
                            return
                        else:
                            logger.warning("Firebase Read/Write test failed: Data mismatch.")
                    elif get_resp.status_code == 403:
                        logger.warning("Firebase Read/Write test failed with 403 Forbidden. Please check your Firestore Security Rules (allow read, write).")
                    else:
                        logger.warning(f"Firebase Read/Write test failed: Read returned {get_resp.status_code}")
                    return
                except Exception as e:
                    if attempt == 2:
                        logger.error(f"Failed to connect to Firebase: {e}")
                        self.is_connected = False
                    time.sleep(1.0)

        threading.Thread(target=_run_test, daemon=True).start()

    # ---------------------------------------------------------
    # Authentication & RBAC (Phase 4)
    # ---------------------------------------------------------

    def sign_up(self, email: str, password: str) -> Optional[str]:
        """Signs up a new user and returns their UID."""
        if not self.config.is_valid():
            return None
        
        url = f"{self.auth_url}/accounts:signUp?key={self.config.API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        try:
            response = self.session.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("localId")
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error', {}).get('message', str(e))
            logger.error(f"Firebase Auth Error (sign_up): {error_msg}")
            return None
        except Exception as e:
            logger.error(f"Sign up failed: {e}")
            return None

    def sign_in(self, email: str, password: str) -> bool:
        """Signs in a user, fetches their role, and checks active state."""
        if not self.config.is_valid():
            return False

        url = f"{self.auth_url}/accounts:signInWithPassword?key={self.config.API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        try:
            response = self.session.post(url, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            self.id_token = data.get("idToken")
            uid = data.get("localId")
            
            # Fetch user profile from Firestore
            user_doc = self.get_document("users", uid)
            if not user_doc:
                logger.warning(f"User {email} signed in but has no Firestore profile.")
                self.sign_out()
                return False
                
            if not user_doc.get("active", True):
                logger.warning(f"User {email} is disabled.")
                self.sign_out()
                return False
                
            self.current_user = {
                "uid": uid,
                "email": data.get("email"),
                "displayName": data.get("displayName"),
                "role": user_doc.get("role", "student"),
                "scope": user_doc.get("scope", {})
            }
            logger.info(f"User {email} signed in successfully as {self.current_user['role']}.")
            return True
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error', {}).get('message', str(e))
            logger.error(f"Firebase Auth Error: {error_msg}")
            return False
        except Exception as e:
            logger.error(f"Sign in failed: {e}")
            return False

    def sign_out(self):
        """Clears local authentication state."""
        self.current_user = None
        self.id_token = None
        logger.info("User signed out.")

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        return self.current_user
        
    def get_current_role(self) -> Optional[str]:
        return self.current_user.get("role") if self.current_user else None
        
    def get_user_scope(self) -> Dict[str, Any]:
        """Returns the specific entity IDs this user is authorized to manage/view."""
        return self.current_user.get("scope", {}) if self.current_user else {}

    # ---------------------------------------------------------
    # Cloud Firestore Data Conversion Helpers
    # ---------------------------------------------------------
    
    def _convert_value_to_firestore(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, bool):  # Must check bool before int because bool is a subclass of int in Python
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif value is None:
            return {"nullValue": None}
        elif isinstance(value, list):
            return {"arrayValue": {"values": [self._convert_value_to_firestore(v) for v in value]}}
        elif isinstance(value, dict):
            return {"mapValue": {"fields": {k: self._convert_value_to_firestore(v) for k, v in value.items()}}}
        else:
            return {"stringValue": str(value)}

    def _to_firestore_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converts a flat dictionary to Firestore REST API typed format."""
        fields = {k: self._convert_value_to_firestore(v) for k, v in data.items()}
        return {"fields": fields}

    def _convert_value_from_firestore(self, value_dict: Dict[str, Any]) -> Any:
        if not value_dict:
            return None
        type_key, actual_value = next(iter(value_dict.items()))
        
        if type_key == "integerValue":
            return int(actual_value)
        elif type_key == "doubleValue":
            return float(actual_value)
        elif type_key == "booleanValue":
            return bool(actual_value)
        elif type_key == "nullValue":
            return None
        elif type_key == "arrayValue":
            values = actual_value.get("values", [])
            return [self._convert_value_from_firestore(v) for v in values]
        elif type_key == "mapValue":
            fields = actual_value.get("fields", {})
            return {k: self._convert_value_from_firestore(v) for k, v in fields.items()}
        else:
            return actual_value

    def _from_firestore_format(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Converts Firestore REST API typed format back to a flat dictionary."""
        data = {}
        fields = doc.get("fields", {})
        for key, value_dict in fields.items():
            data[key] = self._convert_value_from_firestore(value_dict)
            
        # Also include document ID if available
        if "name" in doc:
            data["_id"] = doc["name"].split("/")[-1]
            
        return data

    # ---------------------------------------------------------
    # Cloud Firestore Operations
    # ---------------------------------------------------------

    def attach_db_manager(self, db_manager):
        """Attaches DatabaseManager for local offline queue fallback."""
        self.db_manager = db_manager
        self._start_offline_sync_loop()

    def _start_offline_sync_loop(self):
        def _sync_worker():
            while True:
                time.sleep(15.0)
                if not hasattr(self, 'db_manager') or self.db_manager is None:
                    continue
                try:
                    offline_items = self.db_manager.get_offline_items(limit=30)
                    if not offline_items:
                        continue
                    logger.info(f"Flushing {len(offline_items)} offline queued items to Cloud Firestore...")
                    for item in offline_items:
                        success = self.create_document_sync(item['collection'], item['data'], item['document_id'])
                        if success:
                            self.db_manager.delete_offline_item(item['id'])
                except Exception as e:
                    logger.debug(f"Offline sync check encountered temporary error: {e}")
        
        threading.Thread(target=_sync_worker, daemon=True).start()

    def create_document(self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> bool:
        """
        Creates a document in Firestore.
        Uses a background thread to prevent blocking the UI/AI loop.
        Buffers to local SQLite queue if write fails due to network outage.
        """
        if not self.config.is_valid():
            return False

        def _worker():
            try:
                firestore_data = self._to_firestore_format(data)
                headers = {}
                if self.id_token:
                    headers["Authorization"] = f"Bearer {self.id_token}"
                
                if document_id:
                    url = f"{self.firestore_url}/{collection}?documentId={document_id}&key={self.config.API_KEY}"
                    response = self.session.post(url, json=firestore_data, headers=headers, timeout=10)
                else:
                    url = f"{self.firestore_url}/{collection}?key={self.config.API_KEY}"
                    response = self.session.post(url, json=firestore_data, headers=headers, timeout=10)
                    
                response.raise_for_status()
                logger.debug(f"Successfully wrote to {collection}")
            except Exception as e:
                logger.warning(f"Firestore write failed for {collection}: {e}. Buffering to local offline queue...")
                if hasattr(self, 'db_manager') and self.db_manager:
                    self.db_manager.enqueue_offline_item(collection, data, document_id)

        # Fire and forget
        threading.Thread(target=_worker, daemon=True).start()
        return True

    def create_document_sync(self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None) -> bool:
        """Synchronously creates a document in Firestore with retry."""
        if not self.config.is_valid():
            return False

        firestore_data = self._to_firestore_format(data)
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
        
        for attempt in range(2):
            try:
                if document_id:
                    url = f"{self.firestore_url}/{collection}?documentId={document_id}&key={self.config.API_KEY}"
                    response = self.session.post(url, json=firestore_data, headers=headers, timeout=10)
                    if response.status_code == 409: # CONFLICT / already exists
                        url = f"{self.firestore_url}/{collection}/{document_id}?key={self.config.API_KEY}"
                        response = self.session.patch(url, json=firestore_data, headers=headers, timeout=10)
                else:
                    url = f"{self.firestore_url}/{collection}?key={self.config.API_KEY}"
                    response = self.session.post(url, json=firestore_data, headers=headers, timeout=10)
                    
                response.raise_for_status()
                logger.debug(f"Successfully wrote to {collection}")
                return True
            except Exception as e:
                if attempt == 1:
                    logger.warning(f"Firestore sync write failed for {collection}: {e}")
                    return False
                time.sleep(0.3)
        return False

    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Synchronously fetches a document from Firestore with retry."""
        if not self.config.is_valid():
            return None
            
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
            
        url = f"{self.firestore_url}/{collection}/{document_id}?key={self.config.API_KEY}"
        for attempt in range(3):
            try:
                response = self.session.get(url, headers=headers, timeout=15)
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return self._from_firestore_format(response.json())
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Firestore read failed for {collection}/{document_id}: {e}")
                    return None
                time.sleep(0.3 * (attempt + 1))
        return None

    def list_documents(self, collection: str, page_size: int = 300) -> List[Dict[str, Any]]:
        """Synchronously fetches all documents in a collection, handling pagination."""
        if not self.config.is_valid():
            return []
            
        try:
            documents = []
            page_token = None
            headers = {}
            if self.id_token:
                headers["Authorization"] = f"Bearer {self.id_token}"
                
            while True:
                token_param = f"&pageToken={page_token}" if page_token else ""
                url = f"{self.firestore_url}/{collection}?pageSize={page_size}&key={self.config.API_KEY}{token_param}"
                
                resp = None
                for attempt in range(3):
                    try:
                        resp = self.session.get(url, headers=headers, timeout=15)
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise e
                        time.sleep(0.3 * (attempt + 1))

                if resp is None or resp.status_code == 404:
                    break
                resp.raise_for_status()
                
                data = resp.json()
                docs = data.get("documents", [])
                documents.extend([self._from_firestore_format(doc) for doc in docs])
                
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
                    
            return documents
        except Exception as e:
            logger.error(f"Firestore list failed for {collection}: {e}")
            return []

    def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """
        Updates a document in Firestore.
        Uses a background thread.
        """
        if not self.config.is_valid():
            return False

        def _worker():
            try:
                firestore_data = self._to_firestore_format(data)
                update_mask = ""
                for key in data.keys():
                    update_mask += f"&updateMask.fieldPaths={key}"
                    
                url = f"{self.firestore_url}/{collection}/{document_id}?key={self.config.API_KEY}{update_mask}"
                
                headers = {}
                if self.id_token:
                    headers["Authorization"] = f"Bearer {self.id_token}"
                    
                response = self.session.patch(url, json=firestore_data, headers=headers, timeout=15)
                response.raise_for_status()
                logger.debug(f"Successfully updated {collection}/{document_id}")
            except Exception as e:
                logger.error(f"Firestore update failed for {collection}/{document_id}: {e}")

        threading.Thread(target=_worker, daemon=True).start()
        return True

    def soft_delete_document(self, collection: str, document_id: str) -> bool:
        """Sets active=False on a document."""
        return self.update_document(collection, document_id, {"active": False})

    def delete_document_sync(self, collection: str, document_id: str) -> bool:
        """Synchronously deletes a document from Firestore with retry."""
        if not self.config.is_valid():
            return False
            
        url = f"{self.firestore_url}/{collection}/{document_id}?key={self.config.API_KEY}"
        headers = {}
        if self.id_token:
            headers["Authorization"] = f"Bearer {self.id_token}"
            
        for attempt in range(3):
            try:
                response = self.session.delete(url, headers=headers, timeout=15)
                response.raise_for_status()
                logger.debug(f"Successfully deleted {collection}/{document_id}")
                return True
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Firestore delete failed for {collection}/{document_id}: {e}")
                    return False
                time.sleep(0.3 * (attempt + 1))
        return False

