# Manufacturing Inference Advisor MCP

Manufacturing Inference Advisor helps an AI agent plan private inference infrastructure without pretending that incomplete requirements are procurement facts. It validates workloads, estimates GPU and system capacity, evaluates reuse of current infrastructure, compares architecture patterns, creates hardware-neutral specifications and BOMs, screens sourcing evidence, and produces staged deployment plans.

It is a companion to [Michigan Workforce Intelligence](https://github.com/AXIOVEX/michigan-workforce-intelligence). Docker Desktop is the common runtime, and one Docker MCP Gateway profile can expose both servers to Codex or another MCP client.

## Start here

Requirements:

- Docker Desktop 4.63 or newer with MCP Toolkit.
- Python 3.12 or newer for the portable setup wrapper and Rich TUI.
- The workforce repository at `../michigan-workforce-intelligence`, unless `WORKFORCE_REPO` points elsewhere.

From this repository:

```powershell
python scripts/docker_mcp.py setup
python scripts/docker_mcp.py test
python scripts/docker_mcp.py verify
docker mcp gateway run --profile manufacturing-intelligence --verify-signatures=false --block-network
```

The commands work from PowerShell, Command Prompt, macOS, and Linux shells. Copy `.env.example` to `.env` only when overriding defaults. No API key is required for the baseline server.

`setup` builds `manufacturing-inference-advisor:local` and `michigan-workforce-mcp:local`, installs their local Docker MCP catalog entries, creates or updates the `manufacturing-intelligence` profile, and connects it to Codex by default. Set `DOCKER_MCP_CLIENT=none` to skip the client connection or set it to another supported Docker MCP client.

`verify` makes a live call to each server through the gateway. The gateway deliberately blocks server network access, mounts workforce evidence read-only, and gives the inference server a writable volume only for the explicit artifact-save tool.

## Ask naturally

You do not need to know the MCP tool names. Describe the engineering decision, known constraints, and desired output. The agent should call the tools in the right order and preserve assumptions and evidence.

### Size high-quality engineering and vision AI

> We need private agentic AI for 100 engineers and vision-language assistance for 40 manufacturing machines. Assume a 123B int4 engineering model and a 109B int4 multimodal model, 64K context, 10 peak simultaneous sessions per pool, 30 output tokens per second, 99.9% availability, and 25% growth. Size the GPU memory, GPU count, CPU, RAM, storage, network, power, and cooling. Separate the MCP minimum from production redundancy and identify every benchmark still required.

### Use the current architecture without buying hardware

> Assess whether our current inference endpoints and cloud services can support this workload without adding hardware. Reuse our identity provider, SIEM, network segmentation, storage, monitoring, and existing model gateway where possible. Show capacity and security gaps, required interfaces, changes, risks, and acceptance tests. Do not recommend new hardware unless a measured gap requires it.

### Augment an existing plant

> We have two GPU servers, Entra ID, Splunk, a 25 GbE data network, and an existing Kubernetes cluster. Compare using those systems, adding a separate inference node, and building a dedicated enclave. Recommend the smallest defensible change, including data flows, isolation, failover, rollback, and integration work.

### Design a new protected enclave

> Design a new on-prem inference enclave for controlled engineering data. Include management, inference, data, and client zones; identity; secrets; model storage; observability; backup; recovery; secure boot; TPM; driver and firmware lifecycle; acceptance benchmarks; human approval gates; and rollback. Produce a hardware-neutral specification before creating the BOM.

### Plan an AXIOVEX Sentinel deployment

> Size AXIOVEX Sentinel for 250 engineers and 100 connected manufacturing machines using high-quality local engineering and multimodal models. Show the existing-architecture, augmented, and new-infrastructure paths. Estimate the minimum and production GPU counts, identify which current endpoints can remain, generate a specification-first BOM, apply the ITAR sourcing policy, and create a 90-day deployment and verification plan. Leave price and origin unknown unless evidence is supplied.

### Plan smart routing and a living model catalog

> Design an AXIOVEX-vetted model catalog and routing policy for our engineering and manufacturing workloads. Route each request to the least costly approved model that meets its quality, latency, data-boundary, license, origin, and export-policy threshold. Include caching, batching, context reduction, off-peak scheduling, evaluation gates, rollback, and a method to prove whether a newer model lets the same hardware serve more engineers or machines. Treat the AXIOVEX seal as product assurance, not government certification.

### Estimate NRE, infrastructure, savings, and pilot funding

> Assess our current identity, SIEM, EDR, ticketing, network, storage, Kubernetes, local inference, and cloud endpoints. Use MCP adapters wherever practical. Estimate Sentinel NRE, subscriptions, managed monitoring, local-inference hardware and site costs, customer savings, AXIOVEX gross profit, and a 12-month two-company pilot budget. Compare non-CMMC, CMMC Level 1, Level 2-ready, and CUI/ITAR greenfield starting points. Do not call components CMMC-approved; require supplier, origin, firmware, software, contract, and assessor evidence. Separate customer revenue, grant-funded R&D, and scale capital so the same cost is never funded twice.

### Screen sourcing and provenance

> Screen this BOM for a protected defense deployment. Prohibit PRC-origin and the other countries listed in our approved policy. Require authoritative country-of-origin and assembly evidence, approved supplier evidence, firmware provenance, software and driver supply-chain review, and human approval. Treat unknown origin as a blocker and explain each failed rule.

### Compare costed options

> Compare these three BOMs after I supply current quotes and evidence. Show known total cost, unknown-price lines, unverified-origin lines, vendor concentration, support and lifecycle gaps, and benchmark gaps. Do not select a winner until the evidence is comparable.

### Combine workforce and infrastructure analysis

> Use Michigan Workforce Intelligence to identify the engineering and manufacturing skills demand for a proposed program, then use Manufacturing Inference Advisor to size the private AI infrastructure that would support those users and workflows. Keep workforce evidence, workload assumptions, infrastructure calculations, and recommendations distinct.

## What information produces a useful answer

Provide as much of the following as is known. Missing facts remain explicit gaps.

| Area | Useful inputs |
|---|---|
| Models | Model name or neutral size band, total and active parameters for MoE models, quantization, context length, modality, model license, runtime |
| Demand | Named users, peak simultaneous sessions, machine or camera event rate, requests per second, input/output tokens, batch schedule |
| Performance | Target first-token latency, tokens per second, vision frame or image rate, queue tolerance, task-quality acceptance threshold |
| Availability | Uptime target, recovery time, recovery point, failover strategy, maintenance window |
| Data and compliance | Public/internal/confidential/controlled, FCI/CUI/ITAR scope, permitted users and locations, project policy, retention |
| Current environment | Accelerators and memory, CPU, RAM, storage, network, power, cooling, rack space, identity, SIEM, Kubernetes, backup |
| Growth | Expected user, machine, model, context, and request growth over the planning period |
| Procurement | Approved suppliers, current quotes, country of origin, assembly evidence, firmware and driver provenance, warranty |

Engineer or machine count alone does not determine GPU count. The server's capacity formula estimates model-weight storage, runtime overhead, KV cache for peak sessions, and growth headroom. Throughput still requires a real benchmark because two models with similar parameter counts can perform very differently.

For mixture-of-experts models, record both total and active parameters. Total weights affect storage and memory; active parameters affect per-token compute, but routing, cache architecture, interconnect, quantization, and runtime determine the observed result.

## Recommended workflow

1. **Validate requirements.** Normalize the project and expose missing performance, site, data, and compliance facts.
2. **Analyze the workload.** Produce the transparent GPU-memory and system-capacity envelope with formulas and confidence.
3. **Assess existing infrastructure.** Identify reusable identity, monitoring, storage, and network components and compare declared capacity with the envelope.
4. **Recommend an architecture.** Evaluate current-system integration, a separate server, a new architecture, and hybrid patterns.
5. **Generate a hardware-neutral specification.** Define GPU memory, CPU, RAM, NVMe, network, PCIe, rack, power, cooling, security, runtime, and support requirements.
6. **Generate a specification-first BOM.** Keep manufacturer, part number, price, availability, origin, and compliance unknown until supported.
7. **Screen sourcing evidence.** Apply the configured policy and block unknown or prohibited origin when evidence is required.
8. **Compare costed alternatives.** Use current quotes and equivalent evidence; do not fabricate a ranking.
9. **Create a deployment plan.** Stage site readiness, platform foundation, service integration, verification, release, rollback, and human approvals.
10. **Save approved artifacts.** Persist only non-secret artifacts using an explicit write call.

## MCP tools

| Tool | Purpose | Mutates data |
|---|---|---:|
| `validate_requirements_tool` | Validate and normalize a project; report missing facts and contradictions | No |
| `analyze_inference_project_tool` | Calculate GPU memory and a system-sizing envelope | No |
| `assess_existing_infrastructure_tool` | Compare declared infrastructure with the requirement | No |
| `recommend_architecture_tool` | Compare integration patterns and return a reasoned recommendation | No |
| `generate_hardware_spec_tool` | Create a hardware-neutral compute, storage, network, facility, and security specification | No |
| `generate_bom_tool` | Create JSON or CSV specification-first BOM output | No |
| `screen_bom_for_compliance_tool` | Apply configurable sourcing and evidence gates | No |
| `compare_bom_options_tool` | Compare known cost and evidence completeness | No |
| `generate_deployment_plan_tool` | Build staged deployment, verification, approval, and rollback steps | No |
| `save_project_artifacts` | Save approved non-secret artifacts and return a hash and resource URI | Yes |

Resources:

- `inference://policies/{policy_name}` returns the selected policy definition.
- `inference://projects/{project_id}` returns an explicitly saved project artifact.

Built-in policies are `standard`, `enterprise_restricted`, `cmmc`, and `itar`. They are workflow gates, not legal determinations.

## Project request shape

```json
{
  "project_name": "Protected engineering and vision pilot",
  "industry": "defense_manufacturing",
  "models": [
    {
      "name": "approved-agentic-engineering-123b",
      "parameter_count_b": 123,
      "quantization": "int4",
      "context_length": 65536
    },
    {
      "name": "approved-manufacturing-vision-109b",
      "parameter_count_b": 109,
      "quantization": "int4",
      "context_length": 65536
    }
  ],
  "concurrency": {
    "peak_users": 10,
    "target_first_token_ms": 1200,
    "target_tokens_per_second": 30
  },
  "workloads": ["agentic_engineering", "manufacturing_vision"],
  "availability": {"target": "99.9"},
  "compliance": {
    "cmmc": true,
    "itar": true,
    "export_control": true,
    "policy": "itar"
  },
  "data_sensitivity": "controlled",
  "existing_infrastructure": {},
  "site_constraints": {
    "available_power_kw": 16,
    "cooling_capacity_kw": 16,
    "rack_units": 16
  },
  "growth_factor": 1.25
}
```

The current analyzer applies the project concurrency value to every listed model and sums their memory envelopes. Model pools with different concurrency profiles should be analyzed separately and then combined with the intended routing and availability design.

## Direct Docker MCP calls

List the active profile:

```powershell
docker mcp profile show manufacturing-intelligence
```

Call a tool through the profile:

```powershell
docker mcp tools call validate_requirements_tool "project=<compact-json>" `
  --gateway-arg=--profile=manufacturing-intelligence `
  --gateway-arg=--verify-signatures=false `
  --gateway-arg=--block-network
```

The backtick line continuation is PowerShell-specific. On macOS or Linux, use a backslash or put the command on one line. Prefer an MCP client for normal use so it can serialize structured arguments safely.

## Rich terminal manager

Run:

```powershell
uv run inference-advisor
```

The TUI provides setup, profile validation, live dual-server verification, and gateway-command output. It is a local operator interface; the MCP server remains the automation interface for agents.

## Development and verification

```powershell
docker compose build
docker compose --profile tools run --rm ci
docker compose run --rm mcp
python scripts/docker_mcp.py test
python scripts/docker_mcp.py verify
```

Generate an SBOM and scan the image with an approved scanner:

```powershell
docker sbom manufacturing-inference-advisor:local --format cyclonedx-json
```

The runtime image supports Linux/amd64 and Linux/arm64, runs as a non-root user with a read-only filesystem and dropped capabilities, and does not receive the host Docker socket. Docker Desktop supplies the container runtime on Windows, macOS, and Linux.

## Security, compliance, and evidence boundaries

- CMMC, ITAR, export-control, EU AI, and restricted-source modes enforce workflows and produce evidence. They do not confer certification, determine jurisdiction, authorize an export, or replace legal and assessment professionals.
- Brand headquarters does not establish country of origin. Require authoritative manufacturing, assembly, ownership, firmware, driver, license, and supplier evidence.
- Do not save credentials, controlled technical data, supplier-confidential documents, personal data, or assessment secrets in a public repository or unapproved volume.
- Local development images are unsigned. `--verify-signatures=false` is explicit for this local workflow. Shared production images should be signed and pinned by digest.
- Unknown price, availability, origin, certification, support, compatibility, and performance remain unknown.
- A model or component that appears on an organization-prohibited list fails that configured policy. Screening output is not a legal conclusion.

## Troubleshooting

### Docker MCP profile does not resolve

Run `python scripts/docker_mcp.py setup`, then `python scripts/docker_mcp.py test`. Confirm both local images exist and `docker mcp profile show manufacturing-intelligence` lists both servers.

### Docker Desktop reports a locked `sailor-ingest.sock` on Windows

Close processes that are using the Docker MCP gateway, exit Docker Desktop, and restart Docker Desktop. If the stale socket remains locked, reboot Windows before deleting or renaming anything in Docker's application-data directory. Do not remove active socket files while Docker Desktop is running.

### A tool returns a validation error

The schemas reject unknown fields and invalid policy combinations. `data_sensitivity` belongs at the project root and accepts `public`, `internal`, `confidential`, or `controlled`. An ITAR project must use the `itar` policy or leave the policy unset.

### GPU sizing looks too large

Check whether the project concurrency was applied to every listed model, whether full context is needed for every request, and whether a mixture-of-experts model was treated as dense. Measure per-session KV cache and run each pool separately. The planning heuristic intentionally favors visible headroom over an unsupported performance promise.

## Spec Kit and AEE

The repository uses Spec Kit 1.0.6, Applied Epistemic Engineering engine 1.0.2, and community AEE/Evaluator extensions 1.0.0. Immutable sources and SHA-256 archive digests are recorded in `spec-kit-extensions.lock.json`; `python scripts/verify_extensions.py` validates installed manifests. AEE challenges evidence claims and records uncertainty, but does not prove truth or compliance.

A representative claim set is stored at `evidence/aee-claims.json`. Run the installed adapter with:

```powershell
py -3.12 .specify/extensions/aee/scripts/python/run_aee.py --project-root . assess --input evidence/aee-claims.json --phase after_implement --threshold 0.70 --no-ledger
```

On macOS or Linux, replace `py -3.12` with `python3`. The portability claim is supported by successful Windows, macOS, Linux, and read-only-container jobs in GitHub Actions run 35003632109.

MIT licensed. Third-party model licenses, Spec Kit, AEE, Evaluator, Python packages, container base layers, and data sources retain their own terms.
