export function convertContentToText(content) {
  if (!content) return "";
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (typeof item === "string") return item;
        if (typeof item === "object" && item !== null) {
          return Object.values(item).join(", ");
        }
        return "";
      })
      .join("\n\n");
  }
  return "";
}