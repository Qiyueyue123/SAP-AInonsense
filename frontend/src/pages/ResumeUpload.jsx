import React, { useState } from 'react';
import './ResumeUpload.css';

export default function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus('');
  };

  const onUploadClick = () => {
    if (!file) {
      setStatus('Please select a file to upload');
      return;
    }
    setStatus(`Ready to upload: ${file.name}`);
    // Add your upload logic here later
  };

  return (
    <div className="resume-upload-container">
      <div className="resume-upload-box">
        <h2 className="resume-upload-title">Upload Your Resume</h2>
        <div className="resume-upload-controls">
          <input
            type="file"
            onChange={onFileChange}
            accept=".pdf,.doc,.docx"
            className="resume-upload-input"
          />
          <button onClick={onUploadClick} className="resume-upload-button">
            Upload
          </button>
        </div>
        {status && <div className="resume-upload-status">{status}</div>}
      </div>
    </div>
  );
}
