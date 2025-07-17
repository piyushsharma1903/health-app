import React from 'react';
import './ReportModal.css';

const ReportModal = ({ isOpen, onClose, imageUrl }) => {
  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h3>Medical Report</h3>
          <button className="close-button" onClick={onClose}>
            &times;
          </button>
        </div>
        <div className="modal-body">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt="Medical Report"
              className="report-image"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.parentNode.innerHTML = '<p>Error loading image</p>';
              }}
            />
          ) : (
            <p>No image available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportModal;