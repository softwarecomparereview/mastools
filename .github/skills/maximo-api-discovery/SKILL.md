---
name: maximo-api-discovery
description: >
  Discover, validate, and query IBM Maximo / MAS Manage REST-OSLC object
  structures (/maximo/api/os/...). Use whenever generating Maximo API URLs,
  integration code against MXAPI* object structures, or diagnosing 401/403/404
  failures from the Maximo REST API. Prevents guessing object structure names
  from MXINTOBJECT.
---

# Maximo REST API — Object Structure Discovery & Troubleshooting

## The core rule

**Never generate `/maximo/api/os/<name>` URLs from the MXINTOBJECT table or
from memory.** MXINTOBJECT lists *every* object structure, but the REST/OSLC
layer only serves a subset, and each one is additionally gated by security.
The only authoritative source of callable resource names is the server's own
service document:

```
GET https://<host>/maximo/api/os?lean=1
Header: apikey: <key>
```

The JSON response enumerates exactly the resources this environment exposes.
A name absent from that list will 404 no matter what. Always fetch this first
and generate URLs only from names it returns.

## If you must query MXINTOBJECT directly

Only rows consumed by integration are ever published to the API. Filter:

```sql
SELECT intobjectname, description, authapp
FROM   mxintobject
WHERE  usewith = 'INTEGRATION'
ORDER  BY intobjectname;
```

- `usewith` (shown as **Consumed By** in the Object Structures app) values of
  `MIGRATION`, `REPORTING`, or `MOBILE` mean the OS is NOT a REST resource.
  Example: `DMPERSON` is a migration object structure — use `MXAPIPERSON`
  for the API instead. Treat any `DM*` prefix as not-API-callable.
- `authapp` is the **Authorized Application** — the app the calling user's
  security group must have access to (see error triage below).
- The `MXAPI*` family differs between Maximo 7.6.1.x versions and MAS Manage
  releases. Do not assume a name exists (e.g. verify `MXAPIVENDORMSTR` /
  `MXAPIROUTES` before using them); confirm against the service document.

## Authentication

| Route | Auth |
|---|---|
| `/maximo/api/...` | `apikey` header (preferred) or `&apikey=` query param. MAS Manage: API keys are created in Administration → API keys. |
| `/maximo/oslc/...` | Session/basic auth (`maxauth` header, base64 `user:pass`) on older on-prem with app-server security off; LDAP/SAML setups must use `/api` + apikey. |

An API key inherits the permissions of the user it was created for. A key
minted from a low-privilege user will 403 on most `MXAPI*` resources even
though the key itself is valid.

## Error triage — read the status code and message key first

| Symptom | Meaning | Fix |
|---|---|---|
| `404` / `BMXAA8727E` (resource not found) | OS name wrong, not in this version, or Consumed By ≠ INTEGRATION | Pick the name from `GET /api/os?lean=1`; for `DM*` names switch to the `MXAPI*` equivalent |
| `403` / `BMXAA9051E` (not authorized) | User's security group lacks the OS's Authorized Application (e.g. MXAPIASSET→Assets, MXAPICOA→Chart of Accounts, MXAPIVENDOR*→Company Master) or explicit object structure grant | Security Groups → grant the app, or grant READ under the group's Object Structures section |
| `401` / `BMXAA0021E` | Missing/invalid apikey or credentials | Send `apikey` header on the `/api` route |
| `200` but body is HTML (login page) | Request never authenticated; server redirected to the login form | Same as 401 — this is not a query-syntax problem |
| `400` / `BMXAA9310E` | Bad query parameter (misspelled `oslc.*` param or invalid `oslc.where` clause) | Check parameter reference below |

Org-level financial apps (Chart of Accounts, Company Master) are the most
common 403s — many integration users were never granted them.

## Validating a resource before generating bulk code

Smoke-test with the cheapest possible call and escalate only on success:

```
GET /maximo/api/os/MXAPIASSET?lean=1&oslc.pageSize=1
```

- 200 with JSON `member` array → resource is good; proceed.
- Anything else → triage with the table above before writing more URLs.

## Query parameter reference (correct as query-string syntax)

| Param | Purpose | Example |
|---|---|---|
| `lean=1` | Drop RDF namespaces from JSON (use it everywhere) | `lean=1` |
| `oslc.pageSize` | Page size | `oslc.pageSize=100` |
| `pageno` | Page number (with pageSize) | `pageno=2` |
| `oslc.select` | Attribute projection; `*` for all, dot into child objects | `oslc.select=assetnum,description,assetspec{*}` |
| `oslc.where` | Filter; quote strings, `%22` if URL-encoding | `oslc.where=status="OPERATING" and siteid="BEDFORD"` |
| `oslc.orderBy` | Sort, `+`/`-` prefix | `oslc.orderBy=-changedate` |
| `searchAttributes` + `oslc.searchTerms` | Wildcard text search | `searchAttributes=description&oslc.searchTerms="pump"` |
| `collectioncount=1` | Include total count in response | `collectioncount=1` |
| `_dropnulls=0` | Return null attributes too | `_dropnulls=0` |

Common well-known integration object structures (verify against the service
document — availability varies by release): `MXAPIASSET`, `MXAPIITEM`,
`MXAPIPERSON`, `MXAPIPERUSER`, `MXAPIWODETAIL`, `MXAPISR`, `MXAPIPM`,
`MXAPIJOBPLAN`, `MXAPIOPERLOC`, `MXAPIINVENTORY`, `MXAPIPO`, `MXAPIPR`,
`MXAPIVENDOR`, `MXAPISERVITEM`, `MXAPICOA`, `MXAPIDOMAIN`, `MXAPIMETER`,
`MXAPILOCATIONS`, `MXAPIWOACTIVITY`.

## Workflow summary

1. `GET /api/os?lean=1` with the apikey → list of real resource names.
2. Cross-check any name you intend to use against that list (never MXINTOBJECT
   alone; if using MXINTOBJECT, filter `usewith = 'INTEGRATION'`).
3. Smoke-test each resource with `oslc.pageSize=1`.
4. On failure, classify via the error-triage table — report the status code,
   BMXAA message key, and the specific fix (name / security grant / auth),
   not just "the call failed".
5. Only then generate bulk queries or integration code.
