from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from inference_advisor.engine import (
    analyze_inference_project,
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


@pytest.fixture
def project() -> dict:
    return {"project_name": "Plant copilot", "industry": "manufacturing", "models": [{"name": "local-70b", "parameter_count_b": 70, "quantization": "int4", "context_length": 32768}], "concurrency": {"peak_users": 10, "target_first_token_ms": 1000, "target_tokens_per_second": 30}, "workloads": ["engineering_document_search"], "availability": {"target": "99.9"}, "compliance": {}, "existing_infrastructure": {}, "site_constraints": {"available_power_kw": 8, "cooling_capacity_kw": 8, "rack_units": 8}}


def test_full_standard_pipeline(project: dict) -> None:
    assert validate_requirements(project)["valid"] is True
    analysis = analyze_inference_project(project)
    assert analysis["sizing_envelope"]["gpu_memory_gb"] > 0
    assert analysis["calculations"][0]["formula"]
    architecture = recommend_architecture(project)
    assert len(architecture["alternatives"]) == 4
    spec = generate_hardware_spec(project)
    assert spec["hardware_neutral"] is True
    bom = generate_bom(project)
    assert bom["specific_products_selected"] is False
    assert "category" in render_bom_csv(bom)
    assert compare_bom_options([bom])["options"][0]["known_cost"] is None
    assert generate_deployment_plan(project)["rollback"]


def test_missing_values_are_explicit(project: dict) -> None:
    del project["concurrency"]["target_first_token_ms"]
    del project["site_constraints"]
    result = validate_requirements(project)
    assert result["valid"] is False
    assert "site_constraints.available_power_kw" in result["missing_requirements"]


def test_restricted_unknown_origin_never_passes(project: dict) -> None:
    bom = generate_bom(project)
    result = screen_bom_for_compliance(bom, {"policy": "itar", "prohibited_countries": ["CN"]})
    assert result["decision"] == "needs_evidence"
    assert result["human_review_required"] is True
    assert result["procurement_authorized"] is False


def test_prohibited_origin_fails(project: dict) -> None:
    bom = generate_bom(project)
    bom["items"][0]["country_of_origin"] = "CN"
    bom["items"][0]["manufacturing_evidence"] = [{"source": "supplier certificate"}]
    result = screen_bom_for_compliance(bom, {"policy": "itar", "prohibited_countries": ["CN"]})
    assert result["decision"] == "fail"
    assert result["line_results"][0]["status"] == "prohibited"


def test_regulated_architecture_and_schema_validation(project: dict) -> None:
    project["compliance"] = {"itar": True}
    project["data_sensitivity"] = "controlled"
    assert recommend_architecture(project)["recommended_pattern"] == "new_architecture"
    project["unexpected"] = True
    with pytest.raises(ValidationError):
        validate_requirements(project)


def test_save_artifacts_is_hashed_and_path_safe(project: dict, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("INFERENCE_DATA_DIR", str(tmp_path))
    result = save_artifacts("plant-copilot", {"requirements": project})
    saved = tmp_path / "artifacts" / "plant-copilot" / "project.json"
    assert saved.is_file() and len(result["sha256"]) == 64
    assert json.loads(saved.read_text())["requirements"]["project_name"] == "Plant copilot"
    with pytest.raises(ValueError):
        save_artifacts("../escape", {})

