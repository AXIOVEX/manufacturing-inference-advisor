# Manufacturing Inference Advisor MCP

This companion to [Michigan Workforce Intelligence](../michigan-workforce-intelligence) gives agents a vendor-neutral way to size on-site AI inference, compare integration patterns, build specification-first BOMs, screen sourcing evidence and produce deployment plans. Docker Desktop is the single runtime: one profile exposes both independent MCP servers through the Docker MCP Gateway.

## One-stop Docker setup

Requirements: Docker Desktop 4.63+ with MCP Toolkit and Python 3.12+ only for the portable setup wrapper. Copy `.env.example` to `.env` if overriding defaults; no API key is required.

```powershell
python scripts/docker_mcp.py setup
python scripts/docker_mcp.py test
python scripts/docker_mcp.py verify
docker mcp gateway run --profile manufacturing-intelligence --verify-signatures=false --block-network
```

For the Rich interactive manager, run `uv run inference-advisor` and choose setup, profile validation, live dual-server verification, or gateway-command output.

The same commands work in PowerShell, Command Prompt, macOS and Linux shells. The script builds `manufacturing-inference-advisor:local`, builds the workforce repository's `mcp-stdio` target as `michigan-workforce-mcp:local`, creates or updates the `manufacturing-intelligence` profile, and connects the profile to Codex. Set `DOCKER_MCP_CLIENT` to another supported Docker MCP client or `none`. `verify` makes a live tool call to each server through the gateway. Configure any additional MCP client to run the final command over stdio. Local images are unsigned, so the explicit development flag disables signature verification; publish signed digest-pinned images before shared production use. See [Docker MCP setup](docs/docker-mcp-setup.md).

For direct development:

```text
docker compose build
docker compose --profile tools run --rm ci
docker compose run --rm mcp
```

## Agent workflow and tools

Use the skills in this order when the full workflow applies: inference requirements, existing-infrastructure integration, architecture selection, hardware sizing, BOM generation, restricted sourcing, compliance review, deployment planning and verification.

The MCP exposes ten tools: requirements validation and analysis; infrastructure assessment; architecture recommendation; hardware specification; JSON/CSV BOM generation; BOM compliance screening; BOM comparison; deployment planning; and explicit artifact persistence. Resources expose policies and saved projects under `inference://...` URIs.

Example questions:

- “Validate this 70B-model plant copilot workload and list the missing power, cooling and throughput facts.”
- “Compare reusing our two existing GPU servers with adding a dedicated inference node.”
- “Create a hardware-neutral specification and BOM, leaving unverified products and prices unknown.”
- “Screen this BOM using our ITAR sourcing policy and block every line missing authoritative origin or firmware evidence.”
- “Create a staged rollout with identity, network segmentation, observability, acceptance testing and rollback.”
- “Use workforce evidence to identify a manufacturing skills need, then use the inference advisor to size the private agent infrastructure that would support the program.”

## Safety and evidence boundary

This server provides engineering planning, not performance guarantees or legal certification. CMMC, ITAR and export-control modes enforce workflow gates. A qualified reviewer must supply the applicable contract policy and approve regulated procurement. Brand headquarters does not establish country of origin. Missing prices, availability, origin, firmware, driver provenance and certifications remain unknown.

The baseline is catalog-only and the gateway command blocks network access. Generated project artifacts are saved only through the explicit write tool. Do not store credentials, controlled technical data, supplier-confidential documents or personal data in a public repository or unapproved volume.

## Spec Kit and AEE

The repository uses Spec Kit 1.0.6, Applied Epistemic Engineering engine 1.0.2, and community AEE/Evaluator extensions 1.0.0. Immutable sources and SHA-256 archive digests are recorded in `spec-kit-extensions.lock.json`; `python scripts/verify_extensions.py` validates installed manifests. AEE challenges evidence claims and records uncertainty, but does not prove truth or compliance.

A representative claim set is stored at `evidence/aee-claims.json`. Run the installed adapter with `py -3.12 .specify/extensions/aee/scripts/python/run_aee.py --project-root . assess --input evidence/aee-claims.json --phase after_implement --threshold 0.70 --no-ledger` on Windows, or replace `py -3.12` with `python3` on macOS/Linux. The portability claim is supported by the successful Windows, macOS, Linux, and read-only-container jobs in GitHub Actions run 35003632109.

## Portability, tests and artifacts

The runtime image is Linux/amd64 or Linux/arm64 and runs non-root with a read-only filesystem, dropped capabilities and no host Docker socket. Docker Desktop supplies that container runtime on Windows, macOS and Linux. Run `docker compose --profile tools run --rm ci`; generate an SBOM with `docker sbom manufacturing-inference-advisor:local --format cyclonedx-json` and scan with your approved scanner.

MIT licensed. Third-party Spec Kit, AEE, Evaluator, Python packages and container base layers retain their respective licenses.
