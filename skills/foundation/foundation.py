#!/usr/bin/env python3
"""Dependency-free command helper for the AI Delivery Foundation."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = (
    "README.md", "AGENTS.md", "CONTRIBUTING.md", "ARCHITECTURE.md", "SECURITY.md",
    "AI_POLICY.md", "DATA_POLICY.md", "PROJECT.yaml", "plumbline.toml",
    ".plumbline/plumbline.py", ".plumbline/guard.py", ".github/CODEOWNERS",
)
REQUIRED_DIRS = (".github", "docs", "src", "tests", "ai", "infrastructure", "config", "policies", "scripts")
POLICY_PATHS = {
    "ai": "policies/ai/",
    "infrastructure": "policies/architecture/ and policies/devops/",
    "config/": "policies/devops/ and policies/security/",
    "policies/data": "policies/data/",
    "policies/security": "policies/security/",
    "src": "policies/architecture/ and policies/quality/ where configured",
    ".github": "policies/devops/ and policies/repository/",
}
MINIMAL_FILES = (
    "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "AI_POLICY.md", "DATA_POLICY.md", "PROJECT.yaml",
    "ARCHITECTURE.md", "plumbline.toml", ".plumbline/plumbline.py", ".plumbline/guard.py",
    "scripts/plumbline-check.sh", "scripts/plumbline-guard.sh", "scripts/validate.ps1",
    ".github/CODEOWNERS", ".github/pull_request_template.md",
)
FULL_ROOT_FILES = ("README.md", "Makefile")
FULL_DIRECTORIES = ("agents", "ai", "config", "docs", "policies", "scripts", "skills", ".github")


def markdown_assessment(root: Path) -> dict[str, object]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).is_file()]
    missing_dirs = [path for path in REQUIRED_DIRS if not (root / path).is_dir()]
    project = root / "PROJECT.yaml"
    placeholders = []
    if project.is_file() and "CHANGE_ME" in project.read_text(errors="ignore"):
        placeholders.append("PROJECT.yaml")
    return {
        "root": str(root),
        "missing_files": missing_files,
        "missing_directories": missing_dirs,
        "unconfigured_files": placeholders,
        "ready": not (missing_files or missing_dirs or placeholders),
    }


def render_assessment(data: dict[str, object]) -> str:
    status = "READY" if data["ready"] else "GAPS FOUND"
    lines = [f"# Foundation assessment: {status}", "", f"Repository: `{data['root']}`", ""]
    for label, key in (("Missing files", "missing_files"), ("Missing directories", "missing_directories"),
                       ("Unconfigured files", "unconfigured_files")):
        values = data[key]
        lines.append(f"## {label}")
        lines.extend(f"- `{value}`" for value in values) if values else lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def run_process(command: list[str], root: Path) -> int:
    environment = os.environ.copy()
    environment.setdefault("PYTHONIOENCODING", "utf-8")
    return subprocess.run(command, cwd=root, check=False, env=environment).returncode


def check(root: Path) -> int:
    gate = root / ".plumbline" / "plumbline.py"
    if not gate.is_file():
        print("Foundation check cannot run: .plumbline/plumbline.py is missing.", file=sys.stderr)
        return 1
    gate_result = run_process([sys.executable, str(gate), "--all", "--format", "markdown"], root)
    if gate_result:
        return gate_result
    validator = root / "scripts" / "validate.ps1"
    if validator.is_file() and shutil.which("powershell"):
        return run_process(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(validator)], root)
    return 0


def policy(paths: list[str]) -> str:
    if not paths:
        return "\n".join([
            "Available foundation policy domains:",
            "- repository: policies/repository/",
            "- architecture: policies/architecture/",
            "- DevOps: policies/devops/",
            "- security: policies/security/",
            "- data: policies/data/",
            "- AI: policies/ai/",
        ])
    matched: dict[str, str] = {}
    for path in paths:
        normalized = path.replace("\\", "/")
        owners = [value for prefix, value in POLICY_PATHS.items() if normalized == prefix or normalized.startswith(prefix + "/")]
        matched[path] = "; ".join(owners) if owners else "policies/repository/ and the project-specific overlay"
    return "\n".join(f"- `{path}` -> {owners}" for path, owners in matched.items())


def scaffold_files(source: Path, mode: str) -> list[Path]:
    if mode == "minimal":
        candidates = [source / path for path in MINIMAL_FILES]
    else:
        candidates = [source / path for path in (*MINIMAL_FILES, *FULL_ROOT_FILES)]
        for directory in FULL_DIRECTORIES:
            candidates.extend((source / directory).rglob("*"))
    return sorted({path for path in candidates if path.is_file()}, key=lambda path: path.as_posix())


def scaffold(source: Path, target: Path, mode: str, apply: bool) -> int:
    source = source.resolve()
    target = target.resolve()
    if source == target or source in target.parents:
        print("Scaffold target must be outside the foundation source repository.", file=sys.stderr)
        return 1

    files = scaffold_files(source, mode)
    if not files:
        print(f"No {mode} foundation files were found in {source}.", file=sys.stderr)
        return 1

    print(f"Foundation scaffold: {mode} -> {target}")
    added = skipped = 0
    for source_file in files:
        relative = source_file.relative_to(source)
        destination = target / relative
        if destination.exists():
            print(f"SKIP  {relative} (already exists)")
            skipped += 1
            continue
        print(f"ADD   {relative}" if apply else f"PLAN  {relative}")
        added += 1
        if apply:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)
    if not apply:
        print("Dry run only. Re-run with --apply to add missing files; existing files are never overwritten.")
    print(f"Summary: {added} {'added' if apply else 'planned'}, {skipped} skipped")
    return 0


def plan(command: str, root: Path) -> int:
    print(f"/foundation {command} plan for {root}")
    print("1. Review the repository assessment and current owners.")
    print("2. Create a human-reviewed branch in the target repository.")
    print("3. Merge only the missing foundation files and preserve existing project conventions.")
    print("4. Run /foundation check and open a pull request; a human approves the result.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="foundation")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("assess", "init", "adopt", "check", "baseline", "report"):
        command = sub.add_parser(name)
        command.add_argument("path", nargs="?", default=".")
    policy_parser = sub.add_parser("policy")
    policy_parser.add_argument("paths", nargs="*")
    scaffold_parser = sub.add_parser("scaffold")
    scaffold_parser.add_argument("target")
    scaffold_parser.add_argument("--source", default=str(Path(__file__).resolve().parents[2]))
    scaffold_parser.add_argument("--mode", choices=("minimal", "full"), default="minimal")
    scaffold_parser.add_argument("--apply", action="store_true")
    sub.add_parser("protect")
    args = parser.parse_args(argv)

    if args.command == "policy":
        print(policy(args.paths))
        return 0
    if args.command == "protect":
        print("Protect main with required PRs, required CI checks, CODEOWNER approval, current branches, and no force pushes.")
        print("See docs/administrator-setup.md for the human administrator checklist.")
        return 0
    if args.command == "scaffold":
        return scaffold(Path(args.source), Path(args.target), args.mode, args.apply)

    root = Path(args.path).resolve()
    if args.command == "assess":
        print(render_assessment(markdown_assessment(root)))
        return 0
    if args.command == "check":
        return check(root)
    if args.command in {"init", "adopt"}:
        return plan(args.command, root)
    if args.command == "baseline":
        baseline = root / "docs" / "architecture" / "baseline.yaml"
        print(f"Architecture baseline: {baseline}")
        print("Run scripts/validate-baseline.sh with CHANGED_FILES_FILE in a PR context.")
        return 0 if baseline.is_file() else 1
    if args.command == "report":
        print(render_assessment(markdown_assessment(root)))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
