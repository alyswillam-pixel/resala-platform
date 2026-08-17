# 0010 - Use Django Knox for API Token Authentication

 **Date:** 2026-08-17
 **Status:** Accepted

## Context

Resala requires token-based authentication for its Django REST API. We need a
short-lived credentials with server-side revocation and minimal authentication
infrastructure.

## Decision

Use `Django Knox` for API token authentication with:

```
REST_KNOX = {
    "TOKEN_TTL": timedelta(minutes=15),
    "AUTO_REFRESH: True,
    "MIN_REFRESH_INTERVAL": 60,
}
```

Tokens expire after 15 minutes of inactivity and are automatically refreshed for
active sessions. Knox stores tokens server-side, allowing immediate revocation.

## Consequences

* Reduced exposure window for leaked tokens.
* Immediate token revocation without a separate blocklist.
* Active users remain authenticated without repeated logins.
* Authentication requires server-side token state.

## Alternatives Considered (optional)

* `JWT`: Rejected due to due to additional complexity around token revocation and
refresh management. `JWT` is not designed for that particular approach.

* `Django Session Authentication`: Rejected because Resala exposes a separate REST
API to its frontend.
