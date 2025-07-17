import React from "react";
import "./Profile.css";

const Profile = ({ user, handleLogout }) => {
  if (!user) {
    return <p className="profile-loading">Loading...</p>;
  }

  return (
    <div className="profile-container">
      <img className="profile-avatar" src={user.photo} alt="User Avatar" />
      <h2 className="profile-name">{user.name}</h2>
      <p className="profile-email">{user.email}</p>
      <button className="profile-logout-btn" onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
};

export default Profile;
