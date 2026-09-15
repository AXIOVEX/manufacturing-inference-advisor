from __future__ import annotations

from pathlib import Path

from inference_advisor import cli


def test_script_uses_repository_wrapper(monkeypatch, tmp_path: Path) -> None:
    wrapper = tmp_path / "scripts" / "docker_mcp.py"
    wrapper.parent.mkdir()
    wrapper.write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert cli._script() == wrapper


def test_menu_runs_selected_action_then_quits(monkeypatch) -> None:
    choices = iter(["3", "q"])
    actions: list[str] = []
    monkeypatch.setattr(cli.Prompt, "ask", lambda *args, **kwargs: next(choices))
    monkeypatch.setattr(cli, "run_action", lambda action: actions.append(action) or 0)
    cli.main()
    assert actions == ["verify"]
