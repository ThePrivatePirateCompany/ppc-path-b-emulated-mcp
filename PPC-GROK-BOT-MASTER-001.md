# THE PRIVATE PIRATE COMPANY
## Grok Bot as Connector — Master Document

**Document ID:** PPC-GROK-BOT-MASTER-001  
**Classification:** Internal / Project Control  
**Status Date:** 6 November 2026  
**Owner:** Jeff L. St-Preux, Global Founder and CEO, The Private Pirate Company  
**Request of Record:** PPC-GROK-BOT-P1-REQ-001  

---

## 1. Purpose

This master document consolidates the frozen Phase 0 baseline, the Path B emulated reference MCP, and the current Phase 1 position for the Grok Bot as Connector project. It is the single control document for status, blockers, and next actions. It does not reopen Phase 0 design and does not initiate Phase 2.

---

## 2. Project Scope

Enable a Grok Bot to act as a Custom Connector client against a public HTTPS Model Context Protocol (MCP) server, exercising the frozen tool surface:

| Tool | Function |
|------|----------|
| `create` | Open a work item |
| `assign` | Bind an item to a person or role |
| `status` | Read one item or list all |
| `approve` | Mark an assigned item approved |

Two distinct Grok surfaces exist:

- **Grok chat connectors** — added at grok.com/connectors → New Connector → Custom.
- **Grok Bot plugins** — added inside Grok Bot (Plugins page or in-chat). This is the surface required by the project.

Grok Bot runs in the cloud and can only reach public HTTPS MCP endpoints. Localhost, 127.0.0.1, and RFC 1918 addresses are rejected.

---

## 3. Phase Status

| Phase | Status | Notes |
|-------|--------|-------|
| **Phase 0** | COMPLETE / FROZEN | v0.1 + AUTH-01/02 amendments. No further design changes. |
| **Phase 1** | ACTIVE / BLOCKED on durable URL | Path B reference MCP built and published. Ephemeral tunnel used for smoke test is no longer valid. |
| **Phase 2** | NOT STARTED | Out of scope until Phase 1 checklist is closed. |

---

## 4. Path B — Emulated Reference MCP

### 4.1 Delivered Assets

| Asset | Location |
|-------|----------|
| Source repository | https://github.com/ThePrivatePirateCompany/ppc-path-b-emulated-mcp |
| Server | `server.py` (Python stdlib Streamable HTTP MCP) |
| Documentation | `README.md` |
| Tool surface | create, assign, status, approve |
| Auth mode | Optional bearer via `PPC_MCP_TOKEN` (empty = unauthenticated) |

### 4.2 Protocol Characteristics

- Transport: Streamable HTTP (JSON-RPC over POST `/mcp`)
- Protocol version: 2025-03-26 (echoed from client)
- Capabilities: tools listChanged=false
- CORS: open (reference implementation only)
- Persistence: in-memory (reference only; not production)

### 4.3 Smoke Test History

On 4 September 2026 a temporary Cloudflare quick tunnel was used to verify:

- `/health` returned server identity and tool list
- `initialize` succeeded
- `tools/list` returned the four tools
- `tools/call` create produced item `PPC-0001`

That tunnel URL is no longer reachable. A durable public HTTPS endpoint is required before Phase 1.2–1.4 can be executed against a live Grok Bot.

---

## 5. Phase 1 Checklist (Grok-side)

These steps remain the open work. They cannot be performed from this side of the interface.

| Step | Action | Status |
|------|--------|--------|
| 1.1 | Confirm durable public HTTPS MCP URL ending in `/mcp` | OPEN — durable URL not yet provisioned |
| 1.2 | Add Custom Connector / Plugin in Grok Bot | BLOCKED on 1.1 |
| 1.3 | Bind tools: create → assign → status → approve | BLOCKED on 1.2 |
| 1.4 | Record status and obtain approval | BLOCKED on 1.3 |

### 1.2 Procedure (when URL exists)

1. Open Grok Bot → Plugins (or equivalent in-chat add flow).
2. Add custom MCP server.
3. Name: `PPC Path B`
4. Server URL: `https://<durable-host>/mcp`
5. Authentication: empty unless `PPC_MCP_TOKEN` is set (then `Authorization: Bearer <token>`).
6. Confirm the four tools appear.

---

## 6. Remaining Blocker

**Single remaining blocker:** a durable public HTTPS MCP URL does not yet exist for Path B.

The reference implementation is complete and published. The September 2026 quick tunnel was ephemeral by design. Until a persistent host (named Cloudflare tunnel, reverse proxy, or managed MCP hosting) is stood up and the URL is supplied, Phase 1.2–1.4 remain blocked.

---

## 7. Constraints and Boundaries

- Phase 0 design is frozen. AUTH-01/02 amendments stand.
- Phase 2 is not started.
- No production persistence, multi-tenancy, or external identity provider is in scope for Path B.
- All outputs remain neutral. No association with Canadian provinces, municipalities, religious matters, or identity politics is made.

---

## 8. Next Action

Supply or provision a durable public HTTPS MCP URL for the Path B server. Upon receipt, Phase 1.2 (add Custom Connector in Grok Bot) can be executed and the remaining checklist steps closed.

**Document control:** This master document supersedes ad-hoc status notes for the Grok Bot as Connector project as of 6 November 2026.

---

*Prepared for The Private Pirate Company. Jeff L. St-Preux, Global Founder and CEO.*
