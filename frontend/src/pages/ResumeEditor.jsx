import React, { useState, useEffect, useRef } from "react";
import SidebarNav from "../components/sidenav";
import { paraphraseAPI } from "../utils/api";
import { convertContentToText } from "../utils/contentHelpers";
import ResumeSection from "../components/ResumeSection";
import "./ResumeEditor.css";
import html2pdf from "html2pdf.js";
import JsonToReadableText from "../components/JsonToReadableText";

export default function ResumeEditor() {
  const [localResume, setLocalResume] = useState([]);
  const resumeRef = useRef();

  useEffect(() => {
    const fetchResumeData = async () => {
      try {
        const response = await api.get("/resume-editor");
        console.log("Upload successful:", response.data);
      } catch (err) {
        console.error("Upload failed:", err);
        setUploadError("Failed to upload resume. Please try again.");
      } finally {
        setUploading(false);
      }
    };
    fetchResumeData();
  }, []);

  const addSection = () => {
    setLocalResume([
      ...localResume,
      { header: "New Section", content: [] },
    ]);
  };

  const updateSection = (header, text) => {
    setLocalResume((prev) =>
      prev.map((section) =>
        section.header === header
          ? section : { ...section, _contentText: text }
          
      )
    );
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
          <button onClick={addSection} className="add-section-button">
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
          {localResume.map((section, idx) => (
            <ResumeSection
              key={section.header + idx}
              section={section}
              onSave={updateSection}
              onParaphrase={paraphraseAPI}
            />
          ))}
        </div>
      </main>
    </div>
  );
}
