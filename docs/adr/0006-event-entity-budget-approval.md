# 0006 - Introduce Event Entity with Treasurer/Presidential Budget Approval

 **Date:** 2026-08-17
 **Status:** Accepted

## Context

Events have their own budget, which must be approved before committee-level work
(Requests) can begin. Budget approval always starts with the treasurer, who may
either approve/reject directly or escalate to the presidential office for a final
decision — a sequential escalation.

## Decision

Introduce a top-level `Event` entity with its own state machine (Draft -> Pending
Treasurer Review -> [Budget Approved | Pending Presidential Review] -> Budget
Approved/Rejected -> Active -> Done), independent of and parent to the existing
`Request` state machine. `Budget` moves from belonging to `Request` to belonging
to `Event` (one-to-one). `Request` gains an `event` FK. A rejected budget can
either be revised and resubmitted (back to Draft) or marked `Turned Down` as its
own separate terminal state (non-negotiable, no further revision).

## Consequences

* `Event` and `Request` are two independent, peer state machines connected by a
trigger (Event reaching Budget Approved unlocks Request creation) and a parent-
child FK.
* Each escalation step (treasurer approves/rejects/escalates, presidential office
approves/rejects) is logged via the same append-only `EventStateTransition` pattern
used for `Request` , so the full approval history is always reconstructable.
* `Turned Down` is kept as its own distinct terminal state so a dashboard query
can distinguish successfully completed events from non-negotiably rejected one
without reading the transition log.
