// src/components/Navbar.js
import React from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/">Upload</Link>
        <Link to="/reports">Reports</Link>
      </div>

      <div className="navbar-center">
        <span className="navbar-tagline">Stay Informed.</span>
      </div>

      <div className="navbar-right">
        <Link to="/profile">Profile</Link>
      </div>
    </nav>
  );
};

export default Navbar;
