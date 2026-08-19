import React, { useState } from "react";
import { Calendar, MapPin, DollarSign, Clock, Search, Filter, Plus, ArrowUpRight, CheckCircle, AlertCircle, FileText } from "lucide-react";

const INITIAL_EVENTS = [
  {
    id: 1,
    title: "Children's Day Festival 2026",
    location: "Nasr City Youth Center",
    date: "Oct 24, 2026 · 10:00 AM",
    budget: 45000,
    status: "Approved",
    committee: "Operations",
    progress: 85,
    description: "Annual fun fair for 300+ children with interactive workshops, gifts, performance stage, and live entertainment."
  },
  {
    id: 2,
    title: "Blood Drive Marathon",
    location: "Cairo University Main Campus",
    date: "Nov 05, 2026 · 09:00 AM",
    budget: 28000,
    status: "Pending Review",
    committee: "PR & Branding",
    progress: 50,
    description: "Collaborative campus blood drive targeting 500+ blood donations with medical team support and partner sponsors."
  },
  {
    id: 3,
    title: "Ramadan Food Packs Distribution",
    location: "Resala Central Warehouse, Giza",
    date: "Mar 10, 2026 · 08:00 AM",
    budget: 150000,
    status: "Approved",
    committee: "Operations",
    progress: 92,
    description: "Packing & distributing 5,000+ essential Ramadan dry food boxes to families across governorates."
  }
];

export default function MyEvents({ onNavigateToCreate }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("All");

  const filteredEvents = INITIAL_EVENTS.filter((evt) => {
    const matchesSearch = evt.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          evt.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === "All" || evt.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const statusColors = {
    Approved: { bg: "rgba(34, 197, 94, 0.12)", text: "#16a34a", border: "rgba(34, 197, 94, 0.3)" },
    "Pending Review": { bg: "rgba(234, 179, 8, 0.12)", text: "#ca8a04", border: "rgba(234, 179, 8, 0.3)" },
    Draft: { bg: "rgba(148, 163, 184, 0.15)", text: "#64748b", border: "rgba(148, 163, 184, 0.3)" }
  };

  const totalBudget = INITIAL_EVENTS.reduce((acc, curr) => acc + curr.budget, 0);

  return (
    <div className="me-root animate-slide-up">
      <style>{`
        .me-root { width: 100%; }
        .me-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 16px;
          margin-bottom: 32px;
        }
        .me-stat-card {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 16px;
          padding: 20px 22px;
          display: flex;
          align-items: center;
          gap: 16px;
          box-shadow: var(--shadow-soft);
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .me-stat-card:hover {
          transform: translateY(-2px);
          box-shadow: var(--shadow-glow);
        }
        .me-stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 14px;
          background: rgba(139, 79, 209, 0.1);
          color: var(--purple-bright);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .me-stat-num {
          font-family: var(--font-display);
          font-size: 24px;
          font-weight: 700;
          color: var(--text-dark);
          line-height: 1.1;
        }
        .me-stat-lbl {
          font-size: 12.5px;
          color: var(--text-dark-muted);
          margin-top: 3px;
          font-weight: 500;
        }

        .me-controls {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 16px;
          margin-bottom: 24px;
          flex-wrap: wrap;
        }
        .me-search-box {
          display: flex;
          align-items: center;
          gap: 10px;
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 100px;
          padding: 10px 18px;
          flex: 1;
          min-width: 260px;
          max-width: 440px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }
        .me-search-input {
          border: none;
          background: transparent;
          outline: none;
          width: 100%;
          font-size: 14px;
          color: var(--text-dark);
          font-family: var(--font-sans);
        }
        .me-filters {
          display: flex;
          gap: 6px;
          background: rgba(139, 79, 209, 0.06);
          padding: 4px;
          border-radius: 100px;
        }
        .me-filter-btn {
          border: none;
          background: transparent;
          padding: 8px 16px;
          border-radius: 100px;
          font-size: 12.5px;
          font-weight: 600;
          color: var(--text-dark-muted);
          cursor: pointer;
          transition: background 0.2s ease, color 0.2s ease;
        }
        .me-filter-btn.active {
          background: var(--purple-bright);
          color: #ffffff;
          box-shadow: 0 4px 12px rgba(139, 79, 209, 0.3);
        }

        .me-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
          gap: 22px;
        }
        .me-card {
          background: #ffffff;
          border: 1px solid var(--lavender-border);
          border-radius: 20px;
          padding: 26px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          box-shadow: var(--shadow-soft);
          transition: all 0.25s ease;
          position: relative;
          overflow: hidden;
        }
        .me-card::before {
          content: "";
          position: absolute;
          top: 0; left: 0; right: 0;
          height: 4px;
          background: linear-gradient(90deg, var(--purple-bright), var(--gold-accent));
          opacity: 0;
          transition: opacity 0.25s ease;
        }
        .me-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 20px 40px -10px rgba(139, 79, 209, 0.15);
          border-color: rgba(139, 79, 209, 0.4);
        }
        .me-card:hover::before { opacity: 1; }

        .me-card-top {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 12px;
          margin-bottom: 12px;
        }
        .me-card-title {
          font-family: var(--font-display);
          font-size: 19px;
          font-weight: 700;
          color: var(--text-dark);
          line-height: 1.3;
        }
        .me-badge {
          font-size: 11px;
          font-weight: 700;
          padding: 5px 12px;
          border-radius: 100px;
          white-space: nowrap;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .me-desc {
          font-size: 13.5px;
          color: var(--text-dark-muted);
          line-height: 1.55;
          margin-bottom: 20px;
        }

        .me-meta-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 20px;
          font-size: 13px;
          color: var(--text-dark-muted);
        }
        .me-meta-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .me-meta-item svg { color: var(--purple-bright); }

        .me-progress-bar {
          height: 6px;
          background: rgba(139, 79, 209, 0.1);
          border-radius: 100px;
          overflow: hidden;
          margin-bottom: 16px;
        }
        .me-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--purple-main), var(--purple-bright));
          border-radius: 100px;
        }

        .me-card-foot {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-top: 16px;
          border-top: 1px solid rgba(230, 216, 248, 0.6);
        }
        .me-budget-val {
          font-size: 15px;
          font-weight: 700;
          color: var(--text-dark);
        }
        .me-action-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          background: rgba(139, 79, 209, 0.08);
          color: var(--purple-main);
          border: none;
          padding: 8px 14px;
          border-radius: 100px;
          font-size: 12.5px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s ease, color 0.2s ease;
        }
        .me-action-btn:hover {
          background: var(--purple-main);
          color: #ffffff;
        }

        @media (max-width: 640px) {
          .me-controls { flex-direction: column; align-items: stretch; }
          .me-search-box { max-width: 100%; }
        }
      `}</style>

      {/* Stats Summary */}
      <div className="me-stats-grid">
        <div className="me-stat-card">
          <div className="me-stat-icon"><Calendar size={22} /></div>
          <div>
            <div className="me-stat-num">{INITIAL_EVENTS.length}</div>
            <div className="me-stat-lbl">Total Events</div>
          </div>
        </div>
        <div className="me-stat-card">
          <div className="me-stat-icon"><CheckCircle size={22} /></div>
          <div>
            <div className="me-stat-num">{INITIAL_EVENTS.filter(e => e.status === "Approved").length}</div>
            <div className="me-stat-lbl">Approved Events</div>
          </div>
        </div>
        <div className="me-stat-card">
          <div className="me-stat-icon"><DollarSign size={22} /></div>
          <div>
            <div className="me-stat-num">{totalBudget.toLocaleString()} EGP</div>
            <div className="me-stat-lbl">Combined Budget</div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="me-controls">
        <div className="me-search-box">
          <Search size={16} color="var(--text-dark-muted)" />
          <input
            className="me-search-input"
            type="text"
            placeholder="Search events by title or venue..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="me-filters">
          {["All", "Approved", "Pending Review", "Draft"].map((st) => (
            <button
              key={st}
              className={`me-filter-btn ${filterStatus === st ? "active" : ""}`}
              onClick={() => setFilterStatus(st)}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Event Cards Grid */}
      {filteredEvents.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "var(--text-dark-muted)" }}>
          No events found matching your search.
        </div>
      ) : (
        <div className="me-grid">
          {filteredEvents.map((evt) => {
            const stStyle = statusColors[evt.status] || statusColors.Draft;
            return (
              <div className="me-card" key={evt.id}>
                <div>
                  <div className="me-card-top">
                    <h3 className="me-card-title">{evt.title}</h3>
                    <span
                      className="me-badge"
                      style={{
                        background: stStyle.bg,
                        color: stStyle.text,
                        border: `1px solid ${stStyle.border}`
                      }}
                    >
                      {evt.status}
                    </span>
                  </div>

                  <p className="me-desc">{evt.description}</p>

                  <div className="me-meta-list">
                    <div className="me-meta-item">
                      <Clock size={15} />
                      <span>{evt.date}</span>
                    </div>
                    <div className="me-meta-item">
                      <MapPin size={15} />
                      <span>{evt.location}</span>
                    </div>
                  </div>

                  <div className="me-progress-bar">
                    <div className="me-progress-fill" style={{ width: `${evt.progress}%` }} />
                  </div>
                </div>

                <div className="me-card-foot">
                  <span className="me-budget-val">{evt.budget.toLocaleString()} EGP</span>
                  <button className="me-action-btn">
                    Details <ArrowUpRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
