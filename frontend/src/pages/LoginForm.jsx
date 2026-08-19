import { useState } from "react";
import { ArrowLeft, ArrowRight, Lock, Mail, Sparkles } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export default function LoginForm({ onLoginSuccess, onBackToHome }) {
  const [aucEmail, setAucEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auc_email: aucEmail.trim(), password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        if (response.status === 401) {
          throw new Error("Invalid AUC email or password.");
        }

        const fieldErrors = Object.values(data).flat().join(" ");
        throw new Error(fieldErrors || data.detail || "We could not sign you in. Please try again.");
      }

      onLoginSuccess?.({ aucEmail: aucEmail.trim() });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "We could not sign you in. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="rl-root">
      <style>{`
        .rl-root { --ink-bg:#0F172A; --ink-card:rgba(15,23,42,.85); --blue:#2563EB; --blue-dark:#1D4ED8; --gold:#38BDF8; --text:#F8FAFC; --muted:#94A3B8; min-height:100vh; background:var(--ink-bg); color:var(--text); display:flex; flex-direction:column; font-family:var(--font-sans); }
        .rl-nav { padding:32px 7vw; font-size:17px; font-weight:800; display:flex; align-items:center; gap:12px; }
        .rl-mark { width:32px; height:32px; display:grid; place-items:center; border-radius:10px; background:linear-gradient(135deg,var(--blue),var(--blue-dark)); }
        .rl-wrap { flex:1; display:grid; place-items:center; padding:20px 5vw 60px; }
        .rl-card { width:100%; max-width:440px; padding:44px 38px; border:1px solid rgba(248,245,254,.15); border-radius:26px; background:var(--ink-card); box-shadow:0 20px 50px rgba(0,0,0,.5); }
        .rl-eyebrow { color:var(--gold); font-size:11px; letter-spacing:.14em; text-transform:uppercase; display:flex; align-items:center; gap:6px; margin-bottom:12px; }
        .rl-title { margin:0 0 10px; font-size:32px; line-height:1.2; }
        .rl-sub { margin:0 0 30px; color:var(--muted); line-height:1.55; font-size:14px; }
        .rl-field { margin-bottom:20px; }
        .rl-label { display:block; margin-bottom:8px; color:var(--muted); font-size:11px; letter-spacing:.08em; text-transform:uppercase; }
        .rl-input-wrap { position:relative; }
        .rl-icon { position:absolute; left:14px; top:50%; transform:translateY(-50%); color:var(--muted); }
        .rl-input { width:100%; box-sizing:border-box; padding:13px 14px 13px 42px; border-radius:12px; border:1px solid rgba(248,245,254,.16); background:rgba(255,255,255,.05); color:var(--text); font:inherit; }
        .rl-input:focus { outline:none; border-color:var(--blue); box-shadow:0 0 20px rgba(37,99,235,.35); }
        .rl-error { margin:0 0 20px; padding:12px; border:1px solid #f87171; border-radius:12px; background:rgba(248,113,113,.12); color:#fecaca; font-size:13px; }
        .rl-submit { width:100%; border:0; border-radius:999px; padding:15px; color:var(--text); background:linear-gradient(135deg,var(--blue),var(--blue-dark)); font:inherit; font-weight:700; cursor:pointer; display:flex; justify-content:center; align-items:center; gap:8px; }
        .rl-submit:disabled { cursor:wait; opacity:.7; }
        .rl-back { margin-top:24px; border:0; background:none; color:var(--muted); cursor:pointer; display:inline-flex; align-items:center; gap:8px; font:inherit; font-size:13px; }
      `}</style>

      <nav className="rl-nav"><span className="rl-mark">R</span>Resala Platform</nav>
      <main className="rl-wrap">
        <section className="rl-card" aria-labelledby="login-title">
          <div className="rl-eyebrow"><Sparkles size={13} /> Welcome back</div>
          <h1 id="login-title" className="rl-title">Sign in to your account</h1>
          <p className="rl-sub">Use the AUC email and password provided for your Resala Platform account.</p>

          <form onSubmit={handleSubmit}>
            <div className="rl-field">
              <label className="rl-label" htmlFor="auc-email">AUC email address</label>
              <div className="rl-input-wrap">
                <Mail className="rl-icon" size={16} />
                <input id="auc-email" className="rl-input" type="email" autoComplete="username" value={aucEmail} onChange={(event) => setAucEmail(event.target.value)} placeholder="you@aucegypt.edu" required />
              </div>
            </div>
            <div className="rl-field">
              <label className="rl-label" htmlFor="password">Password</label>
              <div className="rl-input-wrap">
                <Lock className="rl-icon" size={16} />
                <input id="password" className="rl-input" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" required />
              </div>
            </div>
            {errorMessage && <p className="rl-error" role="alert">{errorMessage}</p>}
            <button className="rl-submit" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Signing in…" : "Sign in"} <ArrowRight size={18} />
            </button>
          </form>

          {onBackToHome && <button className="rl-back" type="button" onClick={onBackToHome}><ArrowLeft size={14} /> Back to dashboard preview</button>}
        </section>
      </main>
    </div>
  );
}
