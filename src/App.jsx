import { useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "";

const MAX_FILE_SIZE = 4 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ["pdf", "docx", "txt"];

/* =========================================================
   FILE VALIDATION
========================================================= */

function validateFiles(files) {
  if (!files || files.length === 0) {
    throw new Error("Please select at least one document.");
  }

  for (const file of files) {
    if (file.size > MAX_FILE_SIZE) {
      throw new Error(`${file.name} is larger than 4 MB.`);
    }

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      throw new Error(
        `${file.name} is not supported. Please upload PDF, DOCX, or TXT files.`,
      );
    }
  }
}

/* =========================================================
   API REQUEST HELPER
========================================================= */

async function apiRequest(endpoint, formData) {
  let response;

  try {
    response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new Error(
      `Unable to connect to the backend. Make sure the FastAPI server is running.`,
    );
  }

  /*
   * IMPORTANT:
   * Do not directly call response.json().
   *
   * The backend/Vercel may sometimes return plain text such as:
   * "Command failed: ..."
   *
   * Calling response.json() on that causes:
   * Unexpected token 'C'...
   */

  const contentType = response.headers.get("content-type") || "";

  let data;

  if (contentType.includes("application/json")) {
    try {
      data = await response.json();
    } catch {
      throw new Error(
        `The server returned invalid JSON (HTTP ${response.status}).`,
      );
    }
  } else {
    const text = await response.text();

    if (!response.ok) {
      throw new Error(
        text?.trim() || `Server request failed with HTTP ${response.status}.`,
      );
    }

    /*
     * Sometimes a successful backend response may still not
     * have the expected JSON content type.
     */
    try {
      data = JSON.parse(text);
    } catch {
      throw new Error(
        `The server returned an unexpected response: ${
          text?.trim() || "empty response"
        }`,
      );
    }
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.error ||
      data?.message ||
      `Server request failed with HTTP ${response.status}.`;

    throw new Error(
      Array.isArray(message) ? JSON.stringify(message) : String(message),
    );
  }

  return data;
}

/* =========================================================
   DOWNLOAD JSON
========================================================= */

function downloadJSON(filename, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });

  const url = URL.createObjectURL(blob);

  const anchor = document.createElement("a");

  anchor.href = url;
  anchor.download = filename;

  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();

  URL.revokeObjectURL(url);
}

/* =========================================================
   MAIN APP
========================================================= */

function App() {
  const [activeTab, setActiveTab] = useState("summary");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [success, setSuccess] = useState("");

  const clearMessages = () => {
    setError("");
    setSuccess("");
  };

  const changeTab = (tab) => {
    setActiveTab(tab);
    clearMessages();
  };

  const runRequest = async (callback) => {
    clearMessages();
    setLoading(true);

    try {
      await callback();
    } catch (err) {
      console.error("ScholarSphere API error:", err);

      setError(
        err?.message || "Something went wrong while processing your request.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="header">
        <div className="brand">
          <div className="brand-icon">🎓</div>

          <div>
            <h1>ScholarSphere</h1>
            <p>AI-powered Academic Assistant</p>
          </div>
        </div>

        <div className="header-badge">Research Intelligence</div>
      </header>

      {/* =====================================================
          MAIN CONTENT
      ===================================================== */}

      <main className="container">
        {/* HERO */}

        <section className="hero">
          <div>
            <p className="eyebrow">ACADEMIC AI PLATFORM</p>

            <h2>
              Understand research
              <br />
              <span>faster.</span>
            </h2>

            <p className="hero-description">
              Analyze research papers, generate summaries, compare documents,
              create quizzes, and discover related research using AI-powered
              NLP.
            </p>
          </div>
        </section>

        {/* ===================================================
            TABS
        =================================================== */}

        <nav className="tabs">
          <button
            className={activeTab === "summary" ? "tab active" : "tab"}
            onClick={() => changeTab("summary")}
          >
            📄 Summarization
          </button>

          <button
            className={activeTab === "similarity" ? "tab active" : "tab"}
            onClick={() => changeTab("similarity")}
          >
            🔍 Similarity
          </button>

          <button
            className={activeTab === "quiz" ? "tab active" : "tab"}
            onClick={() => changeTab("quiz")}
          >
            📝 Quizzer
          </button>

          <button
            className={activeTab === "research" ? "tab active" : "tab"}
            onClick={() => changeTab("research")}
          >
            🔎 Research Explorer
          </button>
        </nav>

        {/* ===================================================
            GLOBAL MESSAGES
        =================================================== */}

        {error && <div className="alert error">❌ {error}</div>}

        {success && <div className="alert success">✅ {success}</div>}

        {/* ===================================================
            TABS
        =================================================== */}

        {activeTab === "summary" && (
          <SummaryTab
            loading={loading}
            runRequest={runRequest}
            setSuccess={setSuccess}
          />
        )}

        {activeTab === "similarity" && (
          <SimilarityTab loading={loading} runRequest={runRequest} />
        )}

        {activeTab === "quiz" && (
          <QuizTab loading={loading} runRequest={runRequest} />
        )}

        {activeTab === "research" && (
          <ResearchTab loading={loading} runRequest={runRequest} />
        )}
      </main>

      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer>
        <p>ScholarSphere • AI-powered research analysis</p>

        <a
          href="https://github.com/YashUpd/ScholarSphere"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>
      </footer>
    </div>
  );
}

/* =========================================================
   SUMMARY TAB
========================================================= */

function SummaryTab({ loading, runRequest, setSuccess }) {
  const [files, setFiles] = useState([]);

  const [maxLength, setMaxLength] = useState(150);

  const [minLength, setMinLength] = useState(50);

  const [result, setResult] = useState(null);

  const handleSubmit = () => {
    runRequest(async () => {
      if (!files.length) {
        throw new Error("Please select at least one document.");
      }

      validateFiles(files);

      if (minLength >= maxLength) {
        throw new Error(
          "Minimum summary length must be smaller than maximum summary length.",
        );
      }

      const formData = new FormData();

      files.forEach((file) => {
        formData.append("files", file);
      });

      formData.append("max_length", String(maxLength));

      formData.append("min_length", String(minLength));

      const data = await apiRequest("/api/summarize", formData);

      if (!data || !Array.isArray(data.results)) {
        throw new Error(
          "The summarization API returned an unexpected response.",
        );
      }

      setResult(data);

      setSuccess("Summaries generated successfully.");
    });
  };

  return (
    <section className="card">
      <div className="section-heading">
        <div>
          <h3>Document Summarization</h3>

          <p>
            Upload research papers, articles, or reports to generate concise
            summaries.
          </p>
        </div>
      </div>

      <FilePicker files={files} setFiles={setFiles} multiple />

      <div className="settings-grid">
        <label>
          <span>
            Maximum summary length:
            <strong>{maxLength}</strong>
          </span>

          <input
            type="range"
            min="100"
            max="300"
            value={maxLength}
            onChange={(e) => setMaxLength(Number(e.target.value))}
          />
        </label>

        <label>
          <span>
            Minimum summary length:
            <strong>{minLength}</strong>
          </span>

          <input
            type="range"
            min="20"
            max="100"
            value={minLength}
            onChange={(e) => setMinLength(Number(e.target.value))}
          />
        </label>
      </div>

      <button
        className="primary-button"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Generating..." : "Generate Summaries"}
      </button>

      {result && (
        <div className="results">
          <h3>Individual Summaries</h3>

          {result.results.map((item, index) => (
            <div className="result-card" key={index}>
              <h4>📄 {item.filename}</h4>

              <p>{item.summary || "No summary was returned."}</p>
            </div>
          ))}

          {result.combined_summary && (
            <div className="combined">
              <h3>📚 Integrated Summary</h3>

              <p>{result.combined_summary}</p>
            </div>
          )}

          <button
            className="secondary-button"
            onClick={() => downloadJSON("scholarsphere_summaries.json", result)}
          >
            Download Results
          </button>
        </div>
      )}
    </section>
  );
}

/* =========================================================
   SIMILARITY TAB
========================================================= */

function SimilarityTab({ loading, runRequest }) {
  const [files, setFiles] = useState([]);

  const [result, setResult] = useState(null);

  const handleSubmit = () => {
    runRequest(async () => {
      if (files.length < 2) {
        throw new Error("Please select at least two documents.");
      }

      validateFiles(files);

      const formData = new FormData();

      files.forEach((file) => {
        formData.append("files", file);
      });

      const data = await apiRequest("/api/similarity", formData);

      if (
        !data ||
        !Array.isArray(data.filenames) ||
        !Array.isArray(data.matrix)
      ) {
        throw new Error("The similarity API returned an unexpected response.");
      }

      setResult(data);
    });
  };

  return (
    <section className="card">
      <h3>Document Similarity Analysis</h3>

      <p>
        Compare documents to identify semantic relationships and content
        overlap.
      </p>

      <FilePicker files={files} setFiles={setFiles} multiple />

      <button
        className="primary-button"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze Similarity"}
      </button>

      {result && (
        <div className="results">
          <h3>Similarity Matrix</h3>

          <div className="table-wrapper">
            <table className="matrix">
              <thead>
                <tr>
                  <th></th>

                  {result.filenames.map((filename, index) => (
                    <th key={`${filename}-${index}`}>{filename}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {result.matrix.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    <th>{result.filenames[rowIndex]}</th>

                    {row.map((value, columnIndex) => {
                      const numericValue = Number(value) || 0;

                      return (
                        <td
                          key={columnIndex}
                          style={{
                            backgroundColor: `rgba(37, 99, 235, ${Math.max(
                              0.08,
                              Math.min(1, numericValue),
                            )})`,
                          }}
                        >
                          {numericValue.toFixed(2)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {Array.isArray(result.summaries) && (
            <>
              <h3>Document Summaries</h3>

              {result.summaries.map((summary, index) => (
                <div className="result-card" key={index}>
                  <h4>📄 {result.filenames[index]}</h4>

                  <p>{summary}</p>
                </div>
              ))}
            </>
          )}

          <button
            className="secondary-button"
            onClick={() =>
              downloadJSON("scholarsphere_similarity.json", result)
            }
          >
            Download Analysis
          </button>
        </div>
      )}
    </section>
  );
}

/* =========================================================
   QUIZ TAB
========================================================= */

function QuizTab({ loading, runRequest }) {
  const [files, setFiles] = useState([]);

  const [numQuestions, setNumQuestions] = useState(3);

  const [result, setResult] = useState(null);

  const handleSubmit = () => {
    runRequest(async () => {
      if (!files.length) {
        throw new Error("Please select at least one document.");
      }

      validateFiles(files);

      if (
        !Number.isInteger(numQuestions) ||
        numQuestions < 1 ||
        numQuestions > 10
      ) {
        throw new Error("Number of questions must be between 1 and 10.");
      }

      const formData = new FormData();

      files.forEach((file) => {
        formData.append("files", file);
      });

      formData.append("num_questions", String(numQuestions));

      const data = await apiRequest("/api/quiz", formData);

      if (!data || !Array.isArray(data.questions)) {
        throw new Error("The quiz API returned an unexpected response.");
      }

      setResult(data);
    });
  };

  return (
    <section className="card">
      <h3>Quiz Generator</h3>

      <p>Generate multiple-choice questions from your research documents.</p>

      <FilePicker files={files} setFiles={setFiles} multiple />

      <label className="number-input">
        Questions per document
        <input
          type="number"
          min="1"
          max="10"
          value={numQuestions}
          onChange={(e) => setNumQuestions(Number(e.target.value))}
        />
      </label>

      <button
        className="primary-button"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Generating Quiz..." : "Generate Quiz"}
      </button>

      {result && (
        <div className="results">
          <h3>Generated Questions</h3>

          {result.questions.map((question, index) => (
            <div className="question-card" key={index}>
              <p className="question">
                {index + 1}. {question.question}
              </p>

              {Array.isArray(question.options) && (
                <div className="options">
                  {question.options.map((option, optionIndex) => (
                    <div className="option" key={optionIndex}>
                      {String.fromCharCode(65 + optionIndex)}. {option}
                    </div>
                  ))}
                </div>
              )}

              <p className="answer">
                Answer: {question.answer || "Not provided"}
              </p>
            </div>
          ))}

          <button
            className="secondary-button"
            onClick={() => downloadJSON("scholarsphere_quiz.json", result)}
          >
            Download Quiz
          </button>
        </div>
      )}
    </section>
  );
}

/* =========================================================
   RESEARCH TAB
========================================================= */

function ResearchTab({ loading, runRequest }) {
  const [file, setFile] = useState(null);

  const [result, setResult] = useState(null);

  const handleSubmit = () => {
    runRequest(async () => {
      if (!file) {
        throw new Error("Please select a document.");
      }

      validateFiles([file]);

      const formData = new FormData();

      formData.append("file", file);

      const data = await apiRequest("/api/research", formData);

      if (!data || !Array.isArray(data.topics) || !Array.isArray(data.papers)) {
        throw new Error("The research API returned an unexpected response.");
      }

      setResult(data);
    });
  };

  return (
    <section className="card">
      <h3>🔎 Research Explorer</h3>

      <p>
        Extract research topics and discover related papers using Semantic
        Scholar.
      </p>

      <FilePicker
        files={file ? [file] : []}
        setFiles={(items) => setFile(items[0] || null)}
      />

      <button
        className="primary-button"
        onClick={handleSubmit}
        disabled={loading}
      >
        {loading ? "Exploring..." : "Explore Research"}
      </button>

      {result && (
        <div className="results">
          <h3>Suggested Research Topics</h3>

          <div className="topic-list">
            {result.topics.map((topic, index) => (
              <span className="topic" key={`${topic}-${index}`}>
                {topic}
              </span>
            ))}
          </div>

          <h3>Recommended Papers</h3>

          {result.papers.length === 0 && <p>No related papers were found.</p>}

          {result.papers.map((paper, index) => (
            <div className="paper-card" key={index}>
              {paper.url ? (
                <a href={paper.url} target="_blank" rel="noreferrer">
                  {paper.title || "Untitled paper"}
                </a>
              ) : (
                <strong>{paper.title || "Untitled paper"}</strong>
              )}

              <p>
                {paper.year || "Year unavailable"}
                {" • "}
                {paper.authors || "Authors unavailable"}
              </p>

              <small>Topic: {paper.topic || "Topic unavailable"}</small>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

/* =========================================================
   FILE PICKER
========================================================= */

function FilePicker({ files, setFiles, multiple = false }) {
  const handleFileChange = (event) => {
    const selected = Array.from(event.target.files || []);

    try {
      validateFiles(selected);
      setFiles(selected);
    } catch (error) {
      /*
       * We don't have access to the global error
       * state here, so show the browser-level error.
       *
       * The parent will still validate again before
       * submitting.
       */
      window.alert(error?.message || "Invalid file selected.");

      event.target.value = "";
    }
  };

  return (
    <div className="file-picker">
      <label className="upload-area">
        <div className="upload-icon">📁</div>

        <strong>Click to upload</strong>

        <span>PDF, DOCX or TXT • Maximum 4 MB per file</span>

        <input
          type="file"
          accept=".pdf,.docx,.txt"
          multiple={multiple}
          onChange={handleFileChange}
        />
      </label>

      {files.length > 0 && (
        <div className="selected-files">
          {files.map((file, index) => (
            <div className="selected-file" key={`${file.name}-${index}`}>
              📄 {file.name}
              <span>
                {(file.size / 1024 / 1024).toFixed(2)}
                {" MB"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   EXPORT
========================================================= */

export default App;
