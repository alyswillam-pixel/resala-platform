import React, { useState } from "react";
import { PlusCircle, CheckCircle2, Sparkles, DollarSign } from "lucide-react";

const QUESTIONS = [
  { key: "where", label: "Where", placeholder: "e.g. Resala HQ, Nasr City Youth Center" },
  { key: "when", label: "When", placeholder: "e.g. Oct 12, 2026 at 4:00 PM" },
  { key: "why", label: "Why", placeholder: "The purpose & expected impact of this event" },
  { key: "how", label: "How", placeholder: "Logistics, agenda & execution breakdown" },
  { key: "who", label: "Who", placeholder: "Target audience, beneficiaries & team" },
];

export default function CreateEvent() {
  const [title, setTitle] = useState("");
  const [answers, setAnswers] = useState({ where: "", when: "", why: "", how: "", who: "" });
  const [budget, setBudget] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const filledCount = (title.trim() ? 1 : 0) + (budget.trim() ? 1 : 0) + QUESTIONS.filter((q) => answers[q.key].trim()).length;
  const totalFields = 7; // Title + Budget + 5 Questions
  const progressPercent = Math.round((filledCount / totalFields) * 100);
  const allFilled = filledCount === totalFields;

  function handleChange(key, value) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
  }

  function addBudgetPreset(amount) {
    const current = parseInt(budget) || 0;
    setBudget((current + amount).toString());
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!allFilled) return;
    console.log("create event", { title, ...answers, budget });
    setSubmitted(true);
  }

  return (
    <div className="ce-root animate-slide-up">
      <style>{`
        .ce-root {
          width: 100%;
          display: flex;
          justify-content: center;
        }

        .ce-card {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 24px;
          padding: 40px;
          width: 100%;
          max-width: 680px;
          box-shadow: 0 16px 40px -10px rgba(21, 12, 36, 0.07);
        }

        .ce-progress-wrap {
          margin-bottom: 28px;
        }
        .ce-progress-meta {
          display: flex;
          justify-content: space-between;
          font-size: 12.5px;
          font-weight: 600;
          color: var(--text-dark-muted);
          margin-bottom: 8px;
        }
        .ce-progress-bar {
          height: 8px;
          background: rgba(139, 79, 209, 0.08);
          border-radius: 100px;
          overflow: hidden;
        }
        .ce-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--purple-main), var(--purple-bright));
          border-radius: 100px;
          transition: width 0.3s ease;
        }

        .ce-field { margin-bottom: 22px; }
        .ce-label {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          font-weight: 700;
          color: var(--text-dark-muted);
          margin-bottom: 8px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .ce-qtag {
          background: var(--purple-main);
          color: #ffffff;
          padding: 2px 8px;
          border-radius: 6px;
          font-size: 11px;
          font-weight: 800;
        }

        .ce-input {
          width: 100%;
          background: var(--lavender-bg);
          border: 1.5px solid var(--lavender-border);
          border-radius: 12px;
          padding: 13px 16px;
          font-size: 14.5px;
          color: var(--text-dark);
          font-family: var(--font-sans);
          transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .ce-input:focus {
          outline: none;
          border-color: var(--purple-bright);
          box-shadow: 0 0 0 4px rgba(139, 79, 209, 0.12);
        }

        .ce-qgrid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 18px;
          margin-bottom: 22px;
        }

        .ce-budget-presets {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 10px;
        }
        .ce-preset-chip {
          border: 1px solid var(--lavender-border);
          background: #ffffff;
          color: var(--purple-main);
          font-size: 12px;
          font-weight: 700;
          padding: 5px 12px;
          border-radius: 100px;
          cursor: pointer;
          transition: background 0.15s ease, border-color 0.15s ease;
        }
        .ce-preset-chip:hover {
          background: rgba(139, 79, 209, 0.08);
          border-color: var(--purple-bright);
        }

        .ce-submit {
          width: 100%;
          background: var(--purple-main);
          color: #ffffff;
          border: none;
          border-radius: 100px;
          padding: 15px 0;
          font-size: 15px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
          box-shadow: 0 8px 20px -4px rgba(29, 78, 216, 0.3);
        }
        .ce-submit:hover:not(:disabled) {
          background: var(--purple-bright);
          transform: translateY(-1px);
          box-shadow: 0 12px 24px -4px rgba(139, 79, 209, 0.4);
        }
        .ce-submit:disabled {
          opacity: 0.5;
          cursor: not-allowed;
          box-shadow: none;
        }

        .ce-success-card {
          background: #ffffff;
          border: 1px solid #CBEFCF;
          border-radius: 24px;
          padding: 40px;
          text-align: center;
          max-width: 540px;
          width: 100%;
          box-shadow: 0 16px 40px -10px rgba(34, 197, 94, 0.12);
        }
        .ce-success-icon {
          width: 64px;
          height: 64px;
          border-radius: 100px;
          background: #EFFBF1;
          color: #16a34a;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 20px;
        }

        @media (max-width: 600px) {
          .ce-qgrid { grid-template-columns: 1fr; }
          .ce-card { padding: 26px; }
        }
      `}</style>

      {submitted ? (
        <div className="ce-success-card animate-slide-up">
          <div className="ce-success-icon">
            <CheckCircle2 size={36} />
          </div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "24px", color: "var(--text-dark)", marginBottom: "10px" }}>
            Event Created Successfully!
          </h2>
          <p style={{ fontSize: "14.5px", color: "var(--text-dark-muted)", lineHeight: 1.6, marginBottom: "24px" }}>
            <strong>"{title}"</strong> has been submitted with a budget request of <strong>{parseInt(budget).toLocaleString()} EGP</strong>. It will automatically populate in your "My events" dashboard.
          </p>
          <button
            className="ce-submit"
            style={{ maxWidth: "220px", margin: "0 auto" }}
            onClick={() => {
              setSubmitted(false);
              setTitle("");
              setBudget("");
              setAnswers({ where: "", when: "", why: "", how: "", who: "" });
            }}
          >
            Create Another Event
          </button>
        </div>
      ) : (
        <form className="ce-card" onSubmit={handleSubmit}>
          {/* Progress Header */}
          <div className="ce-progress-wrap">
            <div className="ce-progress-meta">
              <span>Form Completion</span>
              <span>{filledCount} of {totalFields} fields ({progressPercent}%)</span>
            </div>
            <div className="ce-progress-bar">
              <div className="ce-progress-fill" style={{ width: `${progressPercent}%` }} />
            </div>
          </div>

          {/* Event Title */}
          <div className="ce-field">
            <label className="ce-label">Event Title</label>
            <input
              className="ce-input"
              type="text"
              placeholder="e.g. Annual Children's Day Festival 2026"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          {/* 5 Ws Grid */}
          <div className="ce-qgrid">
            {QUESTIONS.map((q) => (
              <div className="ce-field" key={q.key} style={{ marginBottom: 0 }}>
                <label className="ce-label">
                  <span className="ce-qtag">{q.label}</span>
                </label>
                <input
                  className="ce-input"
                  type="text"
                  placeholder={q.placeholder}
                  value={answers[q.key]}
                  onChange={(e) => handleChange(q.key, e.target.value)}
                />
              </div>
            ))}
          </div>

          {/* Budget Field + Quick Presets */}
          <div className="ce-field" style={{ marginTop: "18px" }}>
            <label className="ce-label">Target Budget (EGP)</label>
            <input
              className="ce-input"
              type="number"
              min="0"
              placeholder="e.g. 15000"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
            <div className="ce-budget-presets">
              <span style={{ fontSize: "12px", color: "var(--text-dark-muted)", fontWeight: 600 }}>Quick Add:</span>
              <button type="button" className="ce-preset-chip" onClick={() => addBudgetPreset(1000)}>+1,000</button>
              <button type="button" className="ce-preset-chip" onClick={() => addBudgetPreset(5000)}>+5,000</button>
              <button type="button" className="ce-preset-chip" onClick={() => addBudgetPreset(10000)}>+10,000</button>
            </div>
          </div>

          <button type="submit" className="ce-submit" disabled={!allFilled}>
            Submit Event Request <PlusCircle size={18} />
          </button>
        </form>
      )}
    </div>
  );
}
