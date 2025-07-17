import React, { useState } from "react";
import { auth } from '../../pages/firebase/firebaseConfig'; // Adjust path as needed

const UploadForm = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [reportType, setReportType] = useState("");
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const reportTypes = [
    { value: "lab", label: "Lab" },
    { value: "ct", label: "CT" },
    { value: "mri", label: "MRI" }
  ];

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile || !reportType) {
      alert("Please select a file and report type.");
      return;
    }

    setUploading(true);
    setUploadStatus("Uploading...");

    try {
      // Get Firebase auth token
      const user = auth.currentUser;
      if (!user) {
        throw new Error("Please log in first");
      }

      const token = await user.getIdToken();
      
      // Create FormData
      const formData = new FormData();
      formData.append('original_file', selectedFile);
      formData.append('report_type', reportType);

      // Make API call to backend
      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }

      const result = await response.json();
      
      setUploadStatus("✅ Report uploaded and processed successfully!");
      setSelectedFile(null);
      setReportType("");
      
      // Optionally show AI summary
      if (result.ai_summary) {
        console.log("AI Summary:", result.ai_summary);
      }

    } catch (error) {
      console.error("Upload error:", error);
      setUploadStatus(`❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb',
      fontFamily: 'system-ui, -apple-system, sans-serif' 
    }}>
      {/* Main Content */}
      <div style={{
        maxWidth: '672px',
        margin: '0 auto',
        padding: '64px 24px 0'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            fontSize: '30px',
            fontWeight: '700',
            color: '#111827',
            marginBottom: '16px',
            margin: '0 0 16px 0'
          }}>
            Upload Your Health Report
          </h1>
          <p style={{
            color: '#6b7280',
            fontSize: '16px',
            margin: '0'
          }}>
            Upload your lab reports (like blood tests) to receive an AI-generated summary.
          </p>
        </div>

        {/* Status Message */}
        {uploadStatus && (
          <div style={{
            padding: '12px',
            marginBottom: '24px',
            borderRadius: '6px',
            backgroundColor: uploadStatus.includes('✅') ? '#dcfce7' : uploadStatus.includes('❌') ? '#fef2f2' : '#fef3c7',
            color: uploadStatus.includes('✅') ? '#166534' : uploadStatus.includes('❌') ? '#991b1b' : '#92400e',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            {uploadStatus}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Report Type Dropdown */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Select Report Type
            </label>
            <div style={{ position: 'relative' }}>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                disabled={uploading}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  backgroundColor: 'white',
                  appearance: 'none',
                  cursor: uploading ? 'not-allowed' : 'pointer',
                  paddingRight: '32px'
                }}
              >
                <option value="">Select Report Type</option>
                {reportTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <div style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                pointerEvents: 'none'
              }}>
                <svg style={{ width: '20px', height: '20px', color: '#9ca3af' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* File Upload Area */}
          <div>
            <div
              style={{
                position: 'relative',
                border: dragActive ? '2px dashed #3b82f6' : '2px dashed #d1d5db',
                borderRadius: '8px',
                padding: '32px',
                textAlign: 'center',
                backgroundColor: dragActive ? '#eff6ff' : 'transparent',
                cursor: uploading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: uploading ? 0.6 : 1
              }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                disabled={uploading}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  opacity: 0,
                  cursor: uploading ? 'not-allowed' : 'pointer'
                }}
              />
              
              {selectedFile ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    backgroundColor: '#dcfce7',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <svg style={{ width: '24px', height: '24px', color: '#16a34a' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p style={{ fontSize: '14px', fontWeight: '500', color: '#111827', margin: '0' }}>
                    {selectedFile.name}
                  </p>
                  <p style={{ fontSize: '12px', color: '#6b7280', margin: '0' }}>
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    backgroundColor: '#f3f4f6',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <svg style={{ width: '24px', height: '24px', color: '#9ca3af' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <p style={{ fontSize: '18px', fontWeight: '500', color: '#111827', margin: '0' }}>
                      Drag and drop your files here
                    </p>
                    <p style={{ fontSize: '14px', color: '#6b7280', margin: '4px 0 0 0' }}>Or</p>
                  </div>
                  <button
                    type="button"
                    disabled={uploading}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '8px 16px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#374151',
                      backgroundColor: 'white',
                      cursor: uploading ? 'not-allowed' : 'pointer',
                      boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
                    }}
                  >
                    Browse Files
                  </button>
                </div>
              )}
            </div>
            
            <p style={{
              marginTop: '8px',
              fontSize: '14px',
              color: '#6b7280',
              textAlign: 'center',
              margin: '8px 0 0 0'
            }}>
              Supported formats: PDF, JPG, PNG. Max file size: 10MB
            </p>
          </div>

          {/* Submit Button */}
          <div style={{ paddingTop: '16px' }}>
            <button
              onClick={handleSubmit}
              disabled={uploading || !selectedFile || !reportType}
              style={{
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                padding: '12px 16px',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                color: 'white',
                backgroundColor: (uploading || !selectedFile || !reportType) ? '#9ca3af' : '#2563eb',
                cursor: (uploading || !selectedFile || !reportType) ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
            >
              {uploading ? (
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{
                    width: '16px',
                    height: '16px',
                    border: '2px solid transparent',
                    borderTop: '2px solid white',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    marginRight: '8px'
                  }}></div>
                  Uploading...
                </div>
              ) : (
                'Upload Report'
              )}
            </button>
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default UploadForm;