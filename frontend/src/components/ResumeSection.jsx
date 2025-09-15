import React, { useState } from "react";
import { sectionToText } from "../utils/convertResumeJSON";

const ResumeSection = ({ section, onSave }) => {
  const [text, setText] = useState(sectionToText(section));
  const [editing, setEditing] = useState(false);

  const handleSave = () => {
    onSave(section.header, text)
    setEditing(false);
  };

  const handleCancel = () => {
    setText(sectionToText(section));
    setEditing(false);
  };

  return (
    <section style={{ marginBottom: 20 }}>
      <h2>{section.header}</h2>
      {editing ? (
        <>
          <textarea
            style={{ width: "100%", minHeight: 120 }}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button onClick={handleSave} style={{ marginRight: 8 }}>Save</button>
          <button onClick={handleCancel}>Cancel</button>
        </>
      ) : (
        <div
          onClick={() => setEditing(true)}
          style={{ whiteSpace: "pre-wrap", border: "1px solid #ddd", padding: 8, cursor: "pointer" }}
        >
          {text || "(Click to edit text)"}
        </div>
      )}
    </section>
  );
};

export default ResumeSection;
