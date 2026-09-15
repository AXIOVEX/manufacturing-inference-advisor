# Implementation plan

Use Python 3.12, Pydantic and MCP SDK 2 in a non-root multi-stage container. Keep strict schemas in `models.py` and deterministic calculations/policy evaluation in `engine.py`. Keep transport registration in `server.py`. Persist only explicitly requested generated artifacts under `/data/artifacts`; use content hashes. Package the workforce server as a separate stdio image target and create one Docker MCP profile referencing both images. Keep services isolated and block gateway network access for the local catalog-only baseline. Test domain rules directly, test MCP discovery/invocation in-process, then test the image through Docker MCP Gateway.

