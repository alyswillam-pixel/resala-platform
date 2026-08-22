# 0017 - Replace viewflow.fsm with a Database-Driven Generic Workflow Engine

 **Date:** 2026-08-22
 **Status:** Accepted

## Context

ADR-0014 migrated the Event approval workflow from `django-fsm` to
`viewflow.fsm`, hosting the transition graph and authorization logic inside a
dedicated `EventFlow` class in `events/flows.py`. While this was a meaningful
improvement over embedding state logic directly on the `Event` model, a new
requirement surfaced almost immediately: the platform also needs a workflow for
other future domain objects (e.g. Requests).

Implementing a second `RequestFlow` under the same pattern would mean:

* Duplicating the entire `EventFlow` class structure for every new domain object.
* Encoding the workflow's states, transitions, and authorization rules in Python
  source code — meaning any change to a workflow (adding a state, adjusting who
  can approve) requires a code deployment, not a configuration change.
* Hard-coupling the `viewflow.fsm` library to the core domain models, adding to
  the already-noted risk of pulling in a framework surface far larger than
  what's actually used (ADR-0014 Negative consequences).

The conclusion was that the real problem to solve was not "which FSM library to
use" but "how to make workflows configurable without code changes."

## Decision

Remove `viewflow.fsm` and the event-specific `EventFlow` / `EventState` /
`EventStateTransition` constructs entirely. Replace them with a generic,
database-driven workflow engine composed of the following tables, all in a
dedicated `workflows` Django app:

* **`Workflow`** — a named workflow definition bound to a content type via
  Django's `ContentType` framework, marking it as applicable to a specific
  model (e.g. `Event`). Only one `Workflow` per content type may be `is_active`
  at a time.
* **`WorkflowState`** — a node in the graph. Carries `is_initial` and
  `is_terminal` flags, and an optional `review_committee` FK for display
  purposes.
* **`WorkflowTransition`** — a directed edge between two `WorkflowState` rows
  within the same `Workflow`.
* **`WorkflowTransitionRule`** — encodes who may execute a transition, using a
  `TextChoices`-backed `authorization_type` field (e.g. `REQUESTER`,
  `CAPABILITY`, `COMMITTEE_MEMBER`, `COMMITTEE_LEADER`,
  `PRESIDENTIAL_OFFICE_LEADER`). Multiple rules on the same transition are
  evaluated with OR logic.
* **`WorkflowTransitionAction`** — a controlled side effect executed when a
  transition succeeds (e.g. `SET_BUDGET_STATUS`, `SET_BUDGET_APPROVER`).
  Ordered, and all action types are enumerated by a `TextChoices` class so they
  remain auditable and admin-manageable.
* **`WorkflowInstance`** — links a domain object (via a generic `object_id` /
  `content_type` pair) to a `Workflow` and tracks its `current_state`. One
  instance per object, enforced by a `UniqueConstraint`.
* **`WorkflowTransitionLog`** — an append-only audit record of every state
  change: which transition fired, who fired it, and what the before/after states
  were.

Two runtime components complete the engine:

* **`WorkflowEngine`** — takes a `WorkflowInstance` and provides
  `available_transitions(user)`, `can_execute(transition, user)`, and
  `execute(transition, user, note)`. All state mutation goes through this class.
* **`WorkflowService.start(obj, workflow)`** — creates the initial
  `WorkflowInstance` for a domain object at the workflow's initial state.

The `EventViewSet` API layer is updated to call `WorkflowService.start` on event
creation (if an active workflow exists) and exposes transition execution via a
dedicated `execute_transition` endpoint, with `WorkflowEngine` handling
validation and authorization.

## Consequences

### Positive

* **Zero-code workflow changes:** States, transitions, rules, and actions are
  rows in the database, manageable through the Django admin. A PO leader can
  add a new approval state or adjust who can approve without a deployment.
* **True generality:** The same engine handles workflows for any model. Adding
  a `Request` workflow requires no new Python beyond registering the model in
  the admin and configuring it through the UI.
* **Auditable by default:** `WorkflowTransitionLog` records every state change
  with actor, timestamp, and an optional note — a capability previously
  provided by `EventStateTransition` but now generic across all models.
* **Removes the viewflow dependency entirely:** Eliminates the risk of carrying
  an oversized, partially-used framework dependency as the codebase grows
  (ADR-0014 Negative).

### Negative

* **Loss of code-level visibility:** Workflow structure is no longer readable
  from source code. A developer cannot understand the current event approval
  workflow without either querying the database or reading admin screenshots.
  This is a real discoverability cost.
* **Initial data dependency:** Tests and local development must seed a valid
  `Workflow` + `WorkflowState` + `WorkflowTransition` graph into the database
  before the approval flow can run. The `factories.py` module partially
  addresses this, but integration tests now have more setup overhead than the
  old `EventFlow` unit tests did.
* **Action types are still code-enumerated:** `WorkflowTransitionAction` types
  (e.g. `SET_BUDGET_STATUS`) are Python `TextChoices`, not free-text. Adding
  a genuinely new action type still requires a code change and deployment.
  This is a conscious boundary: arbitrary side effects cannot be configured by
  an admin without custom code to back them.

## Alternatives Considered

* **Keep `viewflow.fsm`, duplicate `EventFlow` per domain object:** rejected —
  this is precisely the scaling problem that prompted this ADR. Each new domain
  object doubles the boilerplate and couples a new workflow permanently to a
  deployment.
* **Use a third-party workflow/BPM library (e.g. SpiffWorkflow, django-viewflow's
  full BPMN engine):** rejected — the platform's workflow requirements are
  well-defined and relatively narrow (linear approval chains with branching
  authorization). A BPMN engine would import a large dependency surface and
  introduce a new modelling language without proportionate benefit at this stage.
* **Store the workflow graph as JSON on the `Workflow` model:** considered as
  a schema-lighter alternative. Rejected because normalized relational rows give
  full `ForeignKey` integrity (you cannot reference a non-existent state in a
  transition), query-ability, and admin-level editing with standard Django tooling
  — none of which JSON blobs provide.
