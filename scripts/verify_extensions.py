from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "spec-kit-extensions.lock.json").read_text(encoding="utf-8"))

for extension in LOCK["extensions"]:
    manifest = ROOT / ".specify" / "extensions" / extension["id"] / "extension.yml"
    if not manifest.is_file():
        raise SystemExit(f"missing installed extension: {extension['id']}")
    if f"version: {extension['version']}" not in manifest.read_text(encoding="utf-8"):
        raise SystemExit(f"extension version mismatch: {extension['id']}")
print("Pinned Spec Kit extensions are installed; source archive digests are recorded.")

