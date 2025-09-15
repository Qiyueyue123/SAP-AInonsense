import { useAuth } from "../AuthContext";
import { useState } from "react";
import SidebarNav from "../components/sidenav"; 
import api from '../axios.js';

const ResumeUpload = () => {
  const [fileName, setFileName] = useState("");  // State to store the selected file name
  const [file, setFile] = useState(null); 
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const { user } = useAuth(); // Get the user from AuthContext
  const { token, uid } = user; // Extract the token and uid from user object

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];  // Get the first file (in case multiple files are selected)
    if (file) {
      setFileName(file.name);  // Set the file name state to display it
    }
    setFile(file)
  };
  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file); // "resume" is the key the backend expects
    formData.append("uid",uid)

    setUploading(true);
    setUploadError("");

    try {
      const response = await api.post("/upload-resume", formData, {
        headers: {
          "Content-Type": "multipart/form-data", // Content type for file upload
        },
      });

      console.log("Upload successful:", response.data);
      // Handle success (e.g., show a success message)
    } catch (err) {
      console.error("Upload failed:", err);
      setUploadError("Failed to upload resume. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page-center">
      <SidebarNav />
      <div className="auth-card">
        <p>Upload Resume</p>
        <form onSubmit={handleUpload}>
          <input 
            type="file" 
            accept="application/pdf"  // Only accept PDFs
            onChange={handleFileChange}  // Handle file selection
            style={{ marginBottom: "10px" }} 
          />
          {fileName && (
            <p>File selected: <strong>{fileName}</strong></p>  // Display selected file name
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