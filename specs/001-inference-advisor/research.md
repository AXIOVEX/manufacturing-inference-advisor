# Research and decisions

Docker Desktop 4.91.0 provides MCP Toolkit 0.43.3. Docker profiles are named server collections; clients launch them with `docker mcp gateway run --profile`. The local profile uses unsigned development images with signature verification disabled explicitly and blocks network. Production should publish signed digest-pinned images.

“AEE” resolves to ElectroHire's community `spec-kit-aee` 1.0.0, not an official GitHub extension. It requires Spec Kit >=1.0.0, Applied Epistemic Engineering >=1.0.0 and Evaluator commands. Sources, immutable commit and archive hashes are in `spec-kit-extensions.lock.json`. Installed baseline: Spec Kit 1.0.6, AEE engine 1.0.2 and Evaluator 1.0.0.

The initial component catalog is specification-only. Product performance, prices, availability, origin, firmware and support require current authoritative evidence.

