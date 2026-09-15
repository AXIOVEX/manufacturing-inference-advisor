# Troubleshooting

If Docker reports its named pipe or socket is inaccessible, restart Docker Desktop and verify `docker version` shows a server. If the profile is absent, rerun setup. If image launch fails, run each image health check and inspect `docker mcp gateway run ... --verbose`. If tools are missing, rebuild both images and re-add them to the profile. A dry-run validates resolution but full MCP discovery/invocation is the acceptance test.

