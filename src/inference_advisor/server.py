from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from inference_advisor import __version__
from inference_advisor.engine import (
    POLICIES,
    analyze_inference_project,
    assess_existing_infrastructure,
    compare_bom_options,
    generate_bom,
    generate_deployment_plan,
    generate_hardware_spec,
    recommend_architecture,
    render_bom_csv,
    save_artifacts,
    screen_bom_for_compliance,
    validate_requirements,
)

INSTRUCTIONS = """Manufacturing inference infrastructure engineering tools. Gather requirements before sizing; create a hardware-neutral specification before selecting products. Unknown price, availability, origin, certification or performance stays unknown. CMMC/ITAR modes are workflow controls, never certifications, and regulated procurement requires qualified human approval. Preserve traceability across requirements, architecture, hardware specification, BOM, screening and deployment."""


def build_server() -> MCPServer:
    server = MCPServer("Manufacturing Inference Advisor", instructions=INSTRUCTIONS)
    read = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)
    write = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False)

    @server.tool(annotations=read)
    def validate_requirements_tool(project: dict[str, Any]) -> dict[str, Any]:
        """Validate and normalize project requirements; reports gaps and contradictions without inventing values."""
        return validate_requirements(project)

    @server.tool(annotations=read)
    def analyze_inference_project_tool(project: dict[str, Any]) -> dict[str, Any]:
        """Estimate a transparent capacity envelope from the model, context, concurrency and growth inputs."""
        return analyze_inference_project(project)

    @server.tool(annotations=read)
    def assess_existing_infrastructure_tool(project: dict[str, Any], existing_infrastructure: dict[str, Any]) -> dict[str, Any]:
        """Compare declared infrastructure with the planning envelope and identify reuse and gaps."""
        return assess_existing_infrastructure(project, existing_infrastructure)

    @server.tool(annotations=read)
    def recommend_architecture_tool(project: dict[str, Any]) -> dict[str, Any]:
        """Compare integration patterns and return a reasoned classification, alternatives and risks."""
        return recommend_architecture(project)

    @server.tool(annotations=read)
    def generate_hardware_spec_tool(project: dict[str, Any]) -> dict[str, Any]:
        """Generate a vendor-neutral compute, memory, storage, network, power, cooling and security specification."""
        return generate_hardware_spec(project)

    @server.tool(annotations=read)
    def generate_bom_tool(project: dict[str, Any], output_format: str = "json") -> Any:
        """Generate a specification-first BOM; product, price and origin fields remain unknown without evidence."""
        bom = generate_bom(project)
        if output_format == "csv":
            return {"schema_version": bom["schema_version"], "format": "csv", "content": render_bom_csv(bom)}
        if output_format != "json":
            raise ValueError("output_format must be json or csv")
        return bom

    @server.tool(annotations=read)
    def screen_bom_for_compliance_tool(bom: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
        """Apply a configurable sourcing workflow; unknown origin cannot pass a policy requiring evidence."""
        return screen_bom_for_compliance(bom, policy)

    @server.tool(annotations=read)
    def compare_bom_options_tool(boms: list[dict[str, Any]]) -> dict[str, Any]:
        """Compare BOM evidence completeness and known costs without fabricating a winner."""
        return compare_bom_options(boms)

    @server.tool(annotations=read)
    def generate_deployment_plan_tool(project: dict[str, Any]) -> dict[str, Any]:
        """Produce a staged deployment, verification, approval and rollback plan."""
        return generate_deployment_plan(project)

    @server.tool(annotations=write)
    def save_project_artifacts(project_id: str, artifacts: dict[str, Any]) -> dict[str, Any]:
        """Persist generated non-secret project artifacts and return a content hash and resource URI."""
        return save_artifacts(project_id, artifacts)

    @server.resource("inference://policies/{policy_name}")
    def policy_resource(policy_name: str) -> str:
        if policy_name not in POLICIES:
            raise ValueError("unknown policy")
        return json.dumps({"schema_version": "inference-advisor/v1", "name": policy_name, **POLICIES[policy_name]}, indent=2)

    @server.resource("inference://projects/{project_id}")
    def project_resource(project_id: str) -> str:
        if not project_id.replace("-", "").isalnum():
            raise ValueError("invalid project_id")
        path = Path(os.getenv("INFERENCE_DATA_DIR", "/data")) / "artifacts" / project_id / "project.json"
        if not path.is_file():
            raise ValueError("project not found")
        return path.read_text(encoding="utf-8")

    return server


def main() -> None:
    if "--healthcheck" in sys.argv:
        print(json.dumps({"status": "ok", "version": __version__}))
        return
    build_server().run()


if __name__ == "__main__":
    main()

