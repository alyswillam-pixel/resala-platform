# 0009 - User Identity Uses AUC ID and AUC Email Only

 **Date:** 2026-08-17
 **Status:** Accepted (superseds the generic `email` field assumed in ADR 0002)

## Context

Users authenticate and are identified using AUC-issued credentials, not a personal
email. Every AUC ID maps 1:1 to a specific AUC email — neither can be shared between
users. AUC emails must end in `@aucegypt.edu`. AUC IDs follow the format
`900<YY><NNNN>` (9 digits: literal `900`, 2-digit year issued, 4-digit sequence
number), and the year portion can never be later than the current year.

## Decision

Drop the personal `email` field entirely. `User` has `auc_id` and `auc_email` as
the only email/identifier fields, both unique, both required. `USERNAME_FIELD = "auc_email"`, `REQUIRED_FIELDS = ["auc_id"]`. `User.id` is a UUID primary key
(overriding Django's integer PK).

Validation (AUC email domain, AUC ID format and year) is enforced in `UserManger`'s
`create_user`/`create_superuser` methods.

## Consequences

* Login and all user-facing identification is exclusively AUC-based; no personal
email is stored or used anywhere in the system.
* `createsuperuser` prompts for AUC email then AUC ID (via `REQUIRED_FIELDS`),
and rejects non-AUC-domain emails or malformed AUC IDs at creation time.
* Manager-level validation does not cover every path a `User` could be created
through (e.g. Django admin's add-user form); moving these checks to model-level
`clean()`/field validators was considered and deliberately deferred pending
confirmation of the exact procedures followed later through APIs.
