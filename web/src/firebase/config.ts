import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// The web app uses the same Firebase config as the backend.
// We use Vite environment variables (VITE_ prefix).
// Use Vite environment variables (VITE_ prefix) with valid default fallbacks
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyAC_0TAIKxKvRMvYG4XGZjQAc3bLUDEyuM",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "edge-ai-attendance-system.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "edge-ai-attendance-system",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "edge-ai-attendance-system.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "505945196859",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:505945196859:web:74e67decdb2faf84d2cf1e",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-88JTDS0VLK"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
