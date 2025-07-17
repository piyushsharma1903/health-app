import React from 'react';
import './SummaryModal.css';

const SummaryModal = ({ isOpen, onClose, summary, reportType, reportDate }) => {
  if (!isOpen) return null;

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const formatSummary = (text) => {
    if (!text) return 'No summary available';
    
    // Split by double newlines for paragraphs
    const paragraphs = text.split('\n\n');
    
    return paragraphs.map((paragraph, index) => {
      // Check if paragraph contains bullet points or lists
      if (paragraph.includes('•') || paragraph.includes('-') || paragraph.includes('*')) {
        const lines = paragraph.split('\n');
        return (
          <div key={index} className="summary-section">
            {lines.map((line, lineIndex) => (
              <div key={lineIndex} className="summary-line">
                {line.trim()}
              </div>
            ))}
          </div>
        );
      }
      
      return (
        <p key={index} className="summary-paragraph">
          {paragraph.trim()}
        </p>
      );
    });
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-content">
        <div className="modal-header">
          <div className="modal-title">
            <h3>AI Summary</h3>
            <div className="modal-subtitle">
              {reportType && <span className="report-type">{reportType.toUpperCase()}</span>}
              {reportDate && <span className="report-date">{reportDate}</span>}
            </div>
          </div>
          <button className="close-button" onClick={onClose}>
            &times;
          </button>
        </div>
        <div className="modal-body">
          <div className="summary-content">
            {formatSummary(summary)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryModal;