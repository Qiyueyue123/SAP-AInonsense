import React, { useState } from "react";

/**
 * Recursively render editable inputs for JSON content.
 */
function EditableJsonField({ label, value, onChange }) {
  if (Array.isArray(value)) {
    return (
      <div style={{ marginLeft: 20 }}>
        <strong>{label}:</strong>
        {value.map((item, index) => (
          <EditableJsonField
            key={index}
            label={`${label} #${index + 1}`}
            value={item}
            onChange={(newVal) => {
              const newArr = [...value];
              newArr[index] = newVal;
              onChange(newArr);
            }}
          />
        ))}
        <button onClick={() => onChange([...value, ""])}>Add {label}</button>
      </div>
    );
  } else if (typeof value === "object" && value !== null) {
    return (
      <div style={{ marginLeft: 20 }}>
        <strong>{label}:</strong>
        {Object.entries(value).map(([key, val]) => (
          <EditableJsonField
            key={key}
            label={key}
            value={val}
            onChange={(newVal) =>
              onChange({ ...value, [key]: newVal })
            }
          />
        ))}
      </div>
    );
  } else {
    // primitive: string or number
    return (
      <div style={{ marginLeft: 20 }}>
        <label>
          {label}:
          <input
            type="text"
            value={value || ""}
            onChange={(e) => onChange(e.target.value)}
            style={{ marginLeft: 10, width: "80%" }}
          />
        </label>
      </div>
    );
  }
}

/**
 * Component to render editable resume JSON from backend schema.
 */
const EditableResume = ({ data }) => {
  // Local state to hold editable content copy
  const [editableData, setEditableData] = useState(data);

  // Handler for section content updates
  const updateSectionContent = (sectionKey, newContent) => {
    setEditableData((prev) => ({
      ...prev,
      [sectionKey]: {
        ...prev[sectionKey],
        content: newContent,
      },
    }));
  };

  return (
    <div>
      {Object.entries(editableData).map(([sectionKey, section]) => (
        <section key={sectionKey} style={{ marginBottom: 40 }}>
          <h2>{section.header}</h2>
          <EditableJsonField
            label="Content"
            value={section.content}
            onChange={(newVal) => updateSectionContent(sectionKey, newVal)}
          />
        </section>
      ))}
    </div>
  );
};

export default EditableResume;
