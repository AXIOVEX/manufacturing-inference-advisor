from __future__ import annotations

import pytest

from inference_advisor.server import build_server


@pytest.mark.anyio
async def test_mcp_contract_exposes_tools_and_resources() -> None:
    server = build_server()
    names = {tool.name for tool in await server.list_tools()}
    assert names == {"validate_requirements_tool", "analyze_inference_project_tool", "assess_existing_infrastructure_tool", "recommend_architecture_tool", "generate_hardware_spec_tool", "generate_bom_tool", "screen_bom_for_compliance_tool", "compare_bom_options_tool", "generate_deployment_plan_tool", "save_project_artifacts"}
    templates = await server.list_resource_templates()
    uris = {str(item.uri_template) for item in templates}
    assert "inference://policies/{policy_name}" in uris
    assert "inference://projects/{project_id}" in uris

