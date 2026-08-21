const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

/**
 * Helper to fetch a fresh CSRF token from the backend CSRFTokenView
 * or read from the 'csrftoken' cookie.
 */
export async function getCsrfToken() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/csrf/`, {
      credentials: "include",
    });
    if (res.ok) {
      const data = await res.json();
      if (data.csrfToken) {
        return data.csrfToken;
      }
    }
  } catch (err) {
    console.warn("Could not fetch CSRF token via endpoint:", err);
  }

  // Fallback: parse document.cookie for csrftoken
  if (typeof document !== "undefined" && document.cookie) {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (match) return match[1];
  }

  return "";
}

/**
 * Creates an Event in the backend (POST /api/events/)
 * and attaches a Budget (POST /api/budgets/) if budget amount is provided.
 */
export async function createEventApi({ title, answers, budget }) {
  const csrfToken = await getCsrfToken();
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  if (csrfToken) {
    headers["X-CSRFToken"] = csrfToken;
  }

  // 1. Build Event payload adhering to backend EventSerializer
  const sanitizeEntries = (val) => {
    if (Array.isArray(val)) {
      const filtered = val.map((s) => (typeof s === "string" ? s.trim() : "")).filter(Boolean);
      return filtered.length > 1 ? filtered : (filtered[0] || "");
    }
    return typeof val === "string" ? val.trim() : "";
  };

  const eventPayload = {
    title: title.trim(),
    description: {
      where: sanitizeEntries(answers.where),
      when: sanitizeEntries(answers.when),
      why: sanitizeEntries(answers.why),
      how: sanitizeEntries(answers.how),
      who: sanitizeEntries(answers.who),
    },
  };

  const eventResponse = await fetch(`${API_BASE_URL}/events/`, {
    method: "POST",
    headers,
    credentials: "include",
    body: JSON.stringify(eventPayload),
  });

  if (!eventResponse.ok) {
    let errorDetail = "Failed to create event in the backend.";
    try {
      const errData = await eventResponse.json();
      if (errData.detail) {
        errorDetail = errData.detail;
      } else if (typeof errData === "object") {
        errorDetail = Object.entries(errData)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(" ") : val}`)
          .join(" ");
      }
    } catch {
      // response wasn't JSON
      errorDetail = `Server responded with status ${eventResponse.status}: ${eventResponse.statusText}`;
    }
    throw new Error(errorDetail);
  }

  const createdEvent = await eventResponse.json();

  // 2. If budget is specified, create the associated Budget record
  const numericBudget = parseFloat(budget);
  if (!isNaN(numericBudget) && numericBudget > 0) {
    try {
      const budgetResponse = await fetch(`${API_BASE_URL}/budgets/`, {
        method: "POST",
        headers,
        credentials: "include",
        body: JSON.stringify({
          event: createdEvent.id,
          amount: numericBudget.toFixed(2),
        }),
      });

      if (budgetResponse.ok) {
        const createdBudget = await budgetResponse.json();
        createdEvent.budget = createdBudget;
      } else {
        const budgetError = await budgetResponse.json().catch(() => ({}));
        console.warn("Event was created, but budget allocation failed:", budgetError);
      }
    } catch (budgetErr) {
      console.warn("Network error creating budget for event:", budgetErr);
    }
  }

  return createdEvent;
}

/**
 * Fetches all events from the backend (GET /api/events/)
 */
export async function fetchEventsApi() {
  try {
    const res = await fetch(`${API_BASE_URL}/events/`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      credentials: "include",
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch events: ${res.statusText}`);
    }

    const data = await res.json();
    return Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.warn("Could not fetch events from backend:", err);
    throw err;
  }
}
