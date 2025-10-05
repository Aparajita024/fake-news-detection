import { useState } from "react";
import axios from "axios";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/detect", { text });
      setResult(res.data);
    } catch (error) {
      console.error("Error fetching:", error);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Fake News Detector (Local)</h1>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste news text here..."
        rows="5"
        cols="50"
      />
      <br />
      <button onClick={handleSubmit}>Check</button>

      {result && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Results</h2>
          <p><b>Query:</b> {result.query}</p>
          <p><b>Suspicious:</b> {result.suspicious_parts.join(", ")}</p>
          <p><b>Confidence Score:</b> {Math.round(result.confidence_score * 100)}%</p>
          <p><b>Explanation:</b> {result.explanation}</p>
          <ul>
            {result.related_articles.map((link, idx) => (
              <li key={idx}><a href={link} target="_blank" rel="noreferrer">{link}</a></li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;