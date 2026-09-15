# Security model

The runtime is non-root, read-only, capability-free, and network-blocked through the Docker MCP Gateway. It receives only named volumes declared in the local catalog. Store no secrets or controlled technical data in repository examples. Regulated deployments require an approved threat model, identity design, segmentation, logging, patching, firmware provenance, vulnerability response, backup, recovery, and human authorization before procurement or production use.
