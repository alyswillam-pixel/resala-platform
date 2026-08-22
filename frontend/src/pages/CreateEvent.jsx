import { useState } from "react";
import { PlusCircle, CheckCircle2, AlertCircle, Loader2, ArrowRight, Plus, Trash2 } from "lucide-react";
import { createEventApi } from "../services/api";

const QUESTIONS = [
  { key: "where", label: "Where", singular: "Location", placeholder: "e.g. Resala HQ, Nasr City" },
  { key: "when", label: "When", singular: "Date / Time", placeholder: "e.g. Oct 12, 2026, 4:00 PM" },
  { key: "why", label: "Why", singular: "Objective", placeholder: "The purpose of this event" },
  { key: "how", label: "How", singular: "Plan / Activity", placeholder: "How it'll run" },
  { key: "who", label: "Who", singular: "Participant / Team", placeholder: "Who it's for / involved" },
];

export default function CreateEvent({ onEventCreated, onNavigateToEvents }) {
  const [title, setTitle] = useState("");
  const [answers, setAnswers] = useState({
    where: [""],
    when: [""],
    why: [""],
    how: [""],
    who: [""],
  });
  const [budget, setBudget] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [createdEvent, setCreatedEvent] = useState(null);

  const allFilled =
    title.trim() &&
    budget.trim() &&
    QUESTIONS.every((q) => answers[q.key]?.some((val) => val.trim()));

  function handleEntryChange(questionKey, index, value) {
    setAnswers((prev) => {
      const list = [...(prev[questionKey] || [""])];
      list[index] = value;
      return { ...prev, [questionKey]: list };
    });
  }

  function handleAddEntry(questionKey) {
    setAnswers((prev) => ({
      ...prev,
      [questionKey]: [...(prev[questionKey] || [""]), ""],
    }));
  }

  function handleRemoveEntry(questionKey, index) {
    setAnswers((prev) => {
      const currentList = prev[questionKey] || [""];
      if (currentList.length <= 1) {
        return { ...prev, [questionKey]: [""] };
      }
      return {
        ...prev,
        [questionKey]: currentList.filter((_, i) => i !== index),
      };
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!allFilled || isSubmitting) return;

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const result = await createEventApi({
        title,
        answers,
        budget,
      });

      setCreatedEvent(result);
      if (onEventCreated) {
        onEventCreated(result);
      }
    } catch (err) {
      console.error("Create event error:", err);
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to connect to backend server."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleReset() {
    setCreatedEvent(null);
    setTitle("");
    setBudget("");
    setAnswers({
      where: [""],
      when: [""],
      why: [""],
      how: [""],
      who: [""],
    });
    setErrorMessage("");
  }

  return (
    <div className="ce-root">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,340..700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

        .ce-root {
          --purple: #1D4ED8;
          --purple-bright: #2563EB;
          --lavender: #F0F7FF;
          --lavender-line: #D1E5F8;
          --gold: #38BDF8;
          --text-on-light: #0F172A;
          --text-on-light-mid: #475569;
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

        .ce-error-banner {
          background: #FEF2F2;
          border: 1px solid #FCA5A5;
          border-radius: 12px;
          padding: 14px 16px;
          margin-bottom: 20px;
          display: flex;
          align-items: flex-start;
          gap: 10px;
          color: #991B1B;
          font-size: 13px;
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
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin-bottom: 20px;
        }
        .ce-qcard {
          background: var(--lavender);
          border: 1px solid var(--lavender-line);
          border-radius: 12px;
          padding: 14px 16px;
        }
        .ce-qcard-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }
        .ce-entry-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }
        .ce-entry-row:last-child {
          margin-bottom: 0;
        }
        .ce-remove-btn {
          background: transparent;
          border: none;
          color: #94a3b8;
          cursor: pointer;
          padding: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 6px;
        }
        .ce-remove-btn:hover {
          color: #ef4444;
          background: #fee2e2;
        }
        .ce-add-entry-btn {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          background: #fff;
          border: 1px dashed var(--purple);
          color: var(--purple);
          font-size: 11.5px;
          font-weight: 600;
          padding: 4px 10px;
          border-radius: 6px;
          cursor: pointer;
          margin-top: 8px;
        }
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
          flex-direction: column;
          gap: 14px;
          color: #1F6B2C;
          font-size: 14px;
          max-width: 620px;
        }

        @media (max-width: 560px) {
          .ce-card { padding: 20px; }
        }
      `}</style>

      {createdEvent ? (
        <div className="ce-success">
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <CheckCircle2 size={24} style={{ flexShrink: 0 }} />
            <div>
              <strong>{createdEvent.title || title}</strong> was saved to the backend database in <strong>{createdEvent.current_state || "Draft"}</strong> state with a budget of <strong>{createdEvent.budget?.amount || budget} EGP</strong>.
            </div>
          </div>
          <div style={{ display: "flex", gap: "10px", marginTop: "8px" }}>
            {onNavigateToEvents && (
              <button
                type="button"
                className="ce-submit"
                onClick={onNavigateToEvents}
              >
                Go to My Events <ArrowRight size={14} />
              </button>
            )}
            <button
              type="button"
              className="ce-submit"
              style={{ background: "#fff", color: "var(--purple)", border: "1px solid var(--purple)" }}
              onClick={handleReset}
            >
              <PlusCircle size={14} /> Create Another
            </button>
          </div>
        </div>
      ) : (
        <form className="ce-card" onSubmit={handleSubmit}>
          {errorMessage && (
            <div className="ce-error-banner">
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <div>
                <strong>Backend Error:</strong> {errorMessage}
              </div>
            </div>
          )}

          <div className="ce-field">
            <label className="ce-label ce-mono">Event title</label>
            <input
              className="ce-input"
              type="text"
              placeholder="e.g. Children's Day 2026"
              value={title}
              disabled={isSubmitting}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="ce-qgrid">
            {QUESTIONS.map((q) => {
              const entries = answers[q.key] || [""];
              return (
                <div className="ce-qcard" key={q.key}>
                  <div className="ce-qcard-top">
                    <label className="ce-label ce-mono" style={{ marginBottom: 0 }}>
                      <span className="ce-qtag">{q.label}</span> {q.singular}s {entries.length > 1 && `(${entries.length})`}
                    </label>
                  </div>

                  {entries.map((val, idx) => (
                    <div className="ce-entry-row" key={idx}>
                      <input
                        className="ce-input"
                        type="text"
                        placeholder={
                          entries.length > 1
                            ? `${q.singular} #${idx + 1}`
                            : q.placeholder
                        }
                        value={val}
                        disabled={isSubmitting}
                        onChange={(e) => handleEntryChange(q.key, idx, e.target.value)}
                        required={idx === 0}
                      />
                      {entries.length > 1 && (
                        <button
                          type="button"
                          className="ce-remove-btn"
                          title="Remove entry"
                          disabled={isSubmitting}
                          onClick={() => handleRemoveEntry(q.key, idx)}
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  ))}

                  <button
                    type="button"
                    className="ce-add-entry-btn"
                    disabled={isSubmitting}
                    onClick={() => handleAddEntry(q.key)}
                  >
                    <Plus size={12} /> Add another {q.singular}
                  </button>
                </div>
              );
            })}
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
                disabled={isSubmitting}
                onChange={(e) => setBudget(e.target.value)}
                style={{ maxWidth: 180 }}
                required
              />
            </div>
          </div>

          <button type="submit" className="ce-submit" disabled={!allFilled || isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Creating event in backend...
              </>
            ) : (
              <>
                Create event <PlusCircle size={16} />
              </>
            )}
          </button>
          {!allFilled && !isSubmitting && (
            <div className="ce-hint">All five questions, the title, and a budget are required before this unlocks.</div>
          )}
        </form>
      )}
    </div>
  );
}