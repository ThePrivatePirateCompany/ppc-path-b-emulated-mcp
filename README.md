# PPC Path B — Emulated Reference MCP

Request: `PPC-GROK-BOT-P1-REQ-001`
Phase 0 frozen. Phase 2 not started.

Tools: `create`, `assign`, `status`, `approve`.

```bash
python3 server.py
# http://127.0.0.1:8787/mcp
cloudflared tunnel --url http://127.0.0.1:8787
```

Grok Custom Connector URL must be public HTTPS ending in `/mcp`.
