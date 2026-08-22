import { useState } from "react";
import { PlusCircle, CheckCircle2, AlertCircle, Loader2, ArrowRight, Plus, Trash2 } from "lucide-react";
import { createEventApi } from "../services/api";

const QUESTIONS = [
  { key: "where", label: "Where", singular: "Location", placeholder: "e.g. Resala HQ, Nasr City Youth Center" },
  { key: "when", label: "When", singular: "Date / Time", placeholder: "e.g. Oct 12, 2026 at 4:00 PM" },
  { key: "why", label: "Why", singular: "Objective / Purpose", placeholder: "The purpose & expected impact of this event" },
  { key: "how", label: "How", singular: "Activity / Step", placeholder: "Logistics, agenda & execution breakdown" },
  { key: "who", label: "Who", singular: "Target Group / Stakeholder", placeholder: "Target audience, beneficiaries & team" },
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

  const filledCount =
    (title.trim() ? 1 : 0) +
    (budget.trim() ? 1 : 0) +
    QUESTIONS.filter((q) => answers[q.key]?.some((val) => val.trim())).length;
  const totalFields = 7; // Title + Budget + 5 Questions
  const progressPercent = Math.round((filledCount / totalFields) * 100);
  const allFilled = filledCount === totalFields;

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

  function addBudgetPreset(amount) {
    const current = parseInt(budget) || 0;
    setBudget((current + amount).toString());
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
      console.error("Event creation error:", err);
      setErrorMessage(
        err instanceof Error
          ? err.message
          : "Failed to connect to backend server. Please verify your connection or login credentials."
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
          background: rgba(37, 99, 235, 0.08);
          border-radius: 100px;
          overflow: hidden;
        }
        .ce-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--purple-main), var(--purple-bright));
          border-radius: 100px;
          transition: width 0.3s ease;
        }

        .ce-error-banner {
          background: #FEF2F2;
          border: 1px solid #FCA5A5;
          border-radius: 14px;
          padding: 16px 18px;
          margin-bottom: 24px;
          display: flex;
          align-items: flex-start;
          gap: 12px;
          color: #991B1B;
          font-size: 13.5px;
          line-height: 1.5;
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
          box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
        }

        .ce-qgrid {
          display: flex;
          flex-direction: column;
          gap: 20px;
          margin-bottom: 24px;
        }

        .ce-qcard {
          background: #faf8fd;
          border: 1.5px solid var(--lavender-border);
          border-radius: 16px;
          padding: 18px 20px;
          transition: border-color 0.2s ease;
        }
        .ce-qcard:focus-within {
          border-color: var(--purple-bright);
          background: #ffffff;
        }

        .ce-qcard-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
        }

        .ce-entry-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 10px;
        }
        .ce-entry-row:last-child {
          margin-bottom: 0;
        }

        .ce-entry-index {
          font-size: 11px;
          font-weight: 700;
          color: var(--text-dark-muted);
          min-width: 22px;
          text-align: center;
        }

        .ce-remove-btn {
          background: transparent;
          border: none;
          color: #94a3b8;
          padding: 8px;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: color 0.15s ease, background 0.15s ease;
        }
        .ce-remove-btn:hover {
          color: #ef4444;
          background: #fee2e2;
        }

        .ce-add-entry-btn {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          background: #ffffff;
          border: 1px dashed var(--purple-bright);
          color: var(--purple-main);
          font-size: 12px;
          font-weight: 600;
          padding: 6px 12px;
          border-radius: 8px;
          cursor: pointer;
          margin-top: 10px;
          transition: background 0.15s ease, transform 0.1s ease;
        }
        .ce-add-entry-btn:hover:not(:disabled) {
          background: rgba(37, 99, 235, 0.06);
          transform: translateY(-1px);
        }
        .ce-add-entry-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
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
          background: rgba(37, 99, 235, 0.08);
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
          box-shadow: 0 12px 24px -4px rgba(37, 99, 235, 0.4);
        }
        .ce-submit:disabled {
          opacity: 0.55;
          cursor: not-allowed;
          box-shadow: none;
        }

        .ce-success-card {
          background: #ffffff;
          border: 1px solid #CBEFCF;
          border-radius: 24px;
          padding: 40px;
          text-align: center;
          max-width: 620px;
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
        .ce-backend-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
          font-weight: 700;
          background: rgba(34, 197, 94, 0.12);
          color: #16a34a;
          padding: 4px 12px;
          border-radius: 100px;
          text-transform: uppercase;
          margin-bottom: 12px;
        }

        .ce-success-details {
          background: var(--lavender-bg);
          border: 1px solid var(--lavender-border);
          border-radius: 16px;
          padding: 20px;
          text-align: left;
          margin-bottom: 28px;
          font-size: 13.5px;
        }
        .ce-detail-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px dashed rgba(0,0,0,0.06);
        }
        .ce-detail-row:last-child {
          border-bottom: none;
        }
        .ce-pill-badge {
          display: inline-block;
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 6px;
          padding: 2px 8px;
          font-size: 12px;
          margin: 2px;
        }

        .ce-success-actions {
          display: flex;
          gap: 12px;
          justify-content: center;
          flex-wrap: wrap;
        }

        @media (max-width: 600px) {
          .ce-card { padding: 24px; }
        }
      `}</style>

      {createdEvent ? (
        <div className="ce-success-card animate-slide-up">
          <div className="ce-success-icon">
            <CheckCircle2 size={36} />
          </div>
          <span className="ce-backend-badge">
            Backend Confirmed · State: {createdEvent.current_state || "Draft"}
          </span>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "24px", color: "var(--text-dark)", marginBottom: "10px" }}>
            Event Created Successfully!
          </h2>
          <p style={{ fontSize: "14.5px", color: "var(--text-dark-muted)", lineHeight: 1.6, marginBottom: "20px" }}>
            <strong>"{createdEvent.title || title}"</strong> has been saved directly to the database and initialized in <strong>Draft</strong> state.
          </p>

          <div className="ce-success-details">
            <div className="ce-detail-row">
              <span style={{ color: "var(--text-dark-muted)" }}>Backend Event ID:</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", fontWeight: 600 }}>{createdEvent.id ? String(createdEvent.id).slice(0, 18) + "..." : "Generated"}</span>
            </div>
            <div className="ce-detail-row">
              <span style={{ color: "var(--text-dark-muted)" }}>Allocated Budget:</span>
              <span style={{ fontWeight: 700, color: "var(--purple-main)" }}>
                {createdEvent.budget?.amount ? `${parseFloat(createdEvent.budget.amount).toLocaleString()} EGP` : `${parseInt(budget || 0).toLocaleString()} EGP`}
              </span>
            </div>

            {QUESTIONS.map((q) => {
              const entries = (answers[q.key] || []).filter(Boolean);
              return (
                <div className="ce-detail-row" key={q.key} style={{ flexDirection: entries.length > 1 ? "column" : "row", gap: entries.length > 1 ? "6px" : "12px" }}>
                  <span style={{ color: "var(--text-dark-muted)", fontWeight: 600 }}>{q.label} ({q.singular}s):</span>
                  <div style={{ textAlign: entries.length > 1 ? "left" : "right" }}>
                    {entries.length === 0 && <span style={{ color: "#94a3b8" }}>None</span>}
                    {entries.length === 1 && <span style={{ fontWeight: 600 }}>{entries[0]}</span>}
                    {entries.length > 1 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                        {entries.map((val, idx) => (
                          <span key={idx} className="ce-pill-badge">
                            <strong>#{idx + 1}</strong> {val}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="ce-success-actions">
            {onNavigateToEvents && (
              <button
                className="ce-submit"
                style={{ flex: 1, minWidth: "180px" }}
                onClick={onNavigateToEvents}
              >
                Go to My Events <ArrowRight size={16} />
              </button>
            )}
            <button
              type="button"
              className="ce-submit"
              style={{
                flex: 1,
                minWidth: "180px",
                background: "#ffffff",
                color: "var(--purple-main)",
                border: "1.5px solid var(--purple-main)",
                boxShadow: "none"
              }}
              onClick={handleReset}
            >
              <PlusCircle size={16} /> Create Another
            </button>
          </div>
        </div>
      ) : (
        <form className="ce-card" onSubmit={handleSubmit}>
          {/* Progress Header */}
          <div className="ce-progress-wrap">
            <div className="ce-progress-meta">
              <span>Form Completion</span>
              <span>{filledCount} of {totalFields} required sections ({progressPercent}%)</span>
            </div>
            <div className="ce-progress-bar">
              <div className="ce-progress-fill" style={{ width: `${progressPercent}%` }} />
            </div>
          </div>

          {errorMessage && (
            <div className="ce-error-banner">
              <AlertCircle size={20} style={{ flexShrink: 0, marginTop: "2px" }} />
              <div>
                <strong>Backend Error:</strong> {errorMessage}
              </div>
            </div>
          )}

          {/* Event Title */}
          <div className="ce-field">
            <label className="ce-label">Event Title</label>
            <input
              className="ce-input"
              type="text"
              placeholder="e.g. Annual Children's Day Festival 2026"
              value={title}
              disabled={isSubmitting}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          {/* 5 Ws Interactive Multi-Entry Cards */}
          <div className="ce-qgrid">
            {QUESTIONS.map((q) => {
              const entries = answers[q.key] || [""];
              return (
                <div className="ce-qcard" key={q.key}>
                  <div className="ce-qcard-header">
                    <label className="ce-label" style={{ marginBottom: 0 }}>
                      <span className="ce-qtag">{q.label}</span>
                      <span style={{ fontSize: "13px", color: "var(--text-dark)", textTransform: "none", fontWeight: 600 }}>
                        {q.singular}s {entries.length > 1 && `(${entries.length})`}
                      </span>
                    </label>
                  </div>

                  {entries.map((val, idx) => (
                    <div className="ce-entry-row" key={idx}>
                      {entries.length > 1 && (
                        <span className="ce-entry-index">#{idx + 1}</span>
                      )}
                      <input
                        className="ce-input"
                        type="text"
                        placeholder={
                          entries.length > 1
                            ? `${q.singular} #${idx + 1} (e.g. ${q.placeholder.split(",")[0] || q.placeholder})`
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
                          title={`Remove this ${q.singular.toLowerCase()}`}
                          disabled={isSubmitting}
                          onClick={() => handleRemoveEntry(q.key, idx)}
                        >
                          <Trash2 size={16} />
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
                    <Plus size={14} /> Add another {q.singular}
                  </button>
                </div>
              );
            })}
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
              disabled={isSubmitting}
              onChange={(e) => setBudget(e.target.value)}
              required
            />
            <div className="ce-budget-presets">
              <span style={{ fontSize: "12px", color: "var(--text-dark-muted)", fontWeight: 600 }}>Quick Add:</span>
              <button type="button" disabled={isSubmitting} className="ce-preset-chip" onClick={() => addBudgetPreset(1000)}>+1,000</button>
              <button type="button" disabled={isSubmitting} className="ce-preset-chip" onClick={() => addBudgetPreset(5000)}>+5,000</button>
              <button type="button" disabled={isSubmitting} className="ce-preset-chip" onClick={() => addBudgetPreset(10000)}>+10,000</button>
            </div>
          </div>

          <button type="submit" className="ce-submit" disabled={!allFilled || isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 size={18} className="animate-spin" /> Saving Event to Backend...
              </>
            ) : (
              <>
                Submit Event Request <PlusCircle size={18} />
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
}
