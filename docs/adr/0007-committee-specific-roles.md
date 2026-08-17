# 0007 - Roles Get Their own Table

 **Date:** 2026-08-17
 **Status:** Accepted

## Context

Roles are actually completely different and nearly unrelated per committee — not
every committee uses the same role names, and there is no shared tier concept to
line them up across committees.

## Decision

We replace the global `Role` choices field on `User` with a `CommitteeRole` model:
each row belongs to a specific `Committee`, has its own `name`, and an optional
`order` for display (later this will be used in creating the hierarchial tree)
within that committee. `User` links via a single `committee_role` FK (nullable, 
since we need to have the ability to remove users but keep them unable to access
committee features; this will be useful when we start creating different committee
portals) instead of separate `role` and `committee` fields. The committee a user
belongs to is derived from `committee_role.committee`.

## Consequences

* No hardcoded role list anywhere in the schema; each committee's roles exist
purely as data, so adding/renaming a committee's role is a data change, not a
code change.
* `User` has one FK instead of two, removing the possibility of a user's `role`
and `committee` fields disagreeing with each other.
* Role-based permission logic (who can do what) must key off `committee_role` (and
by extension its parent `committee`), not a shared role name, since the same role
name in two different committees has no guaranteed relationship.
