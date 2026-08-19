# 0013 - Secure Account Provisioning via Password Reset Links for Committee-Scoped Users

 **Date:** 2026-08-18
 **Status:** Accepted

## Context

Higher-level platform administrators and committee directors need the ability
to create lower-level member accounts directly within the restricted Django
admin scope.

However, generating or handling temporary plaintext passwords introduces severe
security vulnerabilities (such as credential exposure or insecure transmission
over logs). Furthermore, because database transactions wrap admin requests (
`ATOMIC_REQUESTS = True` ), background workers attempting to fetch newly created
records immediately can encounter race conditions if tasks fire before the
transaction commits.

## Decision

We will implement an automated user provisining workflow in the admin model
layer ( `UserAdmin.save_model` ) where newly created accounts are initialized with
an unusable password ( `obj.set_unusable_password()` ). Upon successful transaction
commit, an asynchronous Celery task is triggered using `transaction.on_commit()` .
This task generates a secure, tokenized password-reset URL using Django-allauth's
native token generator and delivers it via email to the user's official AUC
email.

## Consequences

* **Easier:** Completely removes the need to generate, store, or transmit
  temporary passwords. Leverages Django-allauth's built-in, secure tokenized
  password setup mechanism.
* **Harder:** Requires users to complete the password reset flow to set their
  initial password before logging in.
* **Trade-offs:** Relies on correct transaction boundaries (`transaction.on_commit`)
  to prevent race conditions where Celery workers try to access rows before they
  are committed to the database.

## Alternatives Considered (optional)

1. **Plaintext Temporary Passwords:** Generating a random password and sending
  it via email, (Rejected due to security risks and insecure handling of
  temporary credentials).
2. **Immediate Password Setup on Form:** Requiring creators to input passwords
   manually (Rejected due to credential-sharing risks and poor director UX).
