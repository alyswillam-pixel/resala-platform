# 0011 - Committe Hierarchy and Role-Based Access via Scoped Django Admin Permissions

 **Date:** 2026-08-18
 **Status:** Accepted

## Context

The Resala Platform needed a way to manage who can create committees, assign
committee leadership, define committee-specific roles, and add members without
building a custom internal-tools UI, which the team has no bandwidth for at this
stage.

The system needed to reflect a real two-level hierarchy:
* The `Presidential Office` is a permenant, singular committee that can create
and, therefore, modify any committee, and assign each committee's Director and
Vice Director.
* Each committee's `Director/Vice Director` can then manage their own committee's
roles ( `CommitteeRole` ) and add/assign members within their own committee only.
* Regular members (Heads and below) need no administrative access at all, for now.

Django's built-in admin permission system ( `is_staff` + `Group` / `Permission` ) is
model-level and instance-blind by default. It can grant "can change CommitteeRole"
globally, but can't natively express "can change CommitteeRole rows belonging to
committee X only". Achieving per-committee scoping required either a custom-build
UI or overriding Django's admin permission hooks ( `has_module_permission` , `has_change_permission` , 
`get_queryset` , `formfield_for_foreignkey` , `save_model` ) per model.

## Decision

Use the Django admin panel itself as the management interface, with `ModelAdmin` 
subclasses for `Committee` , `CommitteeRole` , and `User` that enforce scoping in
Python rather tha through Django's `Group` / `Permission` tables:

* `Committee.is_presidential_office` (boolean, enforced unique via `clean()`)
identifies the Presidential Office committee. Only its `director` / `vice_director` 
(or true Django superuser) can access the `Committee` admin at all.
* Every other committee's `director`/`vice_director` are scoped to their own
committee's `CommitteeRole` and `User` records via `get_queryset` , `has_change_permission` , 
and `formfield_for_foreign key` overrides. The latter restricts dropdown choices
at form level, not just after submission.
* `is_staff` is never set by hand, by anounone (including Presidential Office).
It's derived automatically via a `post_save` / `post_delete` signal on `Committee` 
that recomputes staff status from the current set of `director` / `vice_director` 
FKs across all committees. This closes a self-evaluation path where a Director
coult otherwise grant themselves or someone broader access by editing `User.is_staff` 
directly.
* Regular members (`User.committee_role` set, but not referenced as any committee's
`director` / `vice_director` ) never received `is_staff` , so they have no admin access
at all. This is consistent with "Heads won't have admin access".

## Consequences

### Positive

* No custom frontend UI needed for committee/role/member management. The whole
hierarchy is manageable via `/admin` , which the team already has for free from
the `cookiecutter-django` templates provided.
* Privilege escalation via direct field edits is structurally closed: `is_staff`
is computed, not editable, for non-superusers; the four permission-relevant fields
( `is_staff` , `is_superuser` , `groups` , `user_permissions` ) are stripped from the
`UserAdmin` fieldsets shown to everyone except true superusers, including
Presidential Office.

### Negative

* This is Django-admin-specific logic. If the platform later moves committee/role
management into the custom frontend (Vite/React) instead of the Django admin, none
of this permission logic automatically transfers. It would need to be reimplemented
as DRF permission classes instead.
* A committee with an active `CommitteeRole` set and members still allows the
Presidential Office to delete the parent `Committee` ; `director` / `vice_director` 
are `SET_NULL` on delete but `CommitteeRole` is `CASCADE` , so member's `committe_role` 
silently becomes null. This is a known gap, not yet decided how to address.
* Relies on Djago's admin UI/UX as-is. This is kinda acceptable for an internal
tool users by the small number of committee leads, but not something members should
see later.

## Alternatives Considered

 
* **Django `Group`/`Permission` objects per committee:** rejected — would
  require creating a `Group` per committee per action (e.g. "Tech
  Director", "Tech Member-Manager"), which doesn't scale cleanly and still
  can't express row-level scoping (a "can change CommitteeRole" permission
  is global, not committee-scoped) without the same custom `ModelAdmin` 
  overrides anyway — so it would have added complexity without removing
  the need for custom code.
* **Custom internal frontend view for committee management:** rejected
  for now — meaningful additional frontend work for functionality the
  Django admin already provides once scoped correctly; may be revisited
  if the platform's frontend team wants a more polished internal-tools
  experience later.
* **Django-guardian (object-level permissions package):** considered but
  not adopted — would solve the row-level scoping problem more generically, 
  but adds a new dependency and its own permission-assignment bookkeeping
  for a hierarchy simple enough (two tiers, one FK-based leadership check)
  to express directly in `ModelAdmin` methods without it.
