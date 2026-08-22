import { useState } from "react";
import { Calendar, PlusCircle, LayoutDashboard, CheckCircle2, User, LogOut, Sparkles } from "lucide-react";
import CreateEvent from "../components/CreateEvent";
import MyEvents from "../components/MyEvents";
import CommitteeDashboard from "../components/CommitteeDashboard";
import ApprovalsQueue from "../components/ApprovalsQueue";

const PLANNER_TABS = [
  { key: "events", label: "My events", icon: Calendar },
  { key: "create", label: "Create event", icon: PlusCircle },
  { key: "approvals", label: "Approvals", icon: CheckCircle2 },
];

const COMMITTEE_TABS = [
  { key: "dashboard", label: "My Assigned Tasks", icon: LayoutDashboard },
  { key: "approvals", label: "Planner Approvals Queue", icon: CheckCircle2 },
];

const INITIAL_SHARED_TASKS = [
  {
    id: 1,
    title: "Design Instagram Banner & Story Poster",
    eventTitle: "Blood Drive Marathon",
    committee: "Branding",
    assignedTo: "Branding Team (Karim & Huda)",
    budget: 3500,
    status: "Waiting for Planner Approval",
    submittedAt: "Today at 2:15 PM",
    notes: "Created 3 Instagram story variants and 1 printable A3 campus flyer."
  },
  {
    id: 2,
    title: "Build Registration Landing Page & QR Form",
    eventTitle: "Children's Day Festival 2026",
    committee: "Tech",
    assignedTo: "Tech Team (Omar & Youssef)",
    budget: 5000,
    status: "Waiting for Planner Approval",
    submittedAt: "Yesterday at 6:30 PM",
    notes: "Web registration form connected to volunteer database with QR check-in generation."
  },
  {
    id: 3,
    title: "Print Roll-Up Banners & 200 Volunteer T-Shirts",
    eventTitle: "Ramadan Food Packs Distribution",
    committee: "Operations",
    assignedTo: "Logistics Team (Ahmed & Mostafa)",
    budget: 18500,
    status: "In Progress",
    submittedAt: "2 days ago",
    notes: "Working with printing vendor in Dokki for t-shirt proofs and banners."
  }
];

export default function ResalaHome({ userAuth, onNavigateToLogin }) {
  const [role, setRole] = useState(userAuth?.role || "planner"); // "planner" | "committee_member"
  const [tasks, setTasks] = useState(INITIAL_SHARED_TASKS);
  const tabs = role === "planner" ? PLANNER_TABS : COMMITTEE_TABS;
  const [activeTab, setActiveTab] = useState(tabs[0].key);

  function switchRole(nextRole) {
    setRole(nextRole);
    const nextTabs = nextRole === "planner" ? PLANNER_TABS : COMMITTEE_TABS;
    setActiveTab(nextTabs[0].key);
  }

  const handleApproveTask = (id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: "Approved" } : t))
    );
  };

  const handleDenyTask = (id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: "Revision Requested" } : t))
    );
  };

  const handleEditTask = (updatedTask) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  };

  const handleSubmitTaskForApproval = (id) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: "Waiting for Planner Approval" } : t))
    );
  };

  return (
    <div className="rh-root">
      <style>{`
        .rh-root {
          min-height: 100vh;
          width: 100%;
          background-color: var(--lavender-bg);
          color: var(--text-dark);
          font-family: var(--font-sans);
        }

        /* Top Dev Switcher Bar */
        .rh-devbar {
          background: #0F172A;
          color: var(--text-light-muted);
          font-size: 12px;
          font-family: var(--font-mono);
          padding: 10px 4vw;
          display: flex;
          align-items: center;
          gap: 12px;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }
        .rh-devbar-btn {
          font-size: 11.5px;
          font-weight: 600;
          padding: 4px 14px;
          border-radius: 100px;
          border: 1px solid rgba(255,255,255,0.2);
          background: transparent;
          color: var(--text-light-muted);
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .rh-devbar-btn.active {
          background: var(--purple-bright);
          color: #ffffff;
          border-color: var(--purple-bright);
          box-shadow: 0 0 12px rgba(139, 79, 209, 0.4);
        }

        /* Glassmorphic Navbar Header */
        .rh-header-wrap {
          background: #0F172A;
          position: sticky;
          top: 0;
          z-index: 100;
          box-shadow: 0 10px 30px rgba(15, 8, 29, 0.4);
        }
        .rh-header {
          max-width: 1200px;
          margin: 0 auto;
          padding: 22px 24px 0;
        }

        .rh-top-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 24px;
        }
        .rh-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          color: var(--text-light);
          font-size: 18px;
          font-weight: 800;
          letter-spacing: -0.02em;
        }
        .rh-brand-mark {
          width: 32px;
          height: 32px;
          border-radius: 10px;
          background: linear-gradient(135deg, var(--purple-bright), var(--purple-main));
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: var(--font-display);
          color: var(--text-light);
          font-size: 18px;
          box-shadow: 0 4px 14px rgba(139, 79, 209, 0.4);
        }

        .rh-user-badge {
          display: flex;
          align-items: center;
          gap: 10px;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.12);
          padding: 6px 14px;
          border-radius: 100px;
          color: var(--text-light);
          font-size: 12.5px;
          font-weight: 600;
        }

        /* Centered Tabs */
        .rh-tabs-nav {
          display: flex;
          gap: 8px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .rh-tab-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 14px 22px;
          font-size: 14px;
          font-weight: 600;
          color: var(--text-light-muted);
          background: transparent;
          border: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .rh-tab-btn:hover:not(.active) {
          color: var(--text-light);
        }
        .rh-tab-btn.active {
          color: var(--text-light);
          border-bottom-color: var(--gold-accent);
        }

        /* Main Centered Content Container */
        .rh-main-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 40px 24px 80px;
        }
      `}</style>

      {/* Dev preview bar */}
      <div className="rh-devbar">
        <span><Sparkles size={13} style={{ display: "inline", marginRight: "4px" }} /> Preview Role:</span>
        <button className={`rh-devbar-btn ${role === "planner" ? "active" : ""}`} onClick={() => switchRole("planner")}>
          Event Planner
        </button>
        <button className={`rh-devbar-btn ${role === "committee_member" ? "active" : ""}`} onClick={() => switchRole("committee_member")}>
          Committee Member
        </button>
        {onNavigateToLogin && (
          <button className="rh-devbar-btn" style={{ marginLeft: "auto" }} onClick={onNavigateToLogin}>
            <LogOut size={12} style={{ display: "inline", marginRight: "4px" }} /> Go to Login Page
          </button>
        )}
      </div>

      {/* Main Glass Header */}
      <div className="rh-header-wrap">
        <header className="rh-header">
          <div className="rh-top-row">
            <div className="rh-brand">
              <span className="rh-brand-mark">R</span>
              Resala Platform
            </div>

            <div className="rh-user-badge">
              <User size={14} color="var(--gold-accent)" />
              <span>{role === "planner" ? "Event Planner Workspace" : "Committee Member Workspace"}</span>
            </div>
          </div>

          <nav className="rh-tabs-nav">
            {tabs.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                className={`rh-tab-btn ${activeTab === key ? "active" : ""}`}
                onClick={() => setActiveTab(key)}
              >
                <Icon size={16} /> {label}
              </button>
            ))}
          </nav>
        </header>
      </div>

      {/* Centered Content Body */}
      <main className="rh-main-container">
        {role === "planner" && activeTab === "events" && (
          <MyEvents onNavigateToCreate={() => setActiveTab("create")} />
        )}
        {role === "planner" && activeTab === "create" && (
          <CreateEvent
            onNavigateToEvents={() => setActiveTab("events")}
          />
        )}
        {role === "planner" && activeTab === "approvals" && (
          <ApprovalsQueue
            tasks={tasks}
            onApproveTask={handleApproveTask}
            onDenyTask={handleDenyTask}
            onEditTask={handleEditTask}
            role={role}
          />
        )}

        {role === "committee_member" && activeTab === "dashboard" && (
          <CommitteeDashboard
            tasks={tasks}
            onSubmitForApproval={handleSubmitTaskForApproval}
          />
        )}
        {role === "committee_member" && activeTab === "approvals" && (
          <ApprovalsQueue
            tasks={tasks}
            onApproveTask={handleApproveTask}
            onDenyTask={handleDenyTask}
            onEditTask={handleEditTask}
            role={role}
          />
        )}
      </main>
    </div>
  );
}