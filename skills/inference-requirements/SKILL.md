---
name: inference-requirements
description: Normalize and validate manufacturing AI inference workload requirements before architecture or hardware decisions.
---
# Inference requirements
Use first for new or revised inference projects. Gather models, quantization, context, concurrency, latency/throughput, workloads, availability, data sensitivity, site constraints, compliance and existing infrastructure. Call `validate_requirements_tool`, then `analyze_inference_project_tool`. Save normalized requirements and calculation lineage. Do not proceed silently past missing power, cooling, latency, model or controlled-data facts; label assumptions and reduce confidence. Hardware selection is outside this step. Human review is required for controlled/regulated scope. Output normalized JSON, missing facts, calculations, warnings and confidence.

