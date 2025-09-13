import { useAuth } from "../AuthContext";
import { useState } from "react";
import api from '../axios.js';

const ResumeUpload = () => {
  const [fileName, setFileName] = useState("");  // Selected file name
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
    }
    setFile(file);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }
    const formData = new FormData();
    formData.append("resume", file);

    setUploading(true);
    setUploadError("");

    try {
      const response = await api.post("/upload-resume", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("Upload successful:", response.data);
      // Optionally clear file input after success
      setFile(null);
      setFileName("");
    } catch (err) {
      console.error("Upload failed:", err);
      setUploadError("Failed to upload resume. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page-center">
      <div className="auth-card">
        <p>Upload Resume</p>
        <form onSubmit={handleUpload}>
          <input 
            type="file" 
            accept="application/pdf" 
            onChange={handleFileChange} 
            style={{ marginBottom: "10px" }} 
          />
          {fileName && (
            <p>File selected: <strong>{fileName}</strong></p>
          )}
          {uploadError && <p className="error">{uploadError}</p>}
          <button type="submit" disabled={uploading}>
            {uploading ? "Uploading..." : "Upload Resume"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResumeUpload;
