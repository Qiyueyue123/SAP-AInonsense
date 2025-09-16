import React, { useState, useEffect, useRef } from "react";
import SidebarNav from "../components/sidenav";
import { paraphraseAPI } from "../utils/api";
import { convertContentToText } from "../utils/contentHelpers";
import ResumeSection from "../components/ResumeSection";
import JsonToReadableText from "../components/JsonToReadableText"; // Import your readable text renderer
import "./ResumeEditor.css";
import html2pdf from "html2pdf.js";

export default function ResumeEditor() {
  const [localResume, setLocalResume] = useState(null); // Initial null for loading
  const resumeRef = useRef();

  useEffect(() => {
    const fetchResumeData = async () => {
      try {
        const response = await api.get("/resume-editor"); // Your API endpoint
        setLocalResume(response.data); // Set raw JSON object (not array, as your new format is object of arrays)
        console.log("Resume data loaded:", response.data);
      } catch (err) {
        console.error("Loading failed:", err);
      }
    };
    fetchResumeData();
  }, []);

  const addSection = () => {
    // This function may not directly apply to your new JSON schema,
    // as sections are keys in an object, not an array.
    // For now, leave empty or implement as needed.
  };

  const handleDownloadPDF = () => {
    if (!resumeRef.current) return;
    const options = {
      margin: 0.5,
      filename: "resume.pdf",
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2, logging: false },
      jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
    };
    html2pdf().set(options).from(resumeRef.current).save();
  };

  return (
    <div className="resume-editor-container">
      <SidebarNav />
      <main className="resume-editor-main">
        <h1>Resume Editor</h1>
        <div className="buttons-container">
          <button onClick={addSection} className="add-section-button" disabled>
            + Add Section
          </button>
          <button onClick={handleDownloadPDF} className="download-pdf-button">
            Download as PDF
          </button>
        </div>
        <div
          ref={resumeRef}
          id="resume-to-pdf"
          style={{ backgroundColor: "white", padding: "1rem", borderRadius: "8px" }}
        >
          {localResume ? (
            <JsonToReadableText data={localResume} />
          ) : (
            <p>Loading resume data...</p>
          )}
        </div>
      </main>
    </div>
  );
}
