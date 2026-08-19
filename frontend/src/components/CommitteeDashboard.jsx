import React, { useState } from "react";
import { LayoutDashboard, Clock, CheckCircle2, AlertTriangle, User, Send, Layers, Check, Edit3, ArrowRight } from "lucide-react";

export default function CommitteeDashboard({ tasks, onSubmitForApproval }) {
  const [toast, setToast] = useState(null);

  const statusBadges = {
    "Waiting for Planner Approval": { bg: "rgba(234, 179, 8, 0.12)", text: "#b45309", border: "rgba(234, 179, 8, 0.3)", icon: Clock },
    Approved: { bg: "rgba(34, 197, 94, 0.12)", text: "#15803d", border: "rgba(34, 197, 94, 0.3)", icon: CheckCircle2 },
    "Revision Requested": { bg: "rgba(239, 68, 68, 0.12)", text: "#b91c1c", border: "rgba(239, 68, 68, 0.3)", icon: AlertTriangle },
    "In Progress": { bg: "rgba(59, 130, 246, 0.12)", text: "#1d4ed8", border: "rgba(59, 130, 246, 0.3)", icon: Layers }
  };

  const pendingCount = tasks.filter((t) => t.status === "Waiting for Planner Approval").length;
  const approvedCount = tasks.filter((t) => t.status === "Approved").length;

  function handleSubmitTask(taskId, title) {
    if (onSubmitForApproval) {
      onSubmitForApproval(taskId);
      setToast(`Submitted "${title}" to Event Planner for approval!`);
      setTimeout(() => setToast(null), 4000);
    }
  }

  return (
    <div className="cd-root animate-slide-up">
      <style>{`
        .cd-root { width: 100%; }

        .cd-toast {
          background: #EFFBF1;
          border: 1px solid #CBEFCF;
          color: #1F6B2C;
          padding: 14px 20px;
          border-radius: 14px;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 24px;
          display: flex;
          align-items: center;
          gap: 10px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        .cd-metrics {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 16px;
          margin-bottom: 32px;
        }
        .cd-metric-card {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 18px;
          padding: 22px;
          box-shadow: var(--shadow-soft);
        }
        .cd-metric-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 12px;
          color: var(--text-dark-muted);
          font-size: 13px;
          font-weight: 600;
        }
        .cd-metric-icon {
          width: 38px;
          height: 38px;
          border-radius: 10px;
          background: rgba(139, 79, 209, 0.08);
          color: var(--purple-bright);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .cd-metric-val {
          font-family: var(--font-display);
          font-size: 26px;
          font-weight: 700;
          color: var(--text-dark);
        }

        .cd-section-title {
          font-family: var(--font-display);
          font-size: 20px;
          font-weight: 700;
          color: var(--text-dark);
          margin-bottom: 18px;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .cd-list {
          display: flex;
          flex-direction: column;
          gap: 18px;
        }
        .cd-item {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 20px;
          padding: 24px 28px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          box-shadow: var(--shadow-soft);
          transition: all 0.25s ease;
        }
        .cd-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 12px 28px -5px rgba(139, 79, 209, 0.15);
          border-color: rgba(139, 79, 209, 0.3);
        }
        .cd-item-main { flex: 1; }
        .cd-item-title {
          font-size: 17px;
          font-weight: 700;
          color: var(--text-dark);
          margin-bottom: 4px;
        }
        .cd-event-name {
          font-size: 13px;
          font-weight: 600;
          color: var(--purple-bright);
          margin-bottom: 10px;
        }
        .cd-item-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          font-size: 13px;
          color: var(--text-dark-muted);
          margin-bottom: 12px;
        }
        .cd-item-notes {
          font-size: 13.5px;
          color: var(--text-dark);
          background: var(--lavender-bg);
          padding: 12px 16px;
          border-radius: 12px;
          line-height: 1.5;
        }

        .cd-status-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 11.5px;
          font-weight: 700;
          padding: 5px 12px;
          border-radius: 100px;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          margin-bottom: 10px;
        }

        .cd-submit-btn {
          background: var(--purple-main);
          color: #ffffff;
          border: none;
          border-radius: 100px;
          padding: 12px 22px;
          font-size: 13.5px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: background 0.2s ease, transform 0.15s ease;
          white-space: nowrap;
        }
        .cd-submit-btn:hover {
          background: var(--purple-bright);
          transform: translateY(-1px);
        }

        @media (max-width: 720px) {
          .cd-item { flex-direction: column; align-items: flex-start; }
          .cd-submit-btn { width: 100%; justify-content: center; }
        }
      `}</style>

      {toast && (
        <div className="cd-toast animate-slide-up">
          <CheckCircle2 size={18} />
          {toast}
        </div>
      )}

      {/* Metrics */}
      <div className="cd-metrics">
        <div className="cd-metric-card">
          <div className="cd-metric-header">
            <span>Assigned Tasks</span>
            <div className="cd-metric-icon"><Layers size={18} /></div>
          </div>
          <div className="cd-metric-val">{tasks.length}</div>
        </div>
        <div className="cd-metric-card">
          <div className="cd-metric-header">
            <span>Waiting for Planner Approval</span>
            <div className="cd-metric-icon"><Clock size={18} /></div>
          </div>
          <div className="cd-metric-val">{pendingCount}</div>
        </div>
        <div className="cd-metric-card">
          <div className="cd-metric-header">
            <span>Approved Tasks</span>
            <div className="cd-metric-icon"><CheckCircle2 size={18} /></div>
          </div>
          <div className="cd-metric-val">{approvedCount}</div>
        </div>
      </div>

      <h2 className="cd-section-title">
        <LayoutDashboard size={20} color="var(--purple-bright)" />
        Committee Tasks & Assignments
      </h2>

      <div className="cd-list">
        {tasks.map((task) => {
          const st = statusBadges[task.status] || statusBadges["In Progress"];
          const Icon = st.icon;
          const isWaiting = task.status === "Waiting for Planner Approval";
          const isApproved = task.status === "Approved";

          return (
            <div className="cd-item" key={task.id}>
              <div className="cd-item-main">
                <span className="cd-status-badge" style={{ background: st.bg, color: st.text, border: `1px solid ${st.border}` }}>
                  <Icon size={13} /> {task.status}
                </span>

                <h3 className="cd-item-title">{task.title}</h3>
                <div className="cd-event-name">Event: {task.eventTitle}</div>

                <div className="cd-item-meta">
                  <span>Assigned Committee: <strong>{task.committee}</strong></span>
                  <span>•</span>
                  <span>Assigned to: <strong>{task.assignedTo}</strong></span>
                  <span>•</span>
                  <span>Budget: <strong>{task.budget.toLocaleString()} EGP</strong></span>
                </div>

                <div className="cd-item-notes">
                  <strong>Task Specs & Notes:</strong> {task.notes}
                </div>
              </div>

              {!isWaiting && !isApproved && (
                <button className="cd-submit-btn" onClick={() => handleSubmitTask(task.id, task.title)}>
                  Submit to Planner <Send size={15} />
                </button>
              )}

              {isWaiting && (
                <div style={{ fontSize: "12.5px", fontWeight: 700, color: "#b45309", background: "rgba(234,179,8,0.1)", padding: "10px 16px", borderRadius: "100px", whiteSpace: "nowrap" }}>
                  Awaiting Event Planner Sign-off
                </div>
              )}

              {isApproved && (
                <div style={{ fontSize: "12.5px", fontWeight: 700, color: "#15803d", background: "rgba(34,197,94,0.1)", padding: "10px 16px", borderRadius: "100px", whiteSpace: "nowrap" }}>
                  ✓ Approved by Planner
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
