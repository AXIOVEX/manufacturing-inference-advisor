from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str, cwd: Path = ROOT, capture: bool = False) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=capture)
    return result.stdout if capture else ""


def setting(name: str, default: str) -> str:
    return os.getenv(name, default)


def setup() -> None:
    workforce = (ROOT / setting("WORKFORCE_REPO", "../michigan-workforce-intelligence")).resolve()
    if not (workforce / "Dockerfile").is_file():
        raise SystemExit(f"Workforce repository not found: {workforce}")
    inference = setting("INFERENCE_MCP_IMAGE", "manufacturing-inference-advisor:local")
    workforce_image = setting("WORKFORCE_MCP_IMAGE", "michigan-workforce-mcp:local")
    profile = setting("DOCKER_MCP_PROFILE", "manufacturing-intelligence")
    run("docker", "build", "--target", "runtime", "-t", inference, ".")
    run("docker", "build", "--target", "mcp-stdio", "-t", workforce_image, ".", cwd=workforce)
    catalog_dir = Path.home() / ".docker" / "mcp" / "catalogs" / "manufacturing-intelligence"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    for name in ("inference-advisor.yaml", "michigan-workforce.yaml"):
        shutil.copyfile(ROOT / "docker-mcp" / name, catalog_dir / name)
    refs = ("file://manufacturing-intelligence/michigan-workforce.yaml", "file://manufacturing-intelligence/inference-advisor.yaml")
    profiles = run("docker", "mcp", "profile", "list", capture=True)
    command = ("profile", "server", "add", profile) if profile in profiles else ("profile", "create", "--name", "Manufacturing Intelligence", "--id", profile)
    run("docker", "mcp", *command, "--server", refs[0], "--server", refs[1])
    client = setting("DOCKER_MCP_CLIENT", "codex")
    if client.lower() not in {"", "none"}:
        run("docker", "mcp", "client", "connect", client, "--global", "--profile", profile)
    print(f"Ready: docker mcp gateway run --profile {profile} --verify-signatures=false --block-network")


def verify(profile: str) -> None:
    gateway = (
        "--gateway-arg=--profile=" + profile,
        "--gateway-arg=--verify-signatures=false",
        "--gateway-arg=--block-network",
    )
    project = json.loads(
        (ROOT / "docs" / "examples" / "standard-project.json").read_text(encoding="utf-8")
    )
    inference = run(
        "docker",
        "mcp",
        "tools",
        "call",
        "validate_requirements_tool",
        "project=" + json.dumps(project, separators=(",", ":")),
        *gateway,
        capture=True,
    )
    workforce = run(
        "docker", "mcp", "tools", "call", "ledger_audit", "{}", *gateway, capture=True
    )
    if '"valid": true' not in inference or '"valid": true' not in workforce:
        raise SystemExit("A live MCP tool call did not return a valid result")
    print(f"Verified live inference and workforce calls through profile {profile}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and configure the Docker MCP companion suite")
    parser.add_argument("command", choices=["setup", "test", "verify", "command"])
    args = parser.parse_args()
    profile = setting("DOCKER_MCP_PROFILE", "manufacturing-intelligence")
    if args.command == "setup":
        setup()
    elif args.command == "test":
        run("docker", "mcp", "gateway", "run", "--profile", profile, "--verify-signatures=false", "--block-network", "--dry-run")
        print(f"Profile {profile} resolved successfully")
    elif args.command == "verify":
        verify(profile)
    else:
        print(f"docker mcp gateway run --profile {profile} --verify-signatures=false --block-network")


if __name__ == "__main__":
    main()
