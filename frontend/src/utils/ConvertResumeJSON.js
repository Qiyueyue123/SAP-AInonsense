// frontend/src/utils/convertResumeJSON.js

export function sectionToText(section) {
  if (!section || !section.content) return "";

  const { header, content } = section;

  function processContent(data) {
    if (Array.isArray(data)) {
      return data
        .map(item => processContent(item))
        .filter(Boolean)
        .join("\n\n");
    }

    if (typeof data === "object" && data !== null) {
      return Object.entries(data)
        .map(([key, val]) => {
          if (Array.isArray(val)) {
            const joinedArray = val.map(v => (typeof v === "object" ? processContent(v) : v)).join("; ");
            return `${capitalize(key)}: ${joinedArray}`;
          } else if (typeof val === "object") {
            return `${capitalize(key)}:\n${processContent(val)}`;
          } else {
            return `${capitalize(key)}: ${val}`;
          }
        })
        .filter(Boolean)
        .join("\n");
    }

    return data ? data.toString() : "";
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, " ");
  }

  return `${header}\n\n${processContent(content)}`;
}
