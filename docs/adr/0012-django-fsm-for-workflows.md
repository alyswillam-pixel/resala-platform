# 0012 - Use django-fsm for Event and Request Workflows

 **Date:** 2026-08-18
 **Status:** Proposed

## Context

The platform requires predictable, strict state machine logic to handle the lifecycles of Events (e.g., Draft -> Pending Treasurer Review -> Budget Approved) and Requests. We needed a reliable way to enforce these transition rules and prevent invalid state changes without writing complex, manual validation logic from scratch.

## Decision

Use the third-party library `django-fsm` to implement the Finite State Machine pattern. We will replace standard `CharField` state trackers with `FSMField` and use the `@transition` decorator to manage and enforce allowable state changes directly at the model layer.

## Consequences

* Ensures that state transitions strictly follow the rules outlined in our workflows (like the Treasurer/Presidential budget escalations).
* State change logic is completely decoupled from views and APIs, keeping the codebase DRY and the models as the single source of truth.
* Adds a new third-party dependency (`django-fsm`) to the `pyproject.toml` file.
* Requires developers to trigger state changes via the defined transition methods rather than directly mutating the state field.