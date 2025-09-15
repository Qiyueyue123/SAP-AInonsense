import React from "react";

function formatNewResumeData(data) {
  let output = "";

  for (const [sectionKey, entries] of Object.entries(data)) {
    const header = sectionKey.replace(/_/g, " ").toUpperCase();
    output += `[${header}]\n\n`;

    entries.forEach((entry) => {
      output += `Date: ${entry.date}\n`;
      output += `Name: ${entry.name}\n`;
      output += `Description: ${entry.description}\n\n`;
    });
  }

  return output.trim();
}

const JsonToReadableText = ({ data }) => {
  if (!data) return null;

  const readableText = formatNewResumeData(data);

  return (
    <pre style={{ whiteSpace: "pre-wrap", fontFamily: "inherit" }}>
      {readableText}
    </pre>
  );
};

export default JsonToReadableText;
