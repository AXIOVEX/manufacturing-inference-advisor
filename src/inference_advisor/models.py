from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelWorkload(StrictModel):
    name: str = Field(min_length=1, max_length=200)
    parameter_count_b: float = Field(gt=0, le=10_000)
    quantization: Literal["fp32", "fp16", "bf16", "int8", "int4"] = "int4"
    context_length: int = Field(ge=128, le=10_000_000)
    kv_cache_gb_per_session: float | None = Field(default=None, gt=0)


class Concurrency(StrictModel):
    peak_users: int = Field(ge=1, le=1_000_000)
    target_requests_per_second: float | None = Field(default=None, gt=0)
    target_first_token_ms: int | None = Field(default=None, gt=0)
    target_tokens_per_second: float | None = Field(default=None, gt=0)


class Compliance(StrictModel):
    cmmc: bool = False
    itar: bool = False
    export_control: bool = False
    policy: Literal["standard", "enterprise_restricted", "cmmc", "itar"] | None = None


class ProjectRequest(StrictModel):
    project_name: str = Field(min_length=1, max_length=200)
    industry: str = Field(min_length=1, max_length=100)
    location: str | None = Field(default=None, max_length=200)
    models: list[ModelWorkload] = Field(min_length=1, max_length=32)
    concurrency: Concurrency
    workloads: list[str] = Field(min_length=1, max_length=100)
    availability: dict[str, Any] = Field(default_factory=dict)
    compliance: Compliance = Field(default_factory=Compliance)
    existing_infrastructure: dict[str, Any] = Field(default_factory=dict)
    site_constraints: dict[str, Any] = Field(default_factory=dict)
    data_sensitivity: Literal["public", "internal", "confidential", "controlled"] = "internal"
    growth_factor: float = Field(default=1.25, ge=1, le=10)

    @model_validator(mode="after")
    def consistent_policy(self) -> ProjectRequest:
        if self.compliance.itar and self.compliance.policy not in (None, "itar"):
            raise ValueError("ITAR projects cannot select a weaker policy")
        if self.compliance.cmmc and self.compliance.policy == "standard":
            raise ValueError("CMMC projects cannot select the standard policy")
        return self


class Component(StrictModel):
    category: str
    description: str
    quantity: int = Field(ge=1, le=10_000)
    manufacturer: str | None = None
    part_number: str | None = None
    country_of_origin: str = "unknown"
    assembly_country: str = "unknown"
    manufacturing_evidence: list[dict[str, Any]] = Field(default_factory=list)
    supplier: str | None = None
    unit_price: float | None = Field(default=None, ge=0)
    currency: str = "USD"
    availability_status: str = "unknown"
    compliance_status: str = "unverified"
    firmware_provenance: str | None = None
    software_supply_chain_reviewed: bool = False
    supplier_approved: bool | None = None
    rationale: str = ""


class SourcingPolicy(StrictModel):
    policy: Literal["standard", "enterprise_restricted", "cmmc", "itar"]
    required_origin_regions: list[str] = Field(default_factory=list)
    prohibited_countries: list[str] = Field(default_factory=list)
    require_country_of_origin_evidence: bool = False
    require_software_supply_chain_review: bool = False
    require_firmware_review: bool = False
    require_supplier_review: bool = False
    require_data_flow_review: bool = False
    require_human_approval: bool = False

