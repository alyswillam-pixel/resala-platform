# 0008 - Request Escalation to HR as a parallel, Independent Record

 **Date:** 2026-08-17
 **Status:** Accepted

## Context

HR requested that a requester be able to escalate concerns (committee unresponsive,
neglecting the request, deadline risk, misconduct, etc.) to HR at any point in
a Request's lifecycle. Adding this as transcations on the existing Request state
machine would require an escalate/return pair on every current and future state,
and raises the question of what state to return to afterward.

## Decision

Model escalation as a separate `RequestEscalation` record (own lifecycle: Open ->
In Review -> Resolved/Dismissed) referencing a `Request`, rather than as a
transition of the Request's own state machine. Raising an escalation does not pause
or alter the Request's normal progress through its committee workflow; the two
proceed independently and in parallel.

## Consequences

* No changes needed to the existing Request state machine or its transition log
to support escalation.
* A Request can have zero, none, or several escalations attached at different
points in its life, each tracked and resolved by HR independently of the Request's
own state.
* This is the concrete instance of the "parallel regions" pattern discussed as a
possible future statechart extension — implemented here as a second table rather
than a full statechart engine, since only this one case has arisen so far.

