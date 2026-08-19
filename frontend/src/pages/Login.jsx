import React, { useState } from "react";
import { ArrowRight, ArrowLeft, Shield, Sparkles, UserCheck, Users, Mail, Lock, User } from "lucide-react";

const COMMITTEES = ["Operations", "Branding", "PR & Fundraising", "HR", "Tech"];

export default function ResalaLogin({ onLoginSuccess, onBackToHome }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [role, setRole] = useState("planner"); // "planner" | "committee_member"
  const [committee, setCommittee] = useState(COMMITTEES[0]);

  function handleSubmit(e) {
    e.preventDefault();
    console.log("submit", { mode, role, committee });
    if (onLoginSuccess) {
      onLoginSuccess({ mode, role, committee });
    }
  }

  return (
    <div className="rl-root animate-slide-up">
      <style>{`
        .rl-root {
          --ink-bg: #0F172A;
          --ink-card: rgba(15, 23, 42, 0.85);
          --purple: #1D4ED8;
          --purple-bright: #2563EB;
          --gold: #38BDF8;
          --text-hi: #F8FAFC;
          --text-mid: #94A3B8;
          font-family: var(--font-sans);
          background: var(--ink-bg);
          color: var(--text-hi);
          min-height: 100vh;
          width: 100%;
          display: flex;
          flex-direction: column;
          position: relative;
          overflow: hidden;
        }
        .rl-root * { box-sizing: border-box; }

        /* Animated Mesh Background Orbs */
        .rl-root::before {
          content: "";
          position: absolute;
          top: -15%;
          left: 50%;
          transform: translateX(-50%);
          width: 750px;
          height: 750px;
          background: radial-gradient(circle, rgba(37,99,235,0.32) 0%, rgba(29,78,216,0.1) 50%, transparent 70%);
          filter: blur(40px);
          pointer-events: none;
          animation: floatOrb 10s ease-in-out infinite;
        }
        .rl-root::after {
          content: "";
          position: absolute;
          bottom: -20%;
          right: -10%;
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(56,189,248,0.2) 0%, transparent 60%);
          filter: blur(50px);
          pointer-events: none;
        }

        .rl-nav {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 32px 7vw;
          position: relative;
          z-index: 2;
        }
        .rl-brand {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 17px;
          font-weight: 800;
          letter-spacing: -0.02em;
        }
        .rl-brand-mark {
          width: 32px; height: 32px;
          border-radius: 10px;
          background: linear-gradient(135deg, var(--purple-bright), var(--purple));
          display: flex; align-items: center; justify-content: center;
          font-family: var(--font-display);
          font-size: 18px;
          box-shadow: 0 4px 16px rgba(139, 79, 209, 0.4);
        }

        .rl-wrap {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px 5vw 60px;
          position: relative;
          z-index: 2;
        }
        .rl-card {
          width: 100%;
          max-width: 440px;
          background: var(--ink-card);
          border: 1px solid rgba(248, 245, 254, 0.15);
          border-radius: 26px;
          padding: 44px 38px;
          backdrop-filter: blur(20px);
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 79, 209, 0.15);
        }

        .rl-eyebrow {
          font-family: var(--font-mono);
          font-size: 11px;
          color: var(--gold);
          letter-spacing: 0.14em;
          text-transform: uppercase;
          margin-bottom: 12px;
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .rl-h1 {
          font-family: var(--font-display);
          font-size: 32px;
          font-weight: 700;
          margin: 0 0 10px;
          line-height: 1.2;
        }
        .rl-sub {
          font-size: 14px;
          color: var(--text-mid);
          margin-bottom: 30px;
          line-height: 1.55;
        }

        .rl-toggle {
          display: flex;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 100px;
          padding: 4px;
          margin-bottom: 28px;
        }
        .rl-toggle button {
          flex: 1;
          border: none;
          background: transparent;
          color: var(--text-mid);
          font-size: 13.5px;
          font-weight: 600;
          padding: 11px 0;
          border-radius: 100px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .rl-toggle button.active {
          background: var(--text-hi);
          color: var(--ink-bg);
          box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .rl-field { margin-bottom: 20px; }
        .rl-label {
          display: block;
          font-family: var(--font-mono);
          font-size: 11px;
          color: var(--text-mid);
          margin-bottom: 8px;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .rl-input-wrap {
          position: relative;
          display: flex;
          align-items: center;
        }
        .rl-input-icon {
          position: absolute;
          left: 14px;
          color: var(--text-mid);
          pointer-events: none;
        }
        .rl-input, .rl-select {
          width: 100%;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(248, 245, 254, 0.16);
          border-radius: 12px;
          padding: 13px 14px 13px 42px;
          font-size: 14px;
          color: var(--text-hi);
          font-family: var(--font-sans);
          transition: all 0.2s ease;
        }
        .rl-input::placeholder { color: rgba(248,245,254,0.3); }
        .rl-input:focus, .rl-select:focus {
          outline: none;
          border-color: var(--purple-bright);
          box-shadow: 0 0 20px rgba(139, 79, 209, 0.35);
          background: rgba(255,255,255,0.08);
        }
        .rl-select { appearance: none; cursor: pointer; padding-left: 14px; }

        .rl-role-row { display: flex; gap: 10px; margin-bottom: 20px; }
        .rl-role-btn {
          flex: 1;
          border: 1px solid rgba(248,245,254,0.15);
          background: rgba(255,255,255,0.03);
          color: var(--text-mid);
          border-radius: 12px;
          padding: 12px 10px;
          font-size: 12.5px;
          font-weight: 600;
          cursor: pointer;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          transition: all 0.2s ease;
        }
        .rl-role-btn.active {
          border-color: var(--purple-bright);
          color: var(--text-hi);
          background: rgba(139, 79, 209, 0.25);
          box-shadow: 0 0 15px rgba(139, 79, 209, 0.3);
        }

        .rl-submit {
          width: 100%;
          background: linear-gradient(135deg, var(--purple-bright), var(--purple));
          color: var(--text-hi);
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
          margin-top: 10px;
          transition: all 0.2s ease;
          box-shadow: 0 8px 24px rgba(139, 79, 209, 0.35);
        }
        .rl-submit:hover {
          transform: translateY(-2px);
          box-shadow: 0 12px 30px rgba(139, 79, 209, 0.5);
        }

        .rl-back {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: var(--text-mid);
          background: none;
          border: none;
          cursor: pointer;
          margin-top: 24px;
          transition: color 0.2s ease;
        }
        .rl-back:hover { color: var(--text-hi); }
      `}</style>

      <nav className="rl-nav">
        <div className="rl-brand">
          <span className="rl-brand-mark">R</span>
          Resala Platform
        </div>
      </nav>

      <div className="rl-wrap">
        <div className="rl-card">
          <div className="rl-eyebrow">
            <Sparkles size={13} />
            {mode === "login" ? "Welcome Back" : "Join Platform"}
          </div>
          <h1 className="rl-h1">
            {mode === "login" ? "Sign in to account" : "Create account"}
          </h1>
          <p className="rl-sub">
            {mode === "login"
              ? "Pick up right where your event or committee dashboard left off."
              : "Select your role so requests land in the right team workspace."}
          </p>

          <div className="rl-toggle">
            <button
              type="button"
              className={mode === "login" ? "active" : ""}
              onClick={() => setMode("login")}
            >
              Sign in
            </button>
            <button
              type="button"
              className={mode === "signup" ? "active" : ""}
              onClick={() => setMode("signup")}
            >
              Create account
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            {mode === "signup" && (
              <div className="rl-field">
                <label className="rl-label">Full name</label>
                <div className="rl-input-wrap">
                  <User className="rl-input-icon" size={16} />
                  <input className="rl-input" type="text" placeholder="Sarah Ahmed" required />
                </div>
              </div>
            )}

            <div className="rl-field">
              <label className="rl-label">Email address</label>
              <div className="rl-input-wrap">
                <Mail className="rl-input-icon" size={16} />
                <input className="rl-input" type="email" placeholder="you@resala.org" required />
              </div>
            </div>

            <div className="rl-field">
              <label className="rl-label">Password</label>
              <div className="rl-input-wrap">
                <Lock className="rl-input-icon" size={16} />
                <input className="rl-input" type="password" placeholder="••••••••" required />
              </div>
            </div>

            {mode === "signup" && (
              <>
                <label className="rl-label">I am joining as a</label>
                <div className="rl-role-row">
                  <button
                    type="button"
                    className={`rl-role-btn ${role === "planner" ? "active" : ""}`}
                    onClick={() => setRole("planner")}
                  >
                    <UserCheck size={18} />
                    Event Planner
                  </button>
                  <button
                    type="button"
                    className={`rl-role-btn ${role === "committee_member" ? "active" : ""}`}
                    onClick={() => setRole("committee_member")}
                  >
                    <Users size={18} />
                    Committee Member
                  </button>
                </div>

                {role === "committee_member" && (
                  <div className="rl-field">
                    <label className="rl-label">Select Committee</label>
                    <select
                      className="rl-select"
                      value={committee}
                      onChange={(e) => setCommittee(e.target.value)}
                    >
                      {COMMITTEES.map((c) => (
                        <option key={c} value={c} style={{ background: "#180E2B", color: "#fff" }}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </>
            )}

            <button type="submit" className="rl-submit">
              {mode === "login" ? "Sign in" : "Create account"} <ArrowRight size={18} />
            </button>
          </form>

          {onBackToHome && (
            <button className="rl-back" type="button" onClick={onBackToHome}>
              <ArrowLeft size={14} /> Back to dashboard preview
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
