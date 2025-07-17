// src/firebase/firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAwoi0qP4BpD0tR_vXCOY4Q3Rw1i4ukMrw",
  authDomain: "health-app-v0-5be85.firebaseapp.com",
  projectId: "health-app-v0-5be85",
  storageBucket: "health-app-v0-5be85.firebasestorage.app",
  messagingSenderId: "400246182251",
  appId: "1:400246182251:web:0759c996bf7286fa4dfc2e"
};
// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// Export auth + Google provider
export { auth, provider };