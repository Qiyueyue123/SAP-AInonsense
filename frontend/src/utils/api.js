export async function paraphraseAPI(header, content, text_rephrase) {
  try {
    const response = await fetch("/api/paraphrase", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        header,
        content,
        text_rephrase,
        mode: 1,
      }),
    });
    if (!response.ok) throw new Error("Failed to paraphrase");
    const data = await response.json();
    return data.paraphrased_text || data;
  } catch (error) {
    alert("Error paraphrasing text. Please try again.");
    console.error(error);
    return null;
  }
}
