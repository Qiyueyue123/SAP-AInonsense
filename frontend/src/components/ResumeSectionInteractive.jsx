import React, { useState, useRef, useEffect } from "react";
import { convertContentToText } from "../utils/contentHelpers";

const ResumeSectionInteractive = ({ section, onSave, onParaphrase }) => {
  const [text, setText] = useState(convertContentToText(section.content));

  const [editing, setEditing] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    setText(convertContentToText(section.content));
  }, [section]);

  const handleSave = () => {
    
    onSave(section.header, text);
    setEditing(false);
  };

  const handleCancel = () => {
    setText(convertContentToText(section.content));
    setEditing(false);
  };

  const handleParaphrase = async () => {
    if (!textareaRef.current) return;
    const textarea = textareaRef.current;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end).trim();
    if (!selectedText) {
      alert("Please select the text you want to paraphrase.");
      return;
    }
    const confirmed = window.confirm(`Paraphrase the selected text?\n\n"${selectedText}"`);
    if (!confirmed) return;

    if (onParaphrase) {
      const paraphrasedText = await onParaphrase(section.header, text, selectedText);
      if (paraphrasedText) {
        const before = text.substring(0, start);
        const after = text.substring(end);
        setText(before + paraphrasedText + after);
      }
    }
  };

  return (
    <section style={{ marginBottom: 20 }}>
      <h2>{section.header}</h2>
      {editing ? (
        <>
          <textarea
            ref={textareaRef}
            style={{ width: "100%", minHeight: 120 }}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button onClick={handleSave} style={{ marginRight: 8 }}>
            Save
          </button>
          <button onClick={handleCancel} style={{ marginRight: 8 }}>
            Cancel
          </button>
          <button onClick={handleParaphrase}>Paraphrase Selection</button>
        </>
      ) : (
        <div
          onClick={() => setEditing(true)}
          style={{
            whiteSpace: "pre-wrap",
            border: "1px solid #ddd",
            padding: 8,
            cursor: "pointer",
          }}
        >
          {text || "(Click to edit text)"}
        </div>
      )}
    </section>
  );
};

export default ResumeSectionInteractive;
