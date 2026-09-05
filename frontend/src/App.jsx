import { useState, useRef, useEffect } from "react";
import "./App.css";

const API_BASE = "/api";

const VERDICT_STYLES = {
  Compliant: { bg: "#e6f4ea", border: "#1a9850", text: "#0f6d33", icon: "✓" },
  "Non-Compliant": { bg: "#fdecea", border: "#d73027", text: "#a3241d", icon: "✕" },
  "Needs Review": { bg: "#fff8e1", border: "#e6ab02", text: "#8a6d02", icon: "?" },
};

async function parseJsonResponse(res) {
  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    const text = await res.text();
    if (text.trim().toLowerCase().startsWith("<!doctype") || text.trim().toLowerCase().startsWith("<html")) {
      throw new Error(`Backend server returned HTML (Status ${res.status}) instead of JSON. Ensure Flask backend is running on port 5001.`);
    }
    throw new Error(`Server returned non-JSON response (Status ${res.status}): ${text.slice(0, 120)}`);
  }
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || `Request failed with status ${res.status}`);
  }
  return data;
}

function VerdictBadge({ verdict }) {
  const s = VERDICT_STYLES[verdict] || VERDICT_STYLES["Needs Review"];
  return (
    <div
      className="verdict-badge"
      style={{ background: s.bg, borderColor: s.border, color: s.text }}
    >
      <span className="verdict-icon">{s.icon}</span> {verdict}
    </div>
  );
}

function FieldsTable({ fields }) {
  return (
    <div className="table-wrapper">
      <table className="fields-table">
        <thead>
          <tr>
            <th>Field</th>
            <th>Extracted Value</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {fields.map((f) => (
            <tr key={f.field} className={`row-${f.status}`}>
              <td className="field-label-cell">{f.label}</td>
              <td className="field-val-cell">{f.value || "—"}</td>
              <td>
                <span className={`status-pill status-${f.status}`}>
                  {f.status.toUpperCase()}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [pasteNotice, setPasteNotice] = useState(false);
  const fileInput = useRef(null);
  const cameraInput = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  useEffect(() => {
    const handlePaste = (e) => {
      const targetTag = e.target?.tagName?.toLowerCase();
      if (targetTag === "input" || targetTag === "textarea") return;

      const items = e.clipboardData?.items;
      if (!items) return;

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.type && item.type.startsWith("image/")) {
          e.preventDefault();
          const pastedBlob = item.getAsFile();
          if (pastedBlob) {
            const fileName = pastedBlob.name && pastedBlob.name !== "image.png"
              ? pastedBlob.name
              : `pasted_label_${Date.now()}.png`;
            const fileObj = new File([pastedBlob], fileName, { type: pastedBlob.type || "image/png" });
            handleFile(fileObj);
            setPasteNotice(true);
            setTimeout(() => setPasteNotice(false), 3000);
          }
          break;
        }
      }
    };

    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, []);

  const loadHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history`, {
        headers: { "Bypass-Tunnel-Remainder": "true" },
      });
      const contentType = res.headers.get("content-type") || "";
      if (!res.ok || !contentType.includes("application/json")) return;
      const data = await res.json();
      setHistory(data);
    } catch {
      // backend optional
    }
  };

  const scanImage = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("image", file);
      const res = await fetch(`${API_BASE}/scan`, {
        method: "POST",
        headers: { "Bypass-Tunnel-Remainder": "true" },
        body: formData,
      });
      const data = await parseJsonResponse(res);
      setResult(data);
      loadHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="logo-row">
          <div className="logo">📦 PackSure</div>
          <div className="team-tag">Team ERRORACCESS · SIH26034</div>
        </div>
        <div className="tagline">
          Legal Metrology (Packaged Commodities) Rules, 2011 — Mobile Scanner
        </div>
      </header>

      <main className="main">
        <section className="upload-panel">
          <h2>1. Upload or Take Photo of Product Label</h2>
          <div
            className="dropzone"
            onClick={() => fileInput.current.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              handleFile(e.dataTransfer.files[0]);
            }}
          >
            {preview ? (
              <img src={preview} alt="preview" className="preview-img" />
            ) : (
              <div className="dropzone-prompt">
                <span className="drop-icon">📷</span>
                <p><strong>Tap to select, drag & drop, or paste (Ctrl+V)</strong></p>
                <p className="subtext">Take photo or upload label image (jpg, png, webp)</p>
              </div>
            )}
          </div>
          {pasteNotice && <p className="paste-notice">📋 Image pasted from clipboard!</p>}

          <div className="upload-btn-row">
            <button
              className="action-btn secondary-btn"
              onClick={() => cameraInput.current.click()}
            >
              📷 Take Live Photo
            </button>

            <button
              className="action-btn secondary-btn"
              onClick={() => fileInput.current.click()}
            >
              📁 Choose File
            </button>
          </div>

          <input
            type="file"
            ref={fileInput}
            accept="image/*"
            style={{ display: "none" }}
            onChange={(e) => handleFile(e.target.files[0])}
          />
          <input
            type="file"
            ref={cameraInput}
            accept="image/*"
            capture="environment"
            style={{ display: "none" }}
            onChange={(e) => handleFile(e.target.files[0])}
          />

          <button className="scan-btn" disabled={!file || loading} onClick={scanImage}>
            {loading ? "Scanning Product Label…" : "Run Compliance Check"}
          </button>
          {error && <p className="error-msg">{error}</p>}
        </section>

        <section className="result-panel">
          <h2>2. Compliance Result</h2>
          {!result && !loading && <p className="placeholder">Scan results will appear here.</p>}
          {loading && (
            <div className="loading-box">
              <span className="spinner">⌛</span>
              <p className="placeholder">Running EasyOCR → Field Mapping → Rule Engine…</p>
            </div>
          )}
          {result && (
            <>
              <VerdictBadge verdict={result.verdict} />
              {result.review_reason && <p className="review-reason">{result.review_reason}</p>}
              <p className="confidence">OCR Confidence: {result.ocr_confidence}%</p>

              <FieldsTable fields={result.checked_fields} />

              {result.issues.length > 0 && (
                <div className="issues-box">
                  <h3>Issues Found</h3>
                  <ul>
                    {result.issues.map((i, idx) => (
                      <li key={idx} className={`issue-${i.severity}`}>
                        <strong>{i.label}:</strong> {i.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <a
                className="download-btn"
                href={`${API_BASE}/report/${result.report_file}`}
                target="_blank"
                rel="noreferrer"
              >
                ⬇ Download PDF Report
              </a>
            </>
          )}
        </section>
      </main>

      <section className="history-panel">
        <div className="history-header">
          <h2>Recent Scans</h2>
          <button className="link-btn" onClick={loadHistory}>Refresh</button>
        </div>
        {history.length === 0 ? (
          <p className="placeholder">No scans yet this session.</p>
        ) : (
          <div className="table-wrapper">
            <table className="fields-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Commodity</th>
                  <th>Manufacturer</th>
                  <th>Verdict</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h) => (
                  <tr key={h.id}>
                    <td>{h.id}</td>
                    <td>{h.commodity_name || "—"}</td>
                    <td>{h.manufacturer || "—"}</td>
                    <td>
                      <span className={`status-pill status-${h.verdict === "Compliant" ? "pass" : "fail"}`}>
                        {h.verdict}
                      </span>
                    </td>
                    <td>{h.ocr_confidence}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer className="footer">
        PackSure Mobile App — React.js + Flask REST API + EasyOCR Engine
      </footer>
    </div>
  );
}
