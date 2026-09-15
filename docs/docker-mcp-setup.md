# Docker MCP companion suite

`scripts/docker_mcp.py` is the portable control point for the workforce and inference servers. It builds both Linux container images, installs local Docker MCP catalog definitions, and maintains the `manufacturing-intelligence` profile.

Run these commands from this repository on Windows, macOS, or Linux:

```text
python scripts/docker_mcp.py setup
python scripts/docker_mcp.py test
python scripts/docker_mcp.py verify
```

`setup` expects the workforce repository at `../michigan-workforce-intelligence`; override it with `WORKFORCE_REPO`. It connects the finished profile to Codex's global MCP configuration by default; set `DOCKER_MCP_CLIENT` to another supported Docker MCP client or `none`. `test` resolves the catalog and checks that both containers start. `verify` connects through the gateway and calls a tool on each server. The gateway command printed by `command` can be registered with any stdio MCP client.

The workforce evidence volume is mounted read-only. The inference project volume is writable only so the explicit `save_project_artifacts` tool can persist approved artifacts. Neither container receives the Docker socket, host filesystem, credentials, or network access.
