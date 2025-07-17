import React from "react";
import { signInWithPopup } from "firebase/auth";
import { auth, provider } from "./firebaseConfig";
import "./Login.css";

const Login = ({ setUser }) => {
  const handleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      console.log("✅ Logged in:", user);
      setUser({
        name: user.displayName,
        email: user.email,
        uid: user.uid,
        photo: user.photoURL,
      });
    } catch (error) {
      console.error("❌ Login failed:", error);
      alert("Login error. Try again.");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-heading">Welcome to HealthApp</h1>
        <p className="login-subtext">Know yourself. Stay aware. Be in control.</p>
        <button className="google-login-btn" onClick={handleLogin}>
          <img src="https://img.icons8.com/color/16/google-logo.png" alt="Google" />
          Sign in with Google
        </button>
      </div>
    </div>
  );
};

export default Login;
