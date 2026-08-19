# Conventional Commits Cheatsheet

A quick reference for writing clear, consistent Git commit messages.

---

## Commit Message Structure

### General Format

```text
<type>([optional scope])[optional !]: <description>

[optional body]

[optional footer]
```

### Examples

**Initial commit**

```text
chore: init
```

**Feature**

```text
feat(users): implement password reset flow
```

**Breaking change**

```text
feat(api)!: remove legacy authentication endpoint
```

**Merge commit**

```text
Merge branch '<branch-name>'
```

**Revert commit**

```text
Revert "feat(users): implement password reset flow"
```

---

## 1. Types

The **type** describes the nature of the change.

### API & UI Changes

| Type   | Description                                       |
| ------ | ------------------------------------------------- |
| `feat` | Add, modify, or remove a feature in the API or UI |
| `fix`  | Fix a bug introduced by a previous `feat` commit  |

### Other Changes

| Type       | Description                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------- |
| `refactor` | Restructure code without changing API or UI behavior                                           |
| `perf`     | Improve performance without changing functionality                                             |
| `style`    | Make code-style changes that do not affect application behavior                                |
| `test`     | Add, modify, or correct tests                                                                  |
| `docs`     | Change documentation only                                                                      |
| `build`    | Change build tools, dependencies, project version, or related configuration                    |
| `ops`      | Change operational infrastructure such as CI/CD, deployment, monitoring, backups, or recovery  |
| `chore`    | Perform repository maintenance tasks such as updating `.gitignore` or initializing the project |

> **Note:** Use the most specific type that accurately describes the change.

---

## 2. Scopes

The **scope** provides additional context about the area affected by the commit.

* The scope is **optional**.
* Scopes should describe a project component, module, or domain.
* Allowed scopes are project-specific.
* **Do not use issue identifiers as scopes.**

### Examples

```text
feat(users): add password reset flow
fix(auth): handle expired tokens
refactor(committee): simplify role validation
```

---

## 3. Breaking Changes

A commit that introduces a **breaking change** must include `!` immediately before the colon.

```text
feat(api)!: remove legacy authentication endpoint
```

Breaking changes should also be documented in the commit footer when the subject or body does not provide enough information.

```text
feat(api)!: remove legacy authentication endpoint

BREAKING CHANGE: clients must migrate to the new authentication endpoint
```

---

## 4. Description

The **description** is a concise summary of the change.

### Rules

* The description is **mandatory**.
* Use the **imperative, present tense**.

  * ✅ `add password reset flow`
  * ❌ `added password reset flow`
  * ❌ `adds password reset flow`
* Do **not** capitalize the first letter.
* Do **not** end the description with a period.

### Good Examples

```text
feat(users): implement password reset flow
fix(auth): reject expired reset tokens
chore(repo): update gitignore
```

---

## 5. Body

The **body** is optional and should explain the motivation behind the change.

Use it when the commit requires additional context, particularly when explaining:

* why the change was necessary
* what behavior changed
* what the previous behavior was
* important implementation decisions

The body should also use the **imperative, present tense**.

### Example

```text
feat(users): implement token-based password reset flow

Replace plaintext password emails with secure reset links
generated using Django's default token generator.

Invalidate all existing sessions after a successful password
reset to prevent previously issued credentials from remaining
usable.
```

---

## 6. Footer

The **footer** is optional unless the commit introduces a breaking change.

It can be used for:

* issue references
* breaking-change explanations
* other commit metadata

### Issue References

```text
Closes #123
```

or

```text
Fixes JIRA-456
```

### Breaking Changes

Breaking changes must begin with:

```text
BREAKING CHANGE:
```

For a single-line description:

```text
BREAKING CHANGE: remove the legacy authentication endpoint
```

For a multi-line description:

```text
BREAKING CHANGE:

The legacy authentication endpoint is removed.
Clients must migrate to the new authentication flow.
```

---

## 7. Semantic Versioning

Commit types determine the version increment for the next release.

| Commit          | Version Impact |
| --------------- | -------------- |
| Breaking change | **MAJOR**      |
| `feat` or `fix` | **MINOR**      |
| Everything else | **PATCH**      |

### Example

Given the following commits:

```text
feat(users): add password reset flow
fix(auth): reject expired tokens
chore(repo): update gitignore
```

The release receives a **minor** version bump because it contains API-relevant changes.

If a breaking change is included:

```text
feat(api)!: remove legacy authentication
```

the release receives a **major** version bump.

---

## Quick Reference

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Common Types

```text
feat      → new or changed API/UI functionality
fix       → bug fix
refactor  → code restructuring
perf      → performance improvement
style     → non-functional style changes
test      → tests
docs      → documentation
build     → build/dependency changes
ops       → operational/infrastructure changes
chore     → repository maintenance
```

### Before Committing

* [ ] Choose the most appropriate commit type
* [ ] Add a scope when it provides useful context
* [ ] Write the description in imperative, present tense
* [ ] Keep the description lowercase
* [ ] Do not end the description with a period
* [ ] Add a body when additional context is useful
* [ ] Mark breaking changes with `!`
* [ ] Add `BREAKING CHANGE:` to the footer when required
* [ ] Reference related issues when appropriate

---

> Adapted from the [Conventional Commits Cheatsheet by qoomon](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13).
