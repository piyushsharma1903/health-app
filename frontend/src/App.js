// src/App.js
import React, { useState } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import Navbar from "./components/Navbar/Navbar";
import Reports from "./pages/Reports";
import UploadForm from "./components/UploadForm/UploadForm";
import Login from "./pages/firebase/Login";
import Profile from "./pages/Profile/Profile";
import { signOut } from "firebase/auth";
import { auth } from "./pages/firebase/firebaseConfig";

function App() {
  const [user, setUser] = useState(null); // 🔐 Auth state
  const navigate = useNavigate();         // 🔁 For redirect after logout

  const handleLogout = async () => {
    await signOut(auth);
    setUser(null);
    navigate("/"); // 👋 Redirect to home/login after logout
  };

  return (
    <>
      {!user ? (
        // 🔒 No user → Show login page only
        <Routes>
          <Route path="*" element={<Login setUser={setUser} />} />
        </Routes>
      ) : (
        <>
          <Navbar />
          <Routes>
            <Route path="/" element={<UploadForm user={user} />} />
            <Route path="/reports" element={<Reports user={user} />} />
            <Route
              path="/profile"
              element={<Profile user={user} handleLogout={handleLogout} />}
            />
          </Routes>
        </>
      )}
    </>
  );
}

export default App;
