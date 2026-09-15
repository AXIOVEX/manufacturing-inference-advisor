# Feature specification: inference infrastructure advisor

## User outcomes

- A plant or engineering team can normalize an AI workload and receive traceable sizing calculations.
- The system compares reuse, dedicated-server, new-platform and hybrid patterns.
- A hardware-neutral specification produces a BOM with unknown fields preserved.
- Restricted sourcing blocks prohibited parts and marks absent origin/firmware/software/supplier evidence unresolved.
- A deployment plan includes acceptance evidence, human gates and rollback.
- Agents reach both this server and Michigan workforce evidence through one Docker MCP profile.

## Functional requirements

- **FR-001** Validate strict project inputs and structured errors.
- **FR-002** Expose formula, inputs, headroom, assumptions, warnings and confidence for sizing.
- **FR-003** Return a classified integration path plus alternatives.
- **FR-004** Generate vendor-neutral hardware and BOM artifacts in JSON and BOM CSV.
- **FR-005** Apply configurable standard, enterprise-restricted, CMMC and ITAR workflow policies.
- **FR-006** Never approve unknown origin when evidence is required; never infer origin from brand.
- **FR-007** Expose nine agent skills and read-only policy/project MCP resources.
- **FR-008** Run as non-root without privilege, host socket, host filesystem or network by default.
- **FR-009** Build and test on Docker Desktop hosts for Windows, Linux and macOS.
- **FR-010** Pin and verify Spec Kit, AEE, Evaluator and application dependencies.

## Boundaries

Outputs are engineering planning aids. They do not certify CMMC, ITAR, export-control, contract sourcing or actual model performance. External pricing/catalog APIs are disabled in the first release.

