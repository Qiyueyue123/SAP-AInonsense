import React, { useEffect, useState } from "react";
import Sidenav from "../components/sidenav";
import "./ResumeEditor.css";
import api from '../axios.js';
import { useAuth } from "../AuthContext";

// Helper to get selected text inside a textarea by its id
function getSelectedText(textareaId) {
  const textarea = document.getElementById(textareaId);
  if (!textarea) return "";
  return textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
}

// Helper to replace selected text inside textarea content and update state
function replaceSelectedText(text, textareaId, newText, updateValueCallback) {
  const textarea = document.getElementById(textareaId);
  if (!textarea) return;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const before = text.substring(0, start);
  const after = text.substring(end);
  const updated = before + newText + after;
  updateValueCallback(updated);
}

function ResumeEditor() {
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const { user } = useAuth();
  const { uid } = user;

  // Local editable copy: keys map to string content for editing
  const [editableContent, setEditableContent] = useState({});

  useEffect(() => {
    const fetchResume = async () => {
      try {
        const response = await api.get("/resume-editor", { params: { uid } });
        setResume(response.data);

        // Initialize editableContent with formatted strings per section
        const initialEditState = {};
        for (const [sectionKey, items] of Object.entries(response.data)) {
          initialEditState[sectionKey] = items.map(item =>
            `Date: ${item.date}\nName: ${item.name}\nDescription: ${item.description}\n`
          ).join("\n");
        }
        setEditableContent(initialEditState);

      } catch (err) {
        setError("Failed to fetch resume. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchResume();
  }, [uid]);

  // Toggle edit mode
  const toggleEdit = () => {
    setIsEditing((prev) => !prev);
  };

  // Handle textarea value change per section
  const handleChange = (sectionKey, value) => {
    setEditableContent((prev) => ({
      ...prev,
      [sectionKey]: value,
    }));
  };

  // Convert editable text back to JSON structure
  const parseEditedContentToJSON = (editable) => {
    const parsed = {};
    for (const [sectionKey, text] of Object.entries(editable)) {
      const items = text.trim().split(/\n\s*\n/); // Split by blank line between items
      const parsedItems = items.map(itemText => {
        const lines = itemText.split("\n");
        const obj = {};
        lines.forEach(line => {
          const [key, ...rest] = line.split(":");
          if (!key || rest.length === 0) return;
          const val = rest.join(":").trim();
          if (key.toLowerCase() === "date") obj.date = val;
          else if (key.toLowerCase() === "name") obj.name = val;
          else if (key.toLowerCase() === "description") obj.description = val;
        });
        return obj;
      }).filter(obj => Object.keys(obj).length > 0);
      parsed[sectionKey] = parsedItems;
    }
    return parsed;
  };

  // On Save: parse text and post update to backend
  const handleSave = async () => {
    const updatedJSON = parseEditedContentToJSON(editableContent);
    console.log("Saving to backend:", updatedJSON);
    try {
      await api.post("/resume-editor/update", { resume: updatedJSON }); // no uid, backend reads from token
      setResume(updatedJSON);
      setIsEditing(false);
      alert("Resume saved successfully.");
    } catch (err) {
      console.error("Failed to save resume:", err);
      alert("Failed to save resume. Please try again.");
    }
  };

  // On paraphrase button click per section
  const handleParaphrase = async (sectionKey, textareaId) => {
    const selectedText = getSelectedText(textareaId);
    if (!selectedText) {
      alert("Please select text to paraphrase.");
      return;
    }
    try {
      const res = await api.post("/resume-editor/paraphrase", {
        header: sectionKey,
        content: editableContent[sectionKey],
        text_to_rephrase: selectedText,
      });
      const paraphrased = res.data.paraphrased_text;
      if (paraphrased) {
        replaceSelectedText(editableContent[sectionKey], textareaId, paraphrased, (updated) =>
          handleChange(sectionKey, updated)
        );
      } else {
        alert("No paraphrased text returned.");
      }
    } catch (err) {
      console.error("Paraphrase failed:", err);
      alert("Failed to paraphrase text.");
    }
  };

  if (loading) return <p>Loading resume...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div className="resume-editor-container">
      <Sidenav />
      <main className="resume-editor-main">
        <h1>Resume Editor</h1>

        <div className="buttons-container">
          <button onClick={toggleEdit} className="edit-button">
            {isEditing ? "Cancel" : "Edit"}
          </button>
          {isEditing && (
            <>
              <button onClick={handleSave} className="save-button">
                Save
              </button>
              <button
                onClick={() => {
                  // Loop through all sections to find first selected text and paraphrase it globally
                  for (const [sectionKey] of Object.entries(editableContent)) {
                    const textareaId = `textarea-${sectionKey}`;
                    const selectedText = getSelectedText(textareaId);
                    if (selectedText) {
                      handleParaphrase(sectionKey, textareaId);
                      return;
                    }
                  }
                  alert("Please select text inside any section to paraphrase.");
                }}
                className="paraphrase-global-button"
                style={{ marginLeft: "10px" }}
              >
                Paraphrase Selected Text (Global)
              </button>
            </>
          )}
        </div>

        <div id="resume-content-area" style={{ whiteSpace: "pre-wrap" }}>
          {Object.entries(editableContent).map(([sectionKey, text]) => {
            const textareaId = `textarea-${sectionKey}`;
            return (
              <section key={sectionKey} style={{ marginBottom: "2rem" }}>
                <h2>{sectionKey.replace(/_/g, " ").toUpperCase()}</h2>
                {isEditing ? (
                  <>
                    <textarea
                      id={textareaId}
                      value={text}
                      onChange={(e) => handleChange(sectionKey, e.target.value)}
                      style={{
                        width: "100%",
                        minHeight: "8rem",
                        fontFamily: "monospace",
                        fontSize: "1rem",
                        padding: "1rem",
                        borderRadius: "6px",
                        border: "1px solid #ccc",
                      }}
                    />
                    <button
                      onClick={() => handleParaphrase(sectionKey, textareaId)}
                      style={{ marginTop: "0.5rem" }}
                    >
                      Paraphrase Selected
                    </button>
                  </>
                ) : (
                  <pre style={{ whiteSpace: "pre-wrap", fontSize: "1.1rem" }}>{text}</pre>
                )}
              </section>
            );
          })}
        </div>
      </main>
    </div>
  );
}

export default ResumeEditor;
