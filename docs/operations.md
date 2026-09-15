# Operations

Run `python scripts/docker_mcp.py setup`, then `test`. Start the gateway using the printed command and configure clients to execute it over stdio. Re-run setup after either image changes. Use `docker mcp profile show manufacturing-intelligence` to inspect the profile. Keep `.env` local. Use signed immutable images for distribution and remove the `--verify-signatures=false` development exception.

