---
name: hardware-sizing
description: Produce vendor-neutral manufacturing inference compute, memory, storage, network, power and cooling specifications.
---
# Hardware sizing
Use only after requirements and architecture are recorded. Call `analyze_inference_project_tool`, then `generate_hardware_spec_tool`. Preserve formula identifiers, inputs, headroom, warnings and confidence. Validate GPU memory, PCIe lanes, system memory, storage, network, rack, power, cooling, TPM, secure boot and support. Treat unbenchmarked throughput and heuristic cache as estimates. Product choice is outside this step. Facilities and platform owners approve the site envelope. Output a hardware-neutral JSON specification and gaps.
