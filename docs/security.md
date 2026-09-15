# Security model

The runtime is non-root, read-only, capability-free, and network-blocked through the Docker MCP Gateway. It receives only named volumes declared in the local catalog. Store no secrets or controlled technical data in repository examples. Regulated deployments require an approved threat model, identity design, segmentation, logging, patching, firmware provenance, vulnerability response, backup, recovery, and human authorization before procurement or production use.

On September 15, 2026, Docker Scout indexed 168 packages in local runtime image digest `4b0545a8b7f2`. It reported zero critical findings and zero fixable high findings. A separate unfixed scan reported Debian `zlib` advisory CVE-2026-85091 as one high finding with no listed fixed version. It is an upstream residual, remains unsuppressed, and should be rescanned when Debian publishes a patched package or refreshed base image.
