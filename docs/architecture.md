# Architecture

An MCP client starts Docker MCP Gateway over stdio. The `manufacturing-intelligence` profile launches separate workforce and inference-advisor images. Workforce evidence stays in its own volume; inference project artifacts stay in the advisor volume. The advisor validates Pydantic inputs, calls deterministic engines, and returns versioned JSON. Only `save_project_artifacts` writes. Network access is blocked for the baseline.

