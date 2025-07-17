import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Table.css";
import { FaFileAlt } from "react-icons/fa";
import ReportModal from "../ReportModal/ReportModal";
import SummaryModal from "../SummaryModal/SummaryModal";
import { getAuth } from "firebase/auth";

const ReportTable = () => {
  const [reports, setReports] = useState([]);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [summaryModalOpen, setSummaryModalOpen] = useState(false);
  const [modalImage, setModalImage] = useState(null);
  const [selectedSummary, setSelectedSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReports = async (user) => {
  try {
    setLoading(true);
    setError(null);
    
    console.log("🔍 User object:", user);
    console.log("🔍 User email:", user.email);
    console.log("🔍 User UID:", user.uid);
    
    // Get a fresh token
    const idToken = await user.getIdToken(true);
    console.log("🎫 Token generated (first 50 chars):", idToken.substring(0, 50) + "...");
    console.log("🎫 Token length:", idToken.length);
    
    // Verify token format
    const tokenParts = idToken.split('.');
    console.log("🎫 Token parts count:", tokenParts.length);
    
    const headers = {
      Authorization: `Bearer ${idToken}`,
      'Content-Type': 'application/json',
    };
    
    console.log("📡 Request headers:", headers);
    console.log("📡 Making request to: http://localhost:8000/api/reports/");

    const response = await axios.get("http://localhost:8000/api/reports/", {
      headers: headers,
    });

    setReports(response.data);
    console.log("✅ Reports fetched successfully:", response.data);
  } catch (err) {
    console.error("❌ Full error object:", err);
    console.error("❌ Error response:", err.response);
    console.error("❌ Error status:", err.response?.status);
    console.error("❌ Error data:", err.response?.data);
    
    if (err.response?.status === 401) {
      setError("Authentication failed. Please log in again.");
    } else {
      setError("Failed to fetch reports. Please try again.");
    }
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    const auth = getAuth();
    
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        // Wait a bit to ensure the user is fully authenticated
        setTimeout(() => {
          fetchReports(user);
        }, 500);
      } else {
        console.warn("⚠️ User is not logged in");
        setReports([]);
        setLoading(false);
        setError("Please log in to view reports.");
      }
    });

    return () => unsubscribe();
  }, []);

  const handleDelete = async (id) => {
    const auth = getAuth();
    const user = auth.currentUser;
    
    if (!user) {
      alert("You must be logged in to delete a report.");
      return;
    }

    if (!window.confirm("Delete this report?")) {
      return;
    }

    try {
      const idToken = await user.getIdToken(true);
      
      await axios.delete(`http://localhost:8000/api/reports/${id}/`, {
        headers: {
          Authorization: `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
      });

      setReports((prev) => prev.filter((report) => report.id !== id));
      console.log("✅ Report deleted successfully");
    } catch (err) {
      console.error("❌ Deletion failed:", err);
      
      if (err.response?.status === 401) {
        alert("Authentication failed. Please log in again.");
      } else {
        alert("Failed to delete report. Please try again.");
      }
    }
  };

  const handleViewSummary = (report) => {
    setSelectedSummary({
      summary: report.ai_summary,
      reportType: report.report_type,
      reportDate: report.report_date,
    });
    setSummaryModalOpen(true);
  };

  const handleRetry = () => {
    const auth = getAuth();
    const user = auth.currentUser;
    if (user) {
      fetchReports(user);
    }
  };

  if (loading) {
    return (
      <div className="report-table-container">
        <h2>Reports History</h2>
        <div style={{ textAlign: "center", padding: "20px" }}>
          Loading reports...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="report-table-container">
        <h2>Reports History</h2>
        <div style={{ textAlign: "center", padding: "20px", color: "red" }}>
          {error}
          <br />
          <button 
            onClick={handleRetry} 
            style={{ 
              marginTop: "10px", 
              padding: "8px 16px", 
              backgroundColor: "#007bff", 
              color: "white", 
              border: "none", 
              borderRadius: "4px", 
              cursor: "pointer" 
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="report-table-container">
      <h2>Reports History</h2>
      <table className="report-table">
        <thead>
          <tr>
            <th>Report Date</th>
            <th>Report Type</th>
            <th>AI Summary</th>
            <th>Report Image</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {reports.length > 0 ? (
            reports.map((report) => (
              <tr key={report.id}>
                <td>{report.report_date || "N/A"}</td>
                <td>{report.report_type}</td>
                <td>
                  <button
                    className="view-btn"
                    onClick={() => handleViewSummary(report)}
                  >
                    View
                  </button>
                </td>
                <td>
                  <button
                    onClick={() => {
                      setModalImage(`http://localhost:8000${report.original_file}`);
                      setReportModalOpen(true);
                    }}
                    style={{
                      backgroundColor: "transparent",
                      color: "#007bff",
                      padding: "6px 12px",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                    }}
                    title="View Report Image"
                  >
                    <FaFileAlt />
                  </button>
                </td>
                <td>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(report.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" style={{ textAlign: "center" }}>
                No reports yet
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <ReportModal
        isOpen={reportModalOpen}
        onClose={() => setReportModalOpen(false)}
        imageUrl={modalImage}
      />

      <SummaryModal
        isOpen={summaryModalOpen}
        onClose={() => setSummaryModalOpen(false)}
        summary={selectedSummary?.summary}
        reportType={selectedSummary?.reportType}
        reportDate={selectedSummary?.reportDate}
      />
    </div>
  );
};

export default ReportTable;