import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

function mockAuthPlugin() {
  const inMemoryEvents = [
    {
      id: "01915f01-7b89-7000-8000-000000000001",
      title: "Children's Day Festival 2026",
      description: {
        where: "Nasr City Youth Center",
        when: "Oct 24, 2026 · 10:00 AM",
        why: "Annual fun fair for 300+ children with interactive workshops and live entertainment.",
        how: "Volunteer squads managing registration, stage, gifts and games.",
        who: "Children and families from community centers."
      },
      current_state: "Budget Approved",
      budget: { amount: "45000.00", status: "Approved" },
      created_at: "2026-08-20",
      updated_at: "2026-08-21"
    },
    {
      id: "01915f01-7b89-7000-8000-000000000002",
      title: "Blood Drive Marathon",
      description: {
        where: "Cairo University Main Campus",
        when: "Nov 05, 2026 · 09:00 AM",
        why: "Collaborative campus blood drive targeting 500+ blood donations.",
        how: "Mobile blood bank buses with medical team support and partner sponsors.",
        who: "University students and faculty donors."
      },
      current_state: "Pending Treasurer Review",
      budget: { amount: "28000.00", status: "Pending" },
      created_at: "2026-08-20",
      updated_at: "2026-08-21"
    },
    {
      id: "01915f01-7b89-7000-8000-000000000003",
      title: "Ramadan Food Packs Distribution",
      description: {
        where: "Resala Central Warehouse, Giza",
        when: "Mar 10, 2026 · 08:00 AM",
        why: "Packing & distributing 5,000+ essential Ramadan dry food boxes.",
        how: "Assembly line packing and fleet distribution to governorate hubs.",
        who: "Families in need across governorates."
      },
      current_state: "Active",
      budget: { amount: "150000.00", status: "Approved" },
      created_at: "2026-08-19",
      updated_at: "2026-08-21"
    }
  ];

  return {
    name: "mock-api-backend",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // CSRF Token endpoint
        if (req.url === "/api/auth/csrf/" && req.method === "GET") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ csrfToken: "dev-csrf-token-resala-2026" }));
          return;
        }

        // Auth Login endpoint
        if (req.url === "/api/auth/login/" && req.method === "POST") {
          let body = "";
          req.on("data", (chunk) => {
            body += chunk;
          });
          req.on("end", () => {
            try {
              const data = JSON.parse(body || "{}");
              if (data.auc_email && data.password) {
                res.writeHead(200, { "Content-Type": "application/json" });
                res.end(
                  JSON.stringify({
                    token: "mock-knox-token-key-auc-2026",
                    user: {
                      auc_email: data.auc_email,
                      role: "planner",
                    },
                  })
                );
                return;
              }
            } catch {
              // Ignore json parse error
            }
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ detail: "Invalid email or password" }));
          });
          return;
        }

        // Events List (GET /api/events/)
        if ((req.url === "/api/events" || req.url === "/api/events/") && req.method === "GET") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify(inMemoryEvents));
          return;
        }

        // Events Create (POST /api/events/)
        if ((req.url === "/api/events" || req.url === "/api/events/") && req.method === "POST") {
          let body = "";
          req.on("data", (chunk) => {
            body += chunk;
          });
          req.on("end", () => {
            try {
              const data = JSON.parse(body || "{}");
              if (!data.title || !data.title.trim()) {
                res.writeHead(400, { "Content-Type": "application/json" });
                res.end(JSON.stringify({ title: ["This field is required."] }));
                return;
              }

              const newEvent = {
                id: "01915f01-" + Math.random().toString(16).substring(2, 10) + "-7000-8000-" + Date.now().toString(16).slice(-12),
                title: data.title,
                description: data.description || {},
                requester: "01915f00-user-7000-8000-000000000001",
                current_state: "Draft",
                budget: null,
                created_at: new Date().toISOString().split("T")[0],
                updated_at: new Date().toISOString().split("T")[0],
              };
              inMemoryEvents.unshift(newEvent);

              res.writeHead(201, { "Content-Type": "application/json" });
              res.end(JSON.stringify(newEvent));
              return;
            } catch {
              res.writeHead(400, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ detail: "Invalid JSON body" }));
            }
          });
          return;
        }

        // Budgets Create (POST /api/budgets/)
        if ((req.url === "/api/budgets" || req.url === "/api/budgets/") && req.method === "POST") {
          let body = "";
          req.on("data", (chunk) => {
            body += chunk;
          });
          req.on("end", () => {
            try {
              const data = JSON.parse(body || "{}");
              const matchingEvent = inMemoryEvents.find((e) => e.id === data.event);
              const budgetObj = {
                id: "01915b01-" + Math.random().toString(16).substring(2, 10),
                event: data.event,
                amount: data.amount ? parseFloat(data.amount).toFixed(2) : "0.00",
                status: "Pending",
                approved_by: null,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
              };

              if (matchingEvent) {
                matchingEvent.budget = budgetObj;
              }

              res.writeHead(201, { "Content-Type": "application/json" });
              res.end(JSON.stringify(budgetObj));
              return;
            } catch {
              res.writeHead(400, { "Content-Type": "application/json" });
              res.end(JSON.stringify({ detail: "Invalid JSON body for budget" }));
            }
          });
          return;
        }

        next();
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), mockAuthPlugin()],
  server: {
    host: "0.0.0.0",
    port: 3000,
  },
  build: {
    outDir: "../dist",
    emptyOutDir: true,
  },
});
