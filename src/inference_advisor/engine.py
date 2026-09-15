from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from inference_advisor.models import Component, ProjectRequest, SourcingPolicy

SCHEMA = "inference-advisor/v1"
BYTES_PER_PARAMETER = {"fp32": 4.0, "fp16": 2.0, "bf16": 2.0, "int8": 1.0, "int4": 0.5}
POLICIES: dict[str, dict[str, Any]] = {
    "standard": {"require_human_approval": False},
    "enterprise_restricted": {"require_country_of_origin_evidence": True, "require_firmware_review": True, "require_supplier_review": True, "require_human_approval": True},
    "cmmc": {"require_country_of_origin_evidence": True, "require_firmware_review": True, "require_supplier_review": True, "require_software_supply_chain_review": True, "require_human_approval": True},
    "itar": {"require_country_of_origin_evidence": True, "require_firmware_review": True, "require_supplier_review": True, "require_software_supply_chain_review": True, "require_data_flow_review": True, "require_human_approval": True},
}


def _base() -> dict[str, Any]:
    return {"schema_version": SCHEMA, "generated_at": datetime.now(UTC).isoformat()}


def _project(payload: dict[str, Any]) -> ProjectRequest:
    return ProjectRequest.model_validate(payload)


def validate_requirements(payload: dict[str, Any]) -> dict[str, Any]:
    project = _project(payload)
    warnings: list[str] = []
    missing: list[str] = []
    if project.concurrency.target_tokens_per_second is None:
        missing.append("concurrency.target_tokens_per_second")
    if project.concurrency.target_first_token_ms is None:
        missing.append("concurrency.target_first_token_ms")
    if not project.site_constraints:
        missing.extend(["site_constraints.available_power_kw", "site_constraints.cooling_capacity_kw", "site_constraints.rack_units"])
    if project.compliance.itar or project.compliance.cmmc:
        warnings.append("Regulated mode is a workflow control, not a legal certification; qualified human review is required.")
    if project.concurrency.target_first_token_ms and project.concurrency.target_first_token_ms < 100:
        warnings.append("Sub-100 ms first-token targets require workload-specific benchmark evidence.")
    return {**_base(), "valid": not missing, "missing_requirements": missing, "contradictions": [], "warnings": warnings, "normalized": project.model_dump(mode="json")}


def analyze_inference_project(payload: dict[str, Any]) -> dict[str, Any]:
    project = _project(payload)
    calculations: list[dict[str, Any]] = []
    total = 0.0
    heuristic = False
    for model in project.models:
        weights = model.parameter_count_b * BYTES_PER_PARAMETER[model.quantization]
        if model.kv_cache_gb_per_session is None:
            kv_each = model.parameter_count_b * model.context_length / 1_000_000 * 0.8
            heuristic = True
        else:
            kv_each = model.kv_cache_gb_per_session
        raw = (weights * 1.20 + kv_each * project.concurrency.peak_users) * project.growth_factor
        total += raw
        calculations.append({"metric": "gpu_memory_required_gb", "model": model.name, "value": round(raw, 2), "formula": "(parameter_storage*1.20 + kv_cache_per_session*peak_users)*growth_factor", "inputs": {"weights_gb": weights, "kv_cache_gb_per_session": kv_each, "peak_users": project.concurrency.peak_users, "growth_factor": project.growth_factor}, "confidence": "low" if model.kv_cache_gb_per_session is None else "medium"})
    validation = validate_requirements(payload)
    return {**_base(), "project_name": project.project_name, "normalized_workload": project.model_dump(mode="json"), "missing_requirements": validation["missing_requirements"], "calculations": calculations, "sizing_envelope": {"gpu_memory_gb": math.ceil(total), "system_memory_gb": max(64, math.ceil(total * 1.5 / 32) * 32), "local_nvme_tb": max(2, math.ceil(total * 6 / 1000)), "network_gbps": 25 if project.concurrency.peak_users > 10 else 10, "estimated_it_load_kw": round(max(1.0, total / 80 * 0.9), 1)}, "assumptions": ["20% runtime memory overhead", f"{int((project.growth_factor-1)*100)}% growth headroom", "Performance must be confirmed with the actual model/runtime benchmark."], "warnings": (["KV cache used an architecture-neutral planning heuristic; provide measured per-session cache for stronger sizing."] if heuristic else []), "confidence_score": 0.55 if heuristic else 0.72}


def assess_existing_infrastructure(payload: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    need = analyze_inference_project(payload)["sizing_envelope"]
    gpu = float(existing.get("total_gpu_memory_gb", 0) or 0)
    power = float(existing.get("available_power_kw", 0) or 0)
    reusable = [name for name in ("identity_provider", "monitoring", "storage", "network") if existing.get(name)]
    gaps = []
    if gpu < need["gpu_memory_gb"]:
        gaps.append({"resource": "gpu_memory_gb", "available": gpu, "required": need["gpu_memory_gb"]})
    if power and power < need["estimated_it_load_kw"]:
        gaps.append({"resource": "power_kw", "available": power, "required": need["estimated_it_load_kw"]})
    return {**_base(), "reusable_components": reusable, "capacity_gaps": gaps, "security_gaps": ["Document trust boundaries and controlled-data flows before integration."], "integration_appropriate": not gaps and bool(existing), "required_changes": ["Benchmark target model/runtime", "Validate network segmentation", "Validate storage and backup capacity"]}


def recommend_architecture(payload: dict[str, Any]) -> dict[str, Any]:
    project = _project(payload)
    existing = project.existing_infrastructure
    assessment = assess_existing_infrastructure(payload, existing)
    regulated = project.compliance.itar or project.compliance.cmmc or project.data_sensitivity == "controlled"
    if regulated:
        choice = "new_architecture"
        reason = "Controlled or regulated workflow requires a separately reviewed security zone."
    elif assessment["integration_appropriate"]:
        choice = "existing_system_integration"
        reason = "Declared existing capacity covers the planning envelope, subject to benchmark validation."
    elif existing:
        choice = "separate_server_existing_integration"
        reason = "Existing shared services are reusable but compute capacity is incomplete."
    else:
        choice = "separate_server_existing_integration"
        reason = "A dedicated pilot node limits disruption while requirements are validated."
    alternatives = [
        {"pattern": "existing_system_integration", "capital_cost": "lower", "isolation": "lower", "integration_effort": "medium", "suitability": "only after capacity and boundary validation"},
        {"pattern": "separate_server_existing_integration", "capital_cost": "medium", "isolation": "medium", "integration_effort": "medium", "suitability": "pilot and departmental production"},
        {"pattern": "new_architecture", "capital_cost": "higher", "isolation": "high", "integration_effort": "high", "suitability": "controlled workloads or platform scale"},
        {"pattern": "hybrid_architecture", "capital_cost": "variable", "isolation": "variable", "integration_effort": "high", "suitability": "distributed plant/core workloads"},
    ]
    return {**_base(), "recommended_pattern": choice, "alternatives": alternatives, "integration_path": {"classification": choice, "reasoning": [reason], "required_interfaces": ["identity", "model storage", "observability", "agent/API network"], "migration_steps": ["validate requirements", "benchmark pilot", "approve security design", "stage deployment", "run acceptance tests"]}, "security_zones": ["management", "inference", "data", "client"], "availability_design": {"target": project.availability.get("target", "not supplied"), "recommendation": "Add redundant nodes only after workload benchmark and recovery objectives are confirmed."}, "network_design": {"default": "deny inter-zone flows; explicitly allow authenticated service paths"}, "data_flow": {"status": "requires site-specific mapping"}, "assumptions": ["No product performance or site readiness has been independently verified."], "risks": ["Sizing uncertainty", "Unverified component origin", "Driver/firmware lifecycle", "Power and cooling constraints"]}


def generate_hardware_spec(payload: dict[str, Any]) -> dict[str, Any]:
    sizing = analyze_inference_project(payload)["sizing_envelope"]
    gpu_count = max(1, math.ceil(sizing["gpu_memory_gb"] / 80))
    return {**_base(), "hardware_neutral": True, "gpu": {"count": gpu_count, "aggregate_memory_gb_min": sizing["gpu_memory_gb"], "per_accelerator_memory_gb_min": math.ceil(sizing["gpu_memory_gb"] / gpu_count), "interconnect": "peer-to-peer high-bandwidth fabric required when model spans accelerators"}, "cpu": {"architecture": "x86_64 or arm64 supported by selected runtime", "physical_cores_min": max(16, gpu_count * 16)}, "system_memory_gb_min": sizing["system_memory_gb"], "local_nvme_tb_min": sizing["local_nvme_tb"], "network": {"data_plane_gbps_min": sizing["network_gbps"], "management_interface": "dedicated"}, "pcie": {"generation_min": 4, "lanes": "validate full accelerator bandwidth and slot layout"}, "power": {"estimated_it_load_kw": sizing["estimated_it_load_kw"], "redundancy": "N+1 power supplies"}, "cooling": {"heat_load_kw": sizing["estimated_it_load_kw"], "validation": "site facilities review required"}, "rack_units": "4-8U planning envelope; confirm chassis", "security": {"tpm": "2.0", "secure_boot": True, "remote_management": "dedicated, access-controlled management plane"}, "runtime": ["OCI containers", "GPU runtime selected after compatibility validation"], "support": "production warranty and firmware/driver support required", "assumptions": ["Vendor-neutral planning values; model benchmarks and physical site survey remain required."]}


def generate_bom(payload: dict[str, Any]) -> dict[str, Any]:
    spec = generate_hardware_spec(payload)
    count = spec["gpu"]["count"]
    items = [
        Component(category="compute_node", description="Server chassis satisfying rack, PCIe, remote-management and redundant-power specification", quantity=1, rationale="Inference host").model_dump(),
        Component(category="gpu", description=f"Accelerator with at least {spec['gpu']['per_accelerator_memory_gb_min']} GB usable memory", quantity=count, rationale="Hardware-neutral capacity requirement").model_dump(),
        Component(category="system_memory", description=f"ECC memory, at least {spec['system_memory_gb_min']} GB", quantity=1, rationale="Runtime and ingestion headroom").model_dump(),
        Component(category="storage", description=f"Enterprise NVMe, at least {spec['local_nvme_tb_min']} TB usable", quantity=1, rationale="Models, cache and local artifacts").model_dump(),
        Component(category="network", description=f"Data-plane adapter, at least {spec['network']['data_plane_gbps_min']} Gb/s", quantity=1, rationale="Inference and storage traffic").model_dump(),
        Component(category="deployment_services", description="Rack, firmware, burn-in, benchmark and acceptance-test services", quantity=1, rationale="Implementation and evidence collection").model_dump(),
    ]
    return {**_base(), "bom_type": "required_specification", "items": items, "specific_products_selected": False, "total_cost": None, "limitations": ["No price, availability, part number, origin, compatibility or compliance is asserted without current evidence."]}


def screen_bom_for_compliance(bom: dict[str, Any], policy_input: dict[str, Any]) -> dict[str, Any]:
    name = policy_input.get("policy", "standard")
    merged = {**POLICIES.get(name, {}), **policy_input, "policy": name}
    policy = SourcingPolicy.model_validate(merged)
    findings: list[str] = []
    results = []
    prohibited = {x.upper() for x in policy.prohibited_countries}
    for raw in bom.get("items", []):
        item = Component.model_validate(raw)
        gaps = []
        status = "approved" if policy.policy == "standard" else "conditionally_approved"
        origin = item.country_of_origin.upper()
        if origin in prohibited:
            status = "prohibited"
            gaps.append("country_of_origin is prohibited by the configured project policy")
        elif policy.require_country_of_origin_evidence and (origin == "UNKNOWN" or not item.manufacturing_evidence):
            status = "needs_evidence"
            gaps.append("authoritative country-of-origin evidence")
        if policy.require_firmware_review and not item.firmware_provenance:
            status = "needs_evidence" if status != "prohibited" else status
            gaps.append("firmware provenance review")
        if policy.require_software_supply_chain_review and not item.software_supply_chain_reviewed:
            status = "needs_evidence" if status != "prohibited" else status
            gaps.append("software/driver supply-chain review")
        if policy.require_supplier_review and item.supplier_approved is not True:
            status = "needs_evidence" if status != "prohibited" else status
            gaps.append("approved supplier evidence")
        results.append({"category": item.category, "part_number": item.part_number, "status": status, "evidence_gaps": gaps})
        findings.extend(f"{item.category}: {gap}" for gap in gaps)
    blocked = any(x["status"] == "prohibited" for x in results)
    needs = any(x["status"] == "needs_evidence" for x in results)
    return {**_base(), "policy": policy.model_dump(), "decision": "fail" if blocked else "needs_evidence" if needs else "pass", "human_review_required": policy.require_human_approval, "procurement_authorized": False if policy.require_human_approval else not (blocked or needs), "line_results": results, "failed_rules": findings, "limitations": ["This screening enforces configured workflow rules; it does not certify CMMC, ITAR, export-control, TAA, Buy American, or contract compliance."]}


def compare_bom_options(boms: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for index, bom in enumerate(boms):
        items = [Component.model_validate(x) for x in bom.get("items", [])]
        known = [x.unit_price * x.quantity for x in items if x.unit_price is not None]
        rows.append({"option": bom.get("name", f"option-{index+1}"), "line_items": len(items), "known_cost": round(sum(known), 2) if len(known) == len(items) else None, "unknown_cost_lines": len(items) - len(known), "unverified_origin_lines": sum(x.country_of_origin == "unknown" for x in items), "vendor_concentration": "unknown" if not any(x.manufacturer for x in items) else len({x.manufacturer for x in items if x.manufacturer})})
    return {**_base(), "options": rows, "recommendation": "Select only after benchmark, compatibility, lifecycle, origin, support and price evidence are comparable.", "ranking": None}


def generate_deployment_plan(payload: dict[str, Any]) -> dict[str, Any]:
    architecture = recommend_architecture(payload)
    phases = [
        ("site readiness", ["rack/power/cooling survey", "network and data-flow review"]),
        ("platform foundation", ["firmware baseline", "secure boot/TPM", "OS hardening", "container and accelerator runtime"]),
        ("service integration", ["identity", "secrets", "model serving", "agent platform", "logging and metrics"]),
        ("verification", ["functional tests", "load/latency benchmark", "failure recovery", "security validation", "backup restore"]),
        ("release", ["human approvals", "staged cutover", "rollback checkpoint", "operational handoff"]),
    ]
    return {**_base(), "architecture": architecture["recommended_pattern"], "phases": [{"name": n, "tasks": t, "exit_evidence": f"approved {n} checklist"} for n, t in phases], "rollback": "Retain prior service path and configuration until acceptance criteria and recovery tests pass.", "human_approval_points": ["security/data-flow design", "regulated procurement", "production cutover"], "assumptions": architecture["assumptions"]}


def save_artifacts(project_id: str, artifacts: dict[str, Any]) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,62}", project_id):
        raise ValueError("project_id must be a lowercase slug of at most 63 characters")
    root = Path(os.getenv("INFERENCE_DATA_DIR", "/data")) / "artifacts" / project_id
    root.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(artifacts, indent=2, sort_keys=True) + "\n"
    path = root / "project.json"
    path.write_text(payload, encoding="utf-8")
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return {**_base(), "project_id": project_id, "resource_uri": f"inference://projects/{project_id}", "sha256": digest}


def render_bom_csv(bom: dict[str, Any]) -> str:
    out = io.StringIO()
    fields = ["category", "description", "manufacturer", "part_number", "quantity", "country_of_origin", "supplier", "unit_price", "currency", "availability_status", "compliance_status", "rationale"]
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(bom.get("items", []))
    return out.getvalue()
