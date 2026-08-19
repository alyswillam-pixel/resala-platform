import React, { useState } from "react";
import { CheckCircle2, XCircle, Edit3, Clock, DollarSign, ExternalLink, Save, X, Sparkles } from "lucide-react";

export default function ApprovalsQueue({ tasks, onApproveTask, onDenyTask, onEditTask, role }) {
  const [editingTask, setEditingTask] = useState(null);
  const [editForm, setEditForm] = useState({ title: "", budget: "", notes: "", committee: "" });
  const [toast, setToast] = useState(null);

  // Filter tasks waiting for approval or show all relevant tasks
  const pendingApprovals = tasks.filter((t) => t.status === "Waiting for Planner Approval");
  const otherTasks = tasks.filter((t) => t.status !== "Waiting for Planner Approval");

  function openEditModal(task) {
    setEditingTask(task);
    setEditForm({
      title: task.title,
      budget: task.budget.toString(),
      notes: task.notes,
      committee: task.committee
    });
  }

  function handleSaveEdit(e) {
    e.preventDefault();
    if (!editingTask) return;

    const updated = {
      ...editingTask,
      title: editForm.title,
      budget: parseInt(editForm.budget) || 0,
      notes: editForm.notes,
      committee: editForm.committee
    };

    onEditTask(updated);
    setEditingTask(null);
    setToast(`Updated task details for "${updated.title}"`);
    setTimeout(() => setToast(null), 4000);
  }

  function handleApprove(task) {
    onApproveTask(task.id);
    setToast(`Approved task "${task.title}"`);
    setTimeout(() => setToast(null), 4000);
  }

  function handleDeny(task) {
    onDenyTask(task.id);
    setToast(`Requested revision for "${task.title}"`);
    setTimeout(() => setToast(null), 4000);
  }

  return (
    <div className="aq-root animate-slide-up">
      <style>{`
        .aq-root { width: 100%; }
        
        .aq-header-banner {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 20px;
          padding: 24px 28px;
          margin-bottom: 30px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          box-shadow: var(--shadow-soft);
        }
        .aq-header-title {
          font-family: var(--font-display);
          font-size: 22px;
          font-weight: 700;
          color: var(--text-dark);
        }
        .aq-header-sub {
          font-size: 13.5px;
          color: var(--text-dark-muted);
          margin-top: 4px;
        }

        .aq-toast {
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

        .aq-section-label {
          font-family: var(--font-display);
          font-size: 18px;
          font-weight: 700;
          color: var(--text-dark);
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .aq-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
          gap: 24px;
          margin-bottom: 40px;
        }

        .aq-card {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 20px;
          padding: 26px;
          box-shadow: var(--shadow-soft);
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          transition: transform 0.25s ease, box-shadow 0.25s ease;
          position: relative;
        }
        .aq-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 16px 32px -8px rgba(139, 79, 209, 0.15);
        }

        .aq-status-pill {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          font-size: 11.5px;
          font-weight: 700;
          padding: 5px 12px;
          border-radius: 100px;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          margin-bottom: 14px;
        }
        .aq-status-pending {
          background: rgba(234, 179, 8, 0.12);
          color: #b45309;
          border: 1px solid rgba(234, 179, 8, 0.3);
        }
        .aq-status-approved {
          background: rgba(34, 197, 94, 0.12);
          color: #15803d;
          border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .aq-status-revision {
          background: rgba(239, 68, 68, 0.12);
          color: #b91c1c;
          border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .aq-card-title {
          font-family: var(--font-display);
          font-size: 18px;
          font-weight: 700;
          color: var(--text-dark);
          line-height: 1.35;
          margin-bottom: 6px;
        }
        .aq-event-tag {
          font-size: 12.5px;
          font-weight: 600;
          color: var(--purple-bright);
          margin-bottom: 14px;
        }

        .aq-meta-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          font-size: 13px;
          color: var(--text-dark-muted);
          margin-bottom: 14px;
          padding-bottom: 12px;
          border-bottom: 1px solid var(--lavender-border);
        }

        .aq-notes {
          font-size: 13.5px;
          color: var(--text-dark);
          line-height: 1.55;
          background: var(--lavender-bg);
          padding: 14px 16px;
          border-radius: 12px;
          margin-bottom: 20px;
        }

        .aq-actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .aq-btn-approve {
          flex: 1;
          background: #16a34a;
          color: #ffffff;
          border: none;
          border-radius: 100px;
          padding: 11px 0;
          font-size: 13px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: background 0.2s ease, transform 0.15s ease;
        }
        .aq-btn-approve:hover {
          background: #15803d;
          transform: translateY(-1px);
        }
        .aq-btn-deny {
          flex: 1;
          background: transparent;
          color: #dc2626;
          border: 1px solid rgba(220, 38, 38, 0.3);
          border-radius: 100px;
          padding: 11px 0;
          font-size: 13px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          transition: background 0.2s ease;
        }
        .aq-btn-deny:hover {
          background: rgba(220, 38, 38, 0.06);
          border-color: #dc2626;
        }
        .aq-btn-edit {
          background: rgba(139, 79, 209, 0.1);
          color: var(--purple-main);
          border: 1px solid rgba(139, 79, 209, 0.2);
          border-radius: 100px;
          padding: 11px 16px;
          font-size: 13px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
          transition: background 0.2s ease;
        }
        .aq-btn-edit:hover {
          background: var(--purple-main);
          color: #ffffff;
        }

        /* Edit Task Modal Overlay */
        .aq-modal-overlay {
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(15, 8, 29, 0.7);
          backdrop-filter: blur(8px);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }
        .aq-modal-card {
          background: #ffffff;
          border-radius: 24px;
          padding: 36px;
          width: 100%;
          max-width: 540px;
          box-shadow: 0 24px 60px rgba(0,0,0,0.3);
        }
        .aq-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 24px;
        }
        .aq-modal-title {
          font-family: var(--font-display);
          font-size: 22px;
          font-weight: 700;
          color: var(--text-dark);
        }
        .aq-modal-field {
          margin-bottom: 18px;
        }
        .aq-modal-label {
          display: block;
          font-size: 12px;
          font-weight: 700;
          color: var(--text-dark-muted);
          margin-bottom: 6px;
          text-transform: uppercase;
        }
        .aq-modal-input, .aq-modal-textarea {
          width: 100%;
          background: var(--lavender-bg);
          border: 1.5px solid var(--lavender-border);
          border-radius: 12px;
          padding: 12px 14px;
          font-size: 14px;
          color: var(--text-dark);
          font-family: var(--font-sans);
        }
        .aq-modal-input:focus, .aq-modal-textarea:focus {
          outline: none;
          border-color: var(--purple-bright);
        }
        .aq-modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          margin-top: 24px;
        }
      `}</style>

      {toast && (
        <div className="aq-toast animate-slide-up">
          <CheckCircle2 size={18} />
          {toast}
        </div>
      )}

      {/* Header Banner explaining the Workflow */}
      <div className="aq-header-banner">
        <div>
          <h2 className="aq-header-title">Event Planner Approvals</h2>
          <p className="aq-header-sub">
            Review completed committee tasks, approve deliverables, or edit task parameters. Any edits update live for committee members.
          </p>
        </div>
        <div style={{ background: "rgba(139,79,209,0.1)", padding: "12px 18px", borderRadius: "100px", color: "var(--purple-main)", fontWeight: 700, fontSize: "13px", whitespace: "nowrap" }}>
          {pendingApprovals.length} Pending Approval
        </div>
      </div>

      {/* Pending Approvals Section */}
      <h3 className="aq-section-label">
        <Clock size={18} color="var(--purple-bright)" />
        Tasks Awaiting Your Approval ({pendingApprovals.length})
      </h3>

      {pendingApprovals.length === 0 ? (
        <div style={{ background: "#ffffff", padding: "50px 20px", borderRadius: "20px", textAlign: "center", color: "var(--text-dark-muted)", marginBottom: "32px", border: "1px dashed var(--lavender-border)" }}>
          <CheckCircle2 size={36} color="#16a34a" style={{ marginBottom: "10px" }} />
          <div style={{ fontWeight: 600, fontSize: "15px" }}>No tasks waiting for approval right now!</div>
        </div>
      ) : (
        <div className="aq-grid">
          {pendingApprovals.map((task) => (
            <div className="aq-card" key={task.id}>
              <div>
                <span className="aq-status-pill aq-status-pending">
                  <Clock size={12} /> Waiting for Planner Approval
                </span>
                <h4 className="aq-card-title">{task.title}</h4>
                <div className="aq-event-tag">📌 {task.eventTitle}</div>

                <div className="aq-meta-row">
                  <span>Assigned to: <strong>{task.assignedTo}</strong></span>
                  <span style={{ fontWeight: 700, color: "var(--text-dark)" }}>{task.budget.toLocaleString()} EGP</span>
                </div>

                <div className="aq-notes">
                  <strong>Deliverable / Notes:</strong><br />
                  {task.notes}
                </div>
              </div>

              <div className="aq-actions">
                <button className="aq-btn-approve" onClick={() => handleApprove(task)}>
                  <CheckCircle2 size={16} /> Approve Task
                </button>
                <button className="aq-btn-deny" onClick={() => handleDeny(task)}>
                  <XCircle size={16} /> Request Revision
                </button>
                <button className="aq-btn-edit" title="Edit task budget or details" onClick={() => openEditModal(task)}>
                  <Edit3 size={15} /> Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Previously Approved or Revision Requested Tasks */}
      {otherTasks.length > 0 && (
        <>
          <h3 className="aq-section-label" style={{ marginTop: "32px" }}>
            <Sparkles size={18} color="var(--purple-bright)" />
            Reviewed & Active Tasks ({otherTasks.length})
          </h3>
          <div className="aq-grid">
            {otherTasks.map((task) => {
              const isApproved = task.status === "Approved";
              return (
                <div className="aq-card" key={task.id}>
                  <div>
                    <span className={`aq-status-pill ${isApproved ? "aq-status-approved" : "aq-status-revision"}`}>
                      {isApproved ? <CheckCircle2 size={12} /> : <XCircle size={12} />} {task.status}
                    </span>
                    <h4 className="aq-card-title">{task.title}</h4>
                    <div className="aq-event-tag">📌 {task.eventTitle}</div>

                    <div className="aq-meta-row">
                      <span>Assigned to: <strong>{task.assignedTo}</strong></span>
                      <span style={{ fontWeight: 700 }}>{task.budget.toLocaleString()} EGP</span>
                    </div>

                    <div className="aq-notes">{task.notes}</div>
                  </div>

                  <div className="aq-actions">
                    <button className="aq-btn-edit" style={{ width: "100%", justifyContent: "center" }} onClick={() => openEditModal(task)}>
                      <Edit3 size={15} /> Edit Task Parameters
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="aq-modal-overlay">
          <form className="aq-modal-card animate-slide-up" onSubmit={handleSaveEdit}>
            <div className="aq-modal-header">
              <h3 className="aq-modal-title">Edit Task Details</h3>
              <button
                type="button"
                style={{ border: "none", background: "none", cursor: "pointer", color: "var(--text-dark-muted)" }}
                onClick={() => setEditingTask(null)}
              >
                <X size={20} />
              </button>
            </div>

            <div className="aq-modal-field">
              <label className="aq-modal-label">Task Title</label>
              <input
                className="aq-modal-input"
                type="text"
                value={editForm.title}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                required
              />
            </div>

            <div className="aq-modal-field">
              <label className="aq-modal-label">Allocated Budget (EGP)</label>
              <input
                className="aq-modal-input"
                type="number"
                value={editForm.budget}
                onChange={(e) => setEditForm({ ...editForm, budget: e.target.value })}
                required
              />
            </div>

            <div className="aq-modal-field">
              <label className="aq-modal-label">Assigned Committee</label>
              <input
                className="aq-modal-input"
                type="text"
                value={editForm.committee}
                onChange={(e) => setEditForm({ ...editForm, committee: e.target.value })}
                required
              />
            </div>

            <div className="aq-modal-field">
              <label className="aq-modal-label">Task Description / Planner Notes</label>
              <textarea
                className="aq-modal-textarea"
                rows={3}
                value={editForm.notes}
                onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
              />
            </div>

            <div className="aq-modal-actions">
              <button
                type="button"
                style={{ padding: "10px 20px", border: "1px solid var(--lavender-border)", background: "#fff", borderRadius: "100px", fontWeight: 600, cursor: "pointer" }}
                onClick={() => setEditingTask(null)}
              >
                Cancel
              </button>
              <button
                type="submit"
                style={{ padding: "10px 24px", border: "none", background: "var(--purple-main)", color: "#fff", borderRadius: "100px", fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: "6px" }}
              >
                <Save size={16} /> Save Changes
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
