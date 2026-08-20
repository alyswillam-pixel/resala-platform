import React, { useState } from "react";
import { PlusCircle, CheckCircle2 } from "lucide-react";

const QUESTIONS = [
  { key: "where", label: "Where", placeholder: "e.g. Resala HQ, Nasr City" },
  { key: "when", label: "When", placeholder: "e.g. Oct 12, 2026, 4:00 PM" },
  { key: "why", label: "Why", placeholder: "The purpose of this event" },
  { key: "how", label: "How", placeholder: "How it'll run" },
  { key: "who", label: "Who", placeholder: "Who it's for / involved" },
];

export default function CreateEvent() {
  const [title, setTitle] = useState("");
  const [answers, setAnswers] = useState({ where: "", when: "", why: "", how: "", who: "" });
  const [budget, setBudget] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const allFilled = title.trim() && budget.trim() && QUESTIONS.every((q) => answers[q.key].trim());

  function handleChange(key, value) {
    setAnswers((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!allFilled) return;
    // Wiring to the real backend endpoint happens once the team's synced on it —
    // for now this proves the form and validation work end to end.
    console.log("create event", { title, ...answers, budget });
    setSubmitted(true);
  }

  return (
    <div className="ce-root">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,340..700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

        .ce-root {
          --purple: #5B2A86;
          --purple-bright: #8B4FD1;
          --lavender: #F3EDFB;
          --lavender-line: #E4D6F5;
          --gold: #E3AE4E;
          --text-on-light: #372350;
          --text-on-light-mid: #6C5A85;
          font-family: 'Inter', sans-serif;
          width: 100%;
        }
        .ce-root * { box-sizing: border-box; }
        .ce-mono { font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.1em; text-transform: uppercase; }

        .ce-card {
          background: #fff;
          border: 1px solid var(--lavender-line);
          border-radius: 18px;
          padding: 34px;
          max-width: 620px;
        }
        .ce-field { margin-bottom: 20px; }
        .ce-label {
          display: block;
          font-size: 11.5px;
          color: var(--text-on-light-mid);
          margin-bottom: 8px;
        }
        .ce-input {
          width: 100%;
          background: var(--lavender);
          border: 1px solid var(--lavender-line);
          border-radius: 10px;
          padding: 12px 14px;
          font-size: 14px;
          color: var(--text-on-light);
          font-family: 'Inter', sans-serif;
        }
        .ce-input:focus { outline: none; border-color: var(--purple-bright); }

        .ce-qgrid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          margin-bottom: 20px;
        }
        .ce-qfield .ce-label { display: flex; align-items: center; gap: 6px; }
        .ce-qtag {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          background: var(--purple);
          color: #fff;
          padding: 2px 6px;
          border-radius: 4px;
        }

        .ce-budget-row {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .ce-budget-tag {
          font-size: 13px;
          color: var(--text-on-light-mid);
          font-weight: 600;
        }

        .ce-submit {
          background: var(--purple);
          color: #fff;
          border: none;
          border-radius: 100px;
          padding: 13px 26px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: background .15s ease, opacity .15s ease;
        }
        .ce-submit:hover:not(:disabled) { background: var(--purple-bright); }
        .ce-submit:disabled { opacity: 0.45; cursor: not-allowed; }
        .ce-submit:focus-visible { outline: 2px solid var(--gold); outline-offset: 3px; }

        .ce-hint { font-size: 12px; color: var(--text-on-light-mid); margin-top: 10px; }

        .ce-success {
          background: #EFFBF1;
          border: 1px solid #CBEFCF;
          border-radius: 14px;
          padding: 22px 24px;
          display: flex;
          align-items: center;
          gap: 12px;
          color: #1F6B2C;
          font-size: 14px;
          max-width: 620px;
        }

        @media (max-width: 560px) {
          .ce-qgrid { grid-template-columns: 1fr; }
          .ce-card { padding: 24px; }
        }
      `}</style>

      {submitted ? (
        <div className="ce-success">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title}</strong> was created with a budget of {budget} EGP.
            It'll show up in "My events" once that's wired to real data.
          </div>
        </div>
      ) : (
        <form className="ce-card" onSubmit={handleSubmit}>
          <div className="ce-field">
            <label className="ce-label ce-mono">Event title</label>
            <input
              className="ce-input"
              type="text"
              placeholder="e.g. Children's Day 2026"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="ce-qgrid">
            {QUESTIONS.map((q) => (
              <div className="ce-field ce-qfield" key={q.key}>
                <label className="ce-label ce-mono">
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

          <div className="ce-field">
            <label className="ce-label ce-mono">Budget</label>
            <div className="ce-budget-row">
              <span className="ce-budget-tag">EGP</span>
              <input
                className="ce-input"
                type="number"
                min="0"
                placeholder="0"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                style={{ maxWidth: 180 }}
              />
            </div>
          </div>

          <button type="submit" className="ce-submit" disabled={!allFilled}>
            Create event <PlusCircle size={16} />
          </button>
          {!allFilled && (
            <div className="ce-hint">All five questions, the title, and a budget are required before this unlocks.</div>
          )}
        </form>
      )}
    </div>
  );
}