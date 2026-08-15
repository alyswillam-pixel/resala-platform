import React, { useState } from "react";
import { Calendar, PlusCircle, LayoutDashboard, CheckCircle2 } from "lucide-react";

const PLANNER_TABS = [
  { key: "events", label: "My events", icon: Calendar },
  { key: "create", label: "Create event", icon: PlusCircle },
];

const COMMITTEE_TABS = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "approvals", label: "Approvals", icon: CheckCircle2 },
];

export default function ResalaHome() {
  // TEMPORARY — until real auth is wired, this stands in for "who's logged in"
  const [role, setRole] = useState("planner"); // "planner" | "committee_member"
  const tabs = role === "planner" ? PLANNER_TABS : COMMITTEE_TABS;
  const [activeTab, setActiveTab] = useState(tabs[0].key);

  function switchRole(nextRole) {
    setRole(nextRole);
    const nextTabs = nextRole === "planner" ? PLANNER_TABS : COMMITTEE_TABS;
    setActiveTab(nextTabs[0].key);
  }

  return (
    <div className="rh-root">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,340..700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

        .rh-root {
          --ink: #150C24;
          --purple: #5B2A86;
          --purple-bright: #8B4FD1;
          --lavender: #F3EDFB;
          --lavender-line: #E4D6F5;
          --gold: #E3AE4E;
          --text-hi: #F7F3FE;
          --text-mid: #C9BADD;
          --text-on-light: #372350;
          --text-on-light-mid: #6C5A85;
          font-family: 'Inter', sans-serif;
          min-height: 100vh;
          width: 100%;
          background: var(--lavender);
        }
        .rh-root * { box-sizing: border-box; }
        .rh-mono { font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.1em; text-transform: uppercase; }
        .rh-display { font-family: 'Fraunces', serif; }

        .rh-devbar {
          background: #2A1B42;
          color: var(--text-mid);
          font-size: 12px;
          padding: 8px 6vw;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .rh-devbar button {
          font-size: 11.5px;
          font-weight: 600;
          padding: 5px 12px;
          border-radius: 100px;
          border: 1px solid rgba(247,243,254,0.25);
          background: transparent;
          color: var(--text-mid);
          cursor: pointer;
        }
        .rh-devbar button.active { background: var(--text-hi); color: var(--ink); border-color: var(--text-hi); }

        .rh-topnav {
          background: var(--ink);
          padding: 20px 6vw 0;
        }
        .rh-topnav-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 22px;
        }
        .rh-brand {
          display: flex; align-items: center; gap: 10px;
          color: var(--text-hi); font-size: 15px; font-weight: 600;
        }
        .rh-brand-mark {
          width: 26px; height: 26px; border-radius: 7px;
          background: linear-gradient(135deg, var(--purple-bright), var(--purple));
          display: flex; align-items: center; justify-content: center;
          font-family: 'Fraunces', serif; color: var(--text-hi); font-size: 15px;
        }
        .rh-role-badge {
          font-size: 11px;
          color: var(--text-mid);
        }

        .rh-tabs { display: flex; gap: 4px; }
        .rh-tab {
          display: flex; align-items: center; gap: 7px;
          padding: 12px 18px;
          font-size: 13.5px;
          font-weight: 600;
          color: var(--text-mid);
          background: transparent;
          border: none;
          border-bottom: 2px solid transparent;
          cursor: pointer;
        }
        .rh-tab.active { color: var(--text-hi); border-bottom-color: var(--gold); }
        .rh-tab:hover:not(.active) { color: var(--text-hi); }
        .rh-tab:focus-visible { outline: 2px solid var(--gold); outline-offset: 2px; }

        .rh-content { padding: 48px 6vw 80px; }
        .rh-kicker { font-size: 11.5px; color: var(--text-on-light-mid); margin-bottom: 10px; }
        .rh-h1 { font-family: 'Fraunces', serif; font-size: 30px; color: var(--text-on-light); margin: 0 0 8px; }
        .rh-sub { font-size: 14.5px; color: var(--text-on-light-mid); margin-bottom: 34px; max-width: 480px; line-height: 1.6; }

        .rh-placeholder {
          background: #fff;
          border: 1px dashed var(--lavender-line);
          border-radius: 16px;
          padding: 60px 30px;
          text-align: center;
          color: var(--text-on-light-mid);
          font-size: 14px;
        }

        @media (max-width: 640px) {
          .rh-topnav-row { flex-direction: column; align-items: flex-start; gap: 10px; }
          .rh-tabs { overflow-x: auto; width: 100%; }
        }
      `}</style>

      {/* DEV-ONLY role switcher — remove once real auth decides this */}
      <div className="rh-devbar rh-mono">
        Preview as:
        <button className={role === "planner" ? "active" : ""} onClick={() => switchRole("planner")}>Planner</button>
        <button className={role === "committee_member" ? "active" : ""} onClick={() => switchRole("committee_member")}>Committee member</button>
      </div>

      <div className="rh-topnav">
        <div className="rh-topnav-row">
          <div className="rh-brand">
            <span className="rh-brand-mark">R</span>
            Resala Platform
          </div>
          <div className="rh-role-badge rh-mono">
            {role === "planner" ? "Signed in · Planner" : "Signed in · Operations"}
          </div>
        </div>
        <div className="rh-tabs">
          {tabs.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              className={`rh-tab ${activeTab === key ? "active" : ""}`}
              onClick={() => setActiveTab(key)}
            >
              <Icon size={15} /> {label}
            </button>
          ))}
        </div>
      </div>

      <div className="rh-content">
        {role === "planner" && activeTab === "events" && (
          <>
            <div className="rh-kicker rh-mono">Your events</div>
            <h1 className="rh-h1">My events</h1>
            <p className="rh-sub">Every event you've created, and where each one stands.</p>
            <div className="rh-placeholder">Event list goes here — connects once the backend's ready.</div>
          </>
        )}
        {role === "planner" && activeTab === "create" && (
          <>
            <div className="rh-kicker rh-mono">New event</div>
            <h1 className="rh-h1">Create event</h1>
            <p className="rh-sub">Answer the five required questions and set a budget.</p>
            <div className="rh-placeholder">Create-event form goes here.</div>
          </>
        )}
        {role === "committee_member" && activeTab === "dashboard" && (
          <>
            <div className="rh-kicker rh-mono">Incoming work</div>
            <h1 className="rh-h1">Dashboard</h1>
            <p className="rh-sub">Requests routed to your committee, and their status.</p>
            <div className="rh-placeholder">Committee request list goes here.</div>
          </>
        )}
        {role === "committee_member" && activeTab === "approvals" && (
          <>
            <div className="rh-kicker rh-mono">Awaiting sign-off</div>
            <h1 className="rh-h1">Approvals</h1>
            <p className="rh-sub">Requests waiting for the planner's approval before moving on.</p>
            <div className="rh-placeholder">Approval queue goes here.</div>
          </>
        )}
      </div>
    </div>
  );
}