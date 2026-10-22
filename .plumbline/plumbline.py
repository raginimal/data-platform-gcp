#!/usr/bin/env python3
"""
plumbline — a dependency-free quality gate for AI-generated changes.

Runs the same checks in four places (DevOps "shift-left"):
  1. the agent loop   (post-edit hook for Claude Code, GitHub Copilot and Gemini CLI: --hook)
  2. pre-commit       (--staged)
  3. CI / PR gate     (--diff origin/main, with --format sarif|markdown|json)
  4. trend reporting  (--all --format json >> history)

Config: plumbline.toml at the repo root (optional). Python 3.11+, stdlib only.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

try:
    import tomllib  # 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

VERSION = "2.6.0"
# repeated config (YAML, Terraform variables) is normal; duplication is only a code smell in programming languages
DUP_IGNORE_EXT = {".yaml", ".yml", ".tf", ".sql"}
SEVERITY_WEIGHT = {"error": 10, "warn": 3, "info": 1}
SEVERITY_RANK = {"info": 0, "warn": 1, "error": 2}

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".java", ".cs",
            ".go", ".rb", ".php", ".kt", ".scala", ".rs", ".swift", ".sql",
            ".sh", ".ps1", ".tf", ".yaml", ".yml"}
PROSE_EXT = {".md", ".mdx", ".rst", ".txt", ".adoc"}

DEFAULT_CONFIG = {
    "fail_on": "error",                # error | warn | info | never
    "min_score": 0,                    # optional score floor (0-100)
    "max_changed_lines": 400,          # PRs larger than this need a human split/justification
    "max_comment_ratio": 0.45,         # comment lines / code lines in a single file
    "require_tests_for": ["src/**", "app/**", "lib/**"],
    "test_globs": ["tests/**", "test/**", "**/*_test.*", "**/*.test.*", "**/*.spec.*", "**/test_*.py"],
    "exclude": [".git/**", "node_modules/**", ".venv/**", "venv/**", "dist/**", "build/**",
                "**/*.min.js", "**/*.lock", "package-lock.json", ".plumbline/**", ".claude/skills/plumbline/**",
                "**/__pycache__/**"],
    "disabled_rules": [],
    "severity_overrides": {},          # e.g. { PL005 = "error" }
    "require_ai_trailer": False,       # commit-msg: require "AI-Assisted: yes|no"
    "ai_trailer_key": "AI-Assisted",   # or the team's own convention, e.g. "Assisted-by" (any value accepted)
    "extra_banned_phrases": [],
    # --- shared-context governance (multi-engineer / multi-agent repos) ---
    "architecture_file": "ARCHITECTURE.md",
    "adr_dir": "docs/adr",
    "required_docs": ["ARCHITECTURE.md", "AGENTS.md", "AI_POLICY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"],
    "unfinished_markers": ["<!-- EDIT", "TODO(architecture)", "@your-org/"],
    "codeowners_file": ".github/CODEOWNERS",
    # team coding standards as regex rules: [[plumbline.custom_rules]] id/pattern/message/severity/paths/exclude_paths
    "custom_rules": [],
    "max_modules_per_change": 3,
    # packages the runtime provides, so they're legitimately not in a manifest (e.g. airflow on Cloud Composer /
    # MWAA / Fabric, pyspark and dbutils on Databricks)
    "provided_packages": [],
    "protected_branches": [],
    # copies by design: examples, demos, fixtures and per-environment/per-stack overlays
    "duplicate_exclude": ["demo/**", "demos/**", "examples/**", "example/**", "**/fixtures/**", "**/overlay/**",
                          "**/overlays/**", "**/templates/**"],
}

RULES = {
    "PL001": ("Hard-coded secret or credential", "error"),
    "PL002": ("Placeholder / stub left in code", "error"),
    "PL003": ("Chatbot artefact leaked into source", "error"),
    "PL004": ("Excessive narrating comments", "warn"),
    "PL005": ("Debug leftover", "warn"),
    "PL006": ("Possibly hallucinated dependency (import not declared)", "error"),
    "PL007": ("Duplicated block (copy-paste generation)", "warn"),
    "PL008": ("Source changed without tests", "warn"),
    "PL009": ("Swallowed exception", "warn"),
    "PL010": ("Oversized change", "warn"),
    "PL011": ("AI filler in prose / docs", "info"),
    "PL012": ("Missing AI provenance trailer", "error"),
    "PL013": ("Architecture boundary violation", "error"),
    "PL014": ("Shared context missing or unfinished", "error"),
    "PL015": ("Architecture changed without an ADR", "error"),
    "PL016": ("Change spans too many modules", "warn"),
    "PL017": ("Code placed outside the declared architecture", "warn"),
}


def rule_catalogue(cfg: dict) -> dict[str, tuple[str, str]]:
    cat = dict(RULES)
    for r in cfg.get("custom_rules", []):
        cat[r["id"]] = (r.get("title") or r.get("message", r["id"]), r.get("severity", "warn"))
    return cat


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    message: str
    snippet: str = ""
    fingerprint: str = field(default="", repr=False)

    def finalize(self) -> "Finding":
        raw = f"{self.rule}|{self.path}|{self.snippet.strip()}"
        self.fingerprint = hashlib.sha1(raw.encode()).hexdigest()[:16]
        return self


# ---------------------------------------------------------------- patterns
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub token"),
    (re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_\-]{24,}\b"), "LLM provider API key"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"AccountKey=[A-Za-z0-9+/=]{40,}"), "Azure storage account key"),
    # Also catches the keyword inside a longer name (AWS_SECRET_ACCESS_KEY, DB_PASSWORD, githubToken); URLs and
    # paths assigned to such names (TOKEN_URL = "https://…") are not credentials.
    (re.compile(r"""(?i)\b\w*(?:api[_-]?key|secret|passw(?:or)?d|token|client[_-]?secret)\w*\b\s*[:=]\s*"""
                r"""["'](?!https?://|/|\./|\.\./)[^"'\s]{12,}["']"""),
     "credential assigned to a literal"),
]
# Names that contain a credential keyword but hold no credential (tokenizer, token_url, secret_name, password_hint …).
NOT_SECRET_NAME = re.compile(r"""(?i)\b\w*(?:tokeni[sz]er|tokens\b|token_?(?:url|uri|endpoint|type|count|limit|file|path|name)"""
                             r"""|secret_?(?:name|arn|path|ref|id|scope)|passw(?:or)?d_?(?:hint|policy|length|field|label))\w*\s*[:=]""")
PLACEHOLDER_PATTERNS = [
    re.compile(r"(?i)\b(?:TODO|FIXME|XXX)\b[:\s-]*(?:implement|add (?:logic|implementation)|fill in|complete this)"),
    re.compile(r"(?i)(?:#|//|/\*)\s*\.\.\.\s*(?:rest of|existing|remaining|other|same as)\b"),
    re.compile(r"(?i)(?:#|//)\s*(?:your|add your) (?:code|logic|implementation) here"),
    re.compile(r"(?i)\b(?:your[_-]?api[_-]?key[_-]?here|replace[_-]?with[_-]?your|<your[-_ ][a-z _-]+>)"),
    re.compile(r"(?i)lorem ipsum"),
    re.compile(r"^\s*raise NotImplementedError\b"),
    re.compile(r"(?i)throw new Error\(\s*['\"]not implemented"),
]
CHATBOT_PATTERNS = [
    re.compile(r"(?i)\bas an ai (?:language )?model\b"),
    re.compile(r"(?i)^\s*(?:#|//|\*)?\s*(?:certainly|sure)[!,]\s+here(?:'s| is)\b"),
    re.compile(r"(?i)\bi hope this helps\b"),
    re.compile(r"(?i)\bhere(?:'s| is) the (?:updated|complete|full|corrected) (?:code|version|implementation)\b"),
    re.compile(r"(?i)\bknowledge cutoff\b"),
    re.compile(r"^\s*```[a-zA-Z]*\s*$"),  # markdown fences inside source files
]
PROSE_FILLER = [
    re.compile(r"(?i)\b(?:delve|delving) into\b"),
    re.compile(r"(?i)\bin today's (?:fast-paced|ever-evolving|rapidly evolving)\b"),
    re.compile(r"(?i)\b(?:a testament to|tapestry of|navigating the complexities)\b"),
    re.compile(r"(?i)\bit is (?:important|worth) (?:to note|noting) that\b"),
    re.compile(r"(?i)\b(?:seamless(?:ly)?|robust and scalable|cutting-edge|game-chang(?:er|ing))\b"),
    re.compile(r"(?i)\bin conclusion,"),
]
DEBUG_PATTERNS = {
    ".py": [re.compile(r"^\s*(?:breakpoint\(\)|import pdb|pdb\.set_trace\(\)|print\(\s*f?[\"']DEBUG)")],
    ".js": [re.compile(r"^\s*(?:debugger;|console\.(?:log|debug)\()")],
    ".ts": [re.compile(r"^\s*(?:debugger;|console\.(?:log|debug)\()")],
    ".jsx": [re.compile(r"^\s*(?:debugger;|console\.(?:log|debug)\()")],
    ".tsx": [re.compile(r"^\s*(?:debugger;|console\.(?:log|debug)\()")],
    ".cs": [re.compile(r"^\s*(?:Debugger\.Break\(\)|Console\.WriteLine\(\s*\"DEBUG)")],
    ".java": [re.compile(r"^\s*(?:System\.out\.println\(\s*\"DEBUG|e\.printStackTrace\(\))")],
}
SWALLOW_PATTERNS = {
    ".py": re.compile(r"^\s*except(?:\s+(?:Exception|BaseException))?\s*(?:as \w+)?\s*:\s*(?:pass)?\s*$"),
    ".js": re.compile(r"catch\s*(?:\(\s*\w*\s*\))?\s*\{\s*\}"),
    ".ts": re.compile(r"catch\s*(?:\(\s*\w*\s*\))?\s*\{\s*\}"),
    ".java": re.compile(r"catch\s*\([^)]*\)\s*\{\s*\}"),
    ".cs": re.compile(r"catch\s*(?:\([^)]*\))?\s*\{\s*\}"),
}
COMMENT_PREFIX = {".mts": "//", ".cts": "//", ".mjs": "//", ".py": "#", ".sh": "#", ".rb": "#", ".yaml": "#", ".yml": "#", ".tf": "#", ".ps1": "#",
                  ".js": "//", ".ts": "//", ".jsx": "//", ".tsx": "//", ".java": "//", ".cs": "//",
                  ".go": "//", ".kt": "//", ".rs": "//", ".swift": "//", ".php": "//", ".sql": "--"}
IMPORT_LINE = re.compile(r"^(?:import |from \S+ import |using |#include |require\(|const \w+ = require\(|export \* from |package )")
SUPPRESS = re.compile(r"plumbline:\s*ignore(?:\s+([A-Z][A-Z0-9_-]*\d+(?:\s*,\s*[A-Z][A-Z0-9_-]*\d+)*))?", re.I)


# ---------------------------------------------------------------- helpers
def sh(*args: str, cwd: Path) -> str:
    try:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def repo_root(start: Path) -> Path:
    out = sh("git", "rev-parse", "--show-toplevel", cwd=start).strip()
    return Path(out) if out else start


def load_config(root: Path) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    path = root / "plumbline.toml"
    if path.exists() and tomllib:
        with path.open("rb") as fh:
            user = tomllib.load(fh)
        cfg.update(user.get("plumbline", user))
    return cfg


def matches(path: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, g) or fnmatch.fnmatch("/" + path, "*/" + g.lstrip("*/")) for g in globs)


def is_test(path: str, cfg: dict) -> bool:
    return matches(path, cfg["test_globs"])


def suppressed(line: str, rule: str) -> bool:
    m = SUPPRESS.search(line)
    if not m:
        return False
    return m.group(1) is None or rule in m.group(1).upper()


# ---------------------------------------------------------------- dependency manifests (PL006)
def declared_python_deps(root: Path) -> set[str]:
    names: set[str] = set()
    for req in list(root.glob("requirements*.txt")) + list(root.glob("requirements/*.txt")):
        for ln in req.read_text(errors="ignore").splitlines():
            ln = ln.split("#")[0].strip()
            if ln and not ln.startswith("-"):
                names.add(re.split(r"[<>=!~\[; ]", ln)[0].lower().replace("-", "_"))
    pp = root / "pyproject.toml"
    if pp.exists() and tomllib:
        data = tomllib.loads(pp.read_text(errors="ignore"))
        deps = list(data.get("project", {}).get("dependencies", []))
        for group in data.get("project", {}).get("optional-dependencies", {}).values():
            deps += group
        for group in data.get("dependency-groups", {}).values():
            deps += [d for d in group if isinstance(d, str)]
        poetry = data.get("tool", {}).get("poetry", {})
        deps += list(poetry.get("dependencies", {}).keys())
        for g in poetry.get("group", {}).values():
            deps += list(g.get("dependencies", {}).keys())
        for d in deps:
            names.add(re.split(r"[<>=!~\[; ]", d)[0].lower().replace("-", "_"))
    return names


# import name -> distribution name mismatches that commonly trip naive checks
PY_ALIASES = {"yaml": "pyyaml", "cv2": "opencv_python", "pil": "pillow", "sklearn": "scikit_learn",
              "bs4": "beautifulsoup4", "dateutil": "python_dateutil", "dotenv": "python_dotenv",
              "jwt": "pyjwt", "google": "google", "azure": "azure", "attr": "attrs", "magic": "python_magic",
              "jose": "python_jose", "airflow": "apache_airflow", "docx": "python_docx", "pptx": "python_pptx", "fitz": "pymupdf"}


_WALK_SKIP = {".git", "node_modules", ".venv", "venv", "env", "dist", "build", "target", "dbt_packages",
              "__pycache__", ".plumbline", ".tox", ".mypy_cache", ".pytest_cache"}


def _walk(root: Path, pattern: str):
    for p in root.rglob(pattern):
        if not _WALK_SKIP & set(p.relative_to(root).parts[:-1]):
            yield p


def local_python_modules(root: Path) -> set[str]:
    """The repo's own importable names: top-level files/dirs at the root and in src/, plus every package
    (a directory with __init__.py) anywhere — monorepos keep packages in libs/, packages/, services/ …"""
    mods = set()
    for base in (root, root / "src"):
        if base.is_dir():
            for p in base.iterdir():
                if p.suffix == ".py":
                    mods.add(p.stem.lower())
                elif p.is_dir() and not p.name.startswith("."):
                    mods.add(p.name.lower())
    for init in _walk(root, "__init__.py"):
        mods.add(init.parent.name.lower())
    for py in _walk(root, "*.py"):  # scripts imported via sys.path (e.g. tests importing tools/check_x.py)
        mods.add(py.stem.lower())
    return mods


def declared_python_deps_anywhere(root: Path) -> set[str]:
    """Union of Python dependencies declared by every manifest in the repo (monorepos, per-stack requirements)."""
    names = declared_python_deps(root)
    dirs = {p.parent for pat in ("requirements*.txt", "pyproject.toml") for p in _walk(root, pat)}
    for d in dirs:
        names |= declared_python_deps(d)
    return names


def declared_js_deps(root: Path) -> set[str] | None:
    pkg = root / "package.json"
    if not pkg.exists():
        return None
    data = json.loads(pkg.read_text(errors="ignore") or "{}")
    names = set()
    for k in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        names |= set(data.get(k, {}).keys())
    return names


NODE_BUILTINS = {"fs", "path", "os", "http", "https", "url", "util", "crypto", "stream", "events",
                 "child_process", "assert", "buffer", "zlib", "net", "tls", "dns", "readline",
                 "worker_threads", "querystring", "timers", "process", "module", "perf_hooks", "test"}


# ---------------------------------------------------------------- architecture as code (PL013-PL017)
_GLOB_CACHE: dict[str, re.Pattern] = {}


def path_glob(pattern: str) -> re.Pattern:
    """Segment-aware glob: `*` and `?` stay inside one folder, `**` crosses folders (CODEOWNERS/gitignore style)."""
    rx = _GLOB_CACHE.get(pattern)
    if rx is None:
        i, out = 0, []
        while i < len(pattern):
            if pattern.startswith("**/", i):
                out.append("(?:.*/)?")
                i += 3
            elif pattern.startswith("**", i):
                out.append(".*")
                i += 2
            elif pattern[i] == "*":
                out.append("[^/]*")
                i += 1
            elif pattern[i] == "?":
                out.append("[^/]")
                i += 1
            else:
                out.append(re.escape(pattern[i]))
                i += 1
        rx = _GLOB_CACHE[pattern] = re.compile("".join(out) + r"\Z")
    return rx


DBT_REF = re.compile(r"""\bref\(\s*['"]([^'"]+)['"]\s*(?:,\s*['"]([^'"]+)['"]\s*)?\)""")
ARCH_BLOCK = re.compile(r"```toml[ \t]+plumbline-architecture[ \t]*\n(.*?)```", re.S)


@dataclass
class Module:
    name: str
    paths: list[str]
    may_import: list[str]
    forbid_packages: list[str]
    owners: list[str] = field(default_factory=list)


class Architecture:
    """Parsed from the ```toml plumbline-architecture``` block inside ARCHITECTURE.md."""

    def __init__(self, data: dict):
        self.source_roots: list[str] = data.get("source_roots", ["src"])
        self.strict_placement: bool = bool(data.get("strict_placement", False))
        self.architecture_owners: list[str] = list(data.get("architecture_owners", []))
        self.modules = [Module(m["name"], list(m.get("paths", [])), list(m.get("may_import", [])),
                               [p.lower() for p in m.get("forbid_packages", [])], list(m.get("owners", [])))
                        for m in data.get("module", [])]
        self.by_name = {m.name: m for m in self.modules}

    @classmethod
    def load(cls, root: Path, cfg: dict) -> tuple["Architecture | None", str]:
        f = root / cfg["architecture_file"]
        if not f.exists():
            return None, f"{cfg['architecture_file']} not found"
        m = ARCH_BLOCK.search(f.read_text(errors="ignore"))
        if not m:
            return None, "no ```toml plumbline-architecture``` block found"
        if not tomllib:
            return None, "Python 3.11+ required to parse architecture block"
        try:
            arch = cls(tomllib.loads(m.group(1)))
        except (tomllib.TOMLDecodeError, KeyError, TypeError) as e:
            return None, f"architecture block is invalid: {e}"
        if not arch.modules:
            return None, "architecture block declares no [[module]] entries"
        unknown = {d for mod in arch.modules for d in mod.may_import} - set(arch.by_name)
        if unknown:
            return None, f"may_import references undeclared module(s): {', '.join(sorted(unknown))}"
        return arch, ""

    def module_of(self, rel: str) -> Module | None:
        for mod in self.modules:
            # a bare package/directory path also belongs to the module that owns its contents
            if any(path_glob(g).match(rel) or path_glob(g).match(rel + "/_") for g in mod.paths):
                return mod
        return None

    def under_source_root(self, rel: str) -> bool:
        return any(rel == r or rel.startswith(r.rstrip("/") + "/") for r in self.source_roots)


CO_BEGIN = "# BEGIN plumbline (generated from ARCHITECTURE.md - run `make codeowners`; edit owners there)"
CO_END = "# END plumbline"


def codeowners_block(arch: "Architecture", cfg: dict) -> str:
    gov = arch.architecture_owners or sorted({o for m in arch.modules for o in m.owners})
    lines = [CO_BEGIN]
    if gov:
        lines.append(f"* {' '.join(gov)}")
    for m in arch.modules:
        if m.owners:
            for g in m.paths:
                lines.append(f"/{g} {' '.join(m.owners)}")
    if gov:  # last match wins: shared context is always reviewed by architecture owners
        for f in [*cfg["required_docs"], "plumbline.toml", ".plumbline/", ".github/", f"{cfg['adr_dir'].rstrip('/')}/"]:
            lines.append(f"/{f} {' '.join(gov)}")
    lines.append(CO_END)
    return "\n".join(lines) + "\n"


def merge_codeowners(existing: str, block: str) -> str:
    if CO_BEGIN in existing and CO_END in existing:
        pre, rest = existing.split(CO_BEGIN, 1)
        return pre + block.rstrip("\n") + rest.split(CO_END, 1)[1]
    return (existing.rstrip() + "\n\n" if existing.strip() else "") + block


_SRC_EXT = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".d.ts")


def exists_in_repo(root: Path, cand: str) -> bool:
    """An import candidate only resolves to a module if that file or package really exists in the repo."""
    p = root / cand
    return p.is_dir() or p.is_file() or any(Path(str(p) + e).is_file() for e in _SRC_EXT)


def python_imports(text: str, rel: str, roots: list[str]) -> list[tuple[int, str, list[str]]]:
    """-> [(line, top_level_package, candidate_repo_paths)] using the AST (no regex guessing)."""
    import ast
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    here = Path(rel).parent
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                out.append((node.lineno, parts[0].lower(),
                            [(Path(r) / Path(*parts)).as_posix() for r in ["", *roots]]))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import -> resolve against this file's package
                base = here
                for _ in range(node.level - 1):
                    base = base.parent
                mod_parts = node.module.split(".") if node.module else []
                targets = [base.joinpath(*mod_parts, a.name).as_posix() for a in node.names] or [base.as_posix()]
                out.append((node.lineno, "", targets))
            elif node.module:
                parts = node.module.split(".")
                cands = []
                for r in ["", *roots]:
                    base = Path(r) / Path(*parts)
                    cands += [base.as_posix()] + [(base / a.name).as_posix() for a in node.names if a.name != "*"]
                out.append((node.lineno, parts[0].lower(), cands))
    return out


def js_imports(lines: list[str], rel: str) -> list[tuple[int, str, list[str]]]:
    rx = re.compile(r"""(?:from\s+|require\(\s*|import\(\s*|^\s*import\s+)["']([^"']+)["']""")
    out = []
    for i, ln in enumerate(lines, 1):
        for spec in rx.findall(ln):
            if spec.startswith("."):
                target = os.path.normpath((Path(rel).parent / spec).as_posix()).replace(os.sep, "/")
                out.append((i, "", [target]))
            else:
                spec = spec.removeprefix("node:")
                pkg = "/".join(spec.split("/")[:2]) if spec.startswith("@") else spec.split("/")[0]
                out.append((i, pkg.lower(), []))
    return out


# ---------------------------------------------------------------- scanner
class Scanner:
    def __init__(self, root: Path, cfg: dict):
        self.root, self.cfg = root, cfg
        self.findings: list[Finding] = []
        self._py_deps = self._js_deps = self._py_local = None
        self.stdlib = set(getattr(sys, "stdlib_module_names", ()))
        self.arch, self.arch_error = Architecture.load(root, cfg)
        self.catalogue = rule_catalogue(cfg)
        self.custom = []
        for r in cfg.get("custom_rules", []):
            try:
                self.custom.append((r, re.compile(r["pattern"])))
            except (KeyError, re.error) as e:
                raise SystemExit(f"plumbline: invalid custom rule {r.get('id', '?')}: {e}")

    def add(self, rule: str, path: str, line: int, msg: str, snippet: str = "", raw_line: str = ""):
        if rule in self.cfg["disabled_rules"] or (raw_line and suppressed(raw_line, rule)):
            return
        sev = self.cfg["severity_overrides"].get(rule, self.catalogue[rule][1])
        self.findings.append(Finding(rule, sev, path, line, msg, snippet[:160]).finalize())

    def scan_file(self, rel: str):
        path = self.root / rel
        if not path.is_file() or matches(rel, self.cfg["exclude"]):
            return
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return
        ext = path.suffix.lower()
        lines = text.splitlines()
        code = ext in CODE_EXT
        prose = ext in PROSE_EXT
        banned = [re.compile(p, re.I) for p in self.cfg["extra_banned_phrases"]]

        for i, ln in enumerate(lines, 1):
            for rx, what in SECRET_PATTERNS:
                if rx.search(ln) and not re.search(r"(?i)example|dummy|fake|xxxx|changeme|\$\{|os\.environ|getenv", ln) \
                        and not (what == "credential assigned to a literal" and NOT_SECRET_NAME.search(ln)):
                    self.add("PL001", rel, i, f"Possible {what}. Move it to a secret store / env var.", ln, ln)
                    break
            if code:
                for rx in PLACEHOLDER_PATTERNS:
                    if rx.search(ln) and not (ext == ".py" and "abstract" in "".join(lines[max(0, i - 4):i])):
                        self.add("PL002", rel, i, "Placeholder or unfinished stub — finish it or open a tracked issue.", ln, ln)
                        break
                for rx in CHATBOT_PATTERNS:
                    if rx.search(ln):
                        self.add("PL003", rel, i, "Conversational/chatbot text pasted into source.", ln, ln)
                        break
                for rx in DEBUG_PATTERNS.get(ext, []):
                    if rx.search(ln) and not is_test(rel, self.cfg):
                        self.add("PL005", rel, i, "Debug statement left in non-test code.", ln, ln)
                sw = SWALLOW_PATTERNS.get(ext)
                if sw and sw.search(ln):
                    nxt = lines[i].strip() if i < len(lines) else ""
                    if ext != ".py" or ln.rstrip().endswith("pass") or nxt == "pass":
                        self.add("PL009", rel, i, "Exception swallowed silently — log, re-raise or handle explicitly.", ln, ln)
            if prose:
                for rx in PROSE_FILLER:
                    if rx.search(ln):
                        self.add("PL011", rel, i, "Generic AI filler phrase — say the specific thing instead.", ln, ln)
                        break
            for rx in banned:
                if rx.search(ln):
                    self.add("PL011", rel, i, f"Banned phrase ({rx.pattern}).", ln, ln)

        for r, rx in self.custom:
            if matches(rel, r.get("paths", ["*"])) and not matches(rel, r.get("exclude_paths", [])):
                for i, ln in enumerate(lines, 1):
                    if rx.search(ln):
                        self.add(r["id"], rel, i, r.get("message", r["id"]), ln, ln)
        if code:
            self._comment_ratio(rel, ext, lines)
            self._architecture(rel, ext, text, lines)
            if ext == ".py":
                self._py_imports(rel, lines)
            elif ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}:
                self._js_imports(rel, lines)
        return lines

    def _comment_ratio(self, rel, ext, lines):
        pfx = COMMENT_PREFIX.get(ext)
        if not pfx or len(lines) < 15:
            return
        comments = sum(1 for l in lines if l.strip().startswith(pfx))
        codel = sum(1 for l in lines if l.strip() and not l.strip().startswith(pfx))
        ratio = comments / max(codel, 1)
        if ratio > self.cfg["max_comment_ratio"]:
            self.add("PL004", rel, 1, f"Comment-to-code ratio {ratio:.0%} — comments should explain *why*, not narrate *what*.")

    def _architecture(self, rel, ext, text, lines):
        arch = self.arch
        if not arch or is_test(rel, self.cfg):
            return
        mod = arch.module_of(rel)
        if mod is None:
            if Path(rel).name in {"__init__.py", "index.ts", "index.js", "py.typed", "__main__.py"}:
                return  # package markers and entry points sit above modules by design
            if arch.strict_placement and arch.under_source_root(rel) and ext in {".py", ".js", ".jsx", ".ts", ".tsx",
                                                                               ".mjs", ".cjs", ".cs", ".java", ".go"}:
                self.add("PL017", rel, 1, "File is not inside any module declared in ARCHITECTURE.md. Move it into "
                         "the right module, or propose a new module via an ADR.")
            return
        if ext == ".py":
            imports = python_imports(text, rel, arch.source_roots)
        elif ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts"}:
            imports = js_imports(lines, rel)
        elif ext == ".sql":
            imports = self._dbt_refs(lines)
        else:
            return
        allowed = set(mod.may_import) | {mod.name}
        for line, pkg, cands in imports:
            raw = lines[line - 1] if 0 < line <= len(lines) else ""
            if pkg and pkg in mod.forbid_packages:
                self.add("PL013", rel, line, f"Module '{mod.name}' must not depend on '{pkg}' (forbid_packages in "
                         "ARCHITECTURE.md).", raw, raw)
                continue
            target = next((t for t in (arch.module_of(c) for c in cands if not pkg or exists_in_repo(self.root, c)) if t), None)
            if target and target.name not in allowed:
                self.add("PL013", rel, line, f"'{mod.name}' imports '{target.name}', which is not in its may_import "
                         f"list {sorted(mod.may_import) or '[]'}. Respect the boundary or change the architecture "
                         "via an ADR.", raw, raw)

    def _dbt_refs(self, lines):
        """dbt: `ref('model')` / `ref('package', 'model')` resolves to the module that owns that model's .sql file."""
        if getattr(self, "_sql_index", None) is None:
            skip = {".git", "target", "dbt_packages", "node_modules", ".venv", "venv"}
            self._sql_index = {p.stem: p.relative_to(self.root).as_posix() for p in self.root.rglob("*.sql")
                               if not skip & set(p.relative_to(self.root).parts)}
        out = []
        for i, ln in enumerate(lines, 1):
            for a, b in DBT_REF.findall(ln):
                target = self._sql_index.get(b or a)
                if target:
                    out.append((i, "", [target]))
        return out

    def governance(self):
        """Repo-level: the shared context every engineer and agent relies on must exist and be finished."""
        cfg = self.cfg
        for doc in cfg["required_docs"]:
            p = self.root / doc
            if not p.exists():
                self.add("PL014", doc, 0, f"Required shared-context file {doc} is missing.")
                continue
            text = p.read_text(errors="ignore")
            if len(text.strip()) < 150:
                self.add("PL014", doc, 1, f"{doc} is effectively empty — agents and engineers rely on it.")
            for i, ln in enumerate(text.splitlines(), 1):
                if any(m in ln for m in cfg["unfinished_markers"]):
                    self.add("PL014", doc, i, "Unfinished template section — replace it with this project's facts.",
                             ln, ln)
        co = self.root / cfg["codeowners_file"]
        if self.arch and co.exists():
            cur = co.read_text(errors="ignore")
            if CO_BEGIN in cur and merge_codeowners(cur, codeowners_block(self.arch, cfg)) != cur:
                self.add("PL014", cfg["codeowners_file"], 1, "CODEOWNERS is out of sync with module owners in "
                         "ARCHITECTURE.md. Run `make codeowners`.")
        if self.arch is None and (self.root / cfg["architecture_file"]).exists():
            self.add("PL014", cfg["architecture_file"], 0, f"Architecture is not machine-checkable: {self.arch_error}.")

    def _py_imports(self, rel, lines):
        if self._py_deps is None:
            self._py_deps = declared_python_deps_anywhere(self.root)
            self._provided = {p.lower().replace("-", "_") for p in self.cfg.get("provided_packages", [])}
            self._py_local = local_python_modules(self.root)
        if not self._py_deps:  # no manifest — can't judge
            return
        rx = re.compile(r"^\s*(?:from\s+([a-zA-Z_][\w]*)[\w.]*\s+import|import\s+([a-zA-Z_][\w]*))")
        sibling = {p.stem.lower() for p in (self.root / rel).parent.glob("*.py")}
        for i, ln in enumerate(lines, 1):
            m = rx.match(ln)
            if not m:
                continue
            mod = (m.group(1) or m.group(2)).lower()
            dist = PY_ALIASES.get(mod, mod)
            if (mod in self.stdlib or mod in self._py_local or mod in sibling or mod == "__future__"
                    or dist in self._py_deps or mod in self._py_deps or mod in self._provided
                    or any(d.startswith(dist + "_") for d in self._py_deps)):  # e.g. apache_airflow_providers_*
                continue
            self.add("PL006", rel, i, f"'{mod}' is imported but not declared in requirements/pyproject. "
                     "Verify the package exists and pin it — or remove the import.", ln, ln)

    def _js_imports(self, rel, lines):
        if self._js_deps is None:
            self._js_deps = declared_js_deps(self.root) or set()
        if not self._js_deps:
            return
        rx = re.compile(r"""(?:from\s+|require\(\s*|import\(\s*|^\s*import\s+)["']([^"'./][^"']*)["']""")
        for i, ln in enumerate(lines, 1):
            for spec in rx.findall(ln):
                spec = spec.removeprefix("node:")
                name = "/".join(spec.split("/")[:2]) if spec.startswith("@") else spec.split("/")[0]
                if name in NODE_BUILTINS or name in self._js_deps or spec.startswith(("~", "#")):
                    continue
                self.add("PL006", rel, i, f"'{name}' is imported but not in package.json. "
                         "Verify it exists on the registry (watch for typosquats) and add it explicitly.", ln, ln)

    # cross-file checks ------------------------------------------------------
    def duplicates(self, files: dict[str, list[str]], window: int = 6):
        seen: dict[str, tuple[str, int]] = {}
        for rel, lines in files.items():
            if not lines or Path(rel).suffix.lower() not in CODE_EXT - DUP_IGNORE_EXT or is_test(rel, self.cfg):
                continue
            if matches(rel, self.cfg["duplicate_exclude"]):
                continue
            norm = [re.sub(r"\s+", " ", l.strip()) for l in lines]
            reported = -window
            for i in range(len(norm) - window + 1):
                chunk = norm[i:i + window]
                if sum(1 for c in chunk if len(c) > 3) < window - 1:
                    continue
                if sum(1 for c in chunk if IMPORT_LINE.match(c)) * 2 >= window:
                    continue  # identical import blocks are normal, not copy-paste generation
                h = hashlib.md5("\n".join(chunk).encode()).hexdigest()
                if h in seen and seen[h] != (rel, i) and i - reported >= window:
                    o_rel, o_line = seen[h]
                    self.add("PL007", rel, i + 1, f"Block duplicates {o_rel}:{o_line + 1}. Extract a shared function.",
                             lines[i])
                    reported = i
                seen.setdefault(h, (rel, i))

    def change_shape(self, changed: list[str], numstat: dict[str, int]):
        cfg = self.cfg
        all_changed = changed
        changed = [f for f in changed if not matches(f, cfg["exclude"])]
        src = [f for f in changed if matches(f, cfg["require_tests_for"]) and not is_test(f, cfg)
               and Path(f).suffix.lower() in CODE_EXT]
        tests = [f for f in all_changed if is_test(f, cfg)]  # tests count even if excluded from content scans
        if src and not tests:
            self.add("PL008", src[0], 1, f"{len(src)} source file(s) changed but no tests changed. "
                     "AI-written code needs executable proof it works.")
        arch_file, adr_dir = cfg["architecture_file"], cfg["adr_dir"].rstrip("/") + "/"
        for f in changed:
            if f.startswith(adr_dir) and f.endswith(".md") and not Path(f).name.startswith("0000-"):
                body = (self.root / f).read_text(errors="ignore") if (self.root / f).exists() else ""
                if "<decision title>" in body or "YYYY-MM-DD" in body or not re.search(r"(?im)^- \*\*Status:\*\*", body):
                    self.add("PL014", f, 1, "ADR is still the template. Fill in title, date, status, context, "
                             "decision and consequences.")
        if arch_file in changed and not any(f.startswith(adr_dir) for f in changed):
            self.add("PL015", arch_file, 0, f"{arch_file} changed but no ADR was added under {adr_dir}. Architecture "
                     "is shared by every engineer and agent — record the decision and its consequences.")
        if self.arch:
            touched = sorted({m.name for f in changed if not is_test(f, cfg)
                              for m in [self.arch.module_of(f)] if m})
            if len(touched) > cfg["max_modules_per_change"]:
                self.add("PL016", "(changeset)", 0, f"Change touches {len(touched)} modules ({', '.join(touched)}). "
                         "Wide changes collide with parallel work — split by module.")
        total = sum(n for f, n in numstat.items() if not matches(f, cfg["exclude"]))
        if total > cfg["max_changed_lines"]:
            self.add("PL010", "(changeset)", 0, f"{total} lines changed (limit {cfg['max_changed_lines']}). "
                     "Large changes hide defects and defeat human review — split into reviewable PRs.")


# ---------------------------------------------------------------- file selection
def changed_files(root: Path, mode: str, base: str | None) -> tuple[list[str], dict[str, int]]:
    if mode == "staged":
        names = sh("git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", cwd=root)
        stat = sh("git", "diff", "--cached", "--numstat", cwd=root)
    else:
        rng = f"{base}...HEAD"
        names = sh("git", "diff", "--name-only", "--diff-filter=ACMR", rng, cwd=root)
        stat = sh("git", "diff", "--numstat", rng, cwd=root)
    numstat = {}
    for ln in stat.splitlines():
        parts = ln.split("\t")
        if len(parts) == 3 and parts[0].isdigit():
            numstat[parts[2]] = int(parts[0]) + int(parts[1])
    return [n for n in names.splitlines() if n], numstat


def all_files(root: Path, cfg: dict) -> list[str]:
    tracked = sh("git", "ls-files", "--cached", "--others", "--exclude-standard", cwd=root).splitlines()
    if tracked:
        return [t for t in tracked if not matches(t, cfg["exclude"])]
    out = []
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and not matches(rel, cfg["exclude"]):
            out.append(rel)
    return out


# ---------------------------------------------------------------- output
def score(findings: list[Finding]) -> int:
    return max(0, 100 - sum(SEVERITY_WEIGHT[f.severity] for f in findings))


def to_sarif(findings: list[Finding], cat: dict = RULES) -> dict:
    lvl = {"error": "error", "warn": "warning", "info": "note"}
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {"name": "plumbline", "version": VERSION, "informationUri": "https://example.com/plumbline",
                                "rules": [{"id": k, "shortDescription": {"text": v[0]}} for k, v in cat.items()]}},
            "results": [{
                "ruleId": f.rule, "level": lvl[f.severity], "message": {"text": f.message},
                "partialFingerprints": {"plumbline/v1": f.fingerprint},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": f.path if f.line else "."},
                                                    "region": {"startLine": max(f.line, 1)}}}],
            } for f in findings],
        }],
    }


def to_markdown(findings: list[Finding], s: int, passed: bool, scope: str, cat: dict = RULES) -> str:
    icon = "✅" if passed else "❌"
    out = [f"## {icon} Plumbline — score {s}/100", f"_Scope: {scope}_", ""]
    if not findings:
        out.append("No findings. Ship it.")
        return "\n".join(out)
    counts = {k: sum(1 for f in findings if f.severity == k) for k in ("error", "warn", "info")}
    out += [f"**{counts['error']} error · {counts['warn']} warn · {counts['info']} info**", "",
            "| Sev | Rule | Location | Finding |", "|---|---|---|---|"]
    for f in sorted(findings, key=lambda f: (-SEVERITY_RANK[f.severity], f.path, f.line)):
        loc = f"`{f.path}:{f.line}`" if f.line else f"`{f.path}`"
        out.append(f"| {f.severity} | {f.rule} {cat.get(f.rule, (f.rule,))[0]} | {loc} | {f.message.replace('|', '/')} |")
    out += ["", "<sub>Suppress a false positive inline with `plumbline: ignore PL00X` and a reason.</sub>"]
    return "\n".join(out)


def to_text(findings: list[Finding], s: int, passed: bool) -> str:
    out = []
    for f in sorted(findings, key=lambda f: (f.path, f.line)):
        out.append(f"{f.path}:{f.line}: [{f.severity.upper()}] {f.rule} {f.message}")
        if f.snippet:
            out.append(f"    > {f.snippet.strip()}")
    out.append(f"\nplumbline: score {s}/100 — {'PASS' if passed else 'FAIL'} ({len(findings)} finding(s))")
    return "\n".join(out)


# ---------------------------------------------------------------- commit-msg (PL012)
def check_commit_msg(path: Path, cfg: dict) -> int:
    if not cfg.get("require_ai_trailer"):
        return 0
    msg = path.read_text(errors="ignore")
    key = cfg.get("ai_trailer_key", "AI-Assisted")
    value = r"(yes|no|partial)\b" if key.lower() == "ai-assisted" else r"\S"
    if re.search(rf"(?im)^{re.escape(key)}:\s*{value}", msg) or msg.startswith(("Merge ", "Revert ")):
        return 0
    example = "AI-Assisted: yes\n    AI-Tool: claude-code" if key.lower() == "ai-assisted" else f"{key}: <tool name>"
    sys.stderr.write(f"plumbline PL012: add a provenance trailer to your commit message, e.g.\n    {example}\n")
    return 1


# ---------------------------------------------------------------- agent hooks
# Tools that only read files; their paths must not be gated as if the agent had written them.
READ_ONLY_TOOLS = {"Read", "view", "read_file", "read_many_files", "Grep", "grep", "Glob", "glob", "list_dir",
                   "file_search", "grep_search", "semantic_search"}
PATCH_FILE = re.compile(r"^\*\*\* (?:Add|Update) File: (.+)$", re.M)


def hook_files(payload: dict) -> list[Path]:
    """Files an agent tool call wrote, from Claude Code, Gemini CLI, GitHub Copilot (CLI, cloud agent, VS Code) payloads."""
    name = payload.get("tool_name") or payload.get("toolName") or ""
    if name in READ_ONLY_TOOLS:
        return []
    args = payload.get("tool_input", payload.get("toolArgs")) or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {"input": args}
    if not isinstance(args, dict):
        return []
    found: list[str] = []
    for key in ("file_path", "filePath", "path"):
        if isinstance(args.get(key), str):
            found.append(args[key])
    for item in args.get("replacements") or []:  # VS Code multi-file replace
        if isinstance(item, dict) and isinstance(item.get("filePath"), str):
            found.append(item["filePath"])
    for key in ("input", "patch"):  # apply_patch
        if isinstance(args.get(key), str):
            found += [m.strip() for m in PATCH_FILE.findall(args[key])]
    return [Path(p) for p in dict.fromkeys(found)]


# ---------------------------------------------------------------- main
def run(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="plumbline check", description="Quality gate for AI-generated changes")
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--diff", metavar="BASE", help="scan files changed vs BASE (e.g. origin/main)")
    scope.add_argument("--staged", action="store_true", help="scan staged files (pre-commit)")
    scope.add_argument("--all", action="store_true", help="scan the whole repo")
    scope.add_argument("--files", nargs="+", help="scan specific files")
    scope.add_argument("--hook", action="store_true", help="agent post-edit hook mode (reads the tool call as JSON on stdin)")
    scope.add_argument("--commit-msg", metavar="FILE", help="validate AI provenance trailer")
    scope.add_argument("--codeowners", metavar="FILE", help="write CODEOWNERS block generated from ARCHITECTURE.md")
    ap.add_argument("--format", choices=["text", "json", "sarif", "markdown"], default="text")
    ap.add_argument("--output", "-o", help="write report to file instead of stdout")
    ap.add_argument("--baseline", default=".plumbline/baseline.json", help="ignore findings recorded here")
    ap.add_argument("--write-baseline", action="store_true", help="record current findings as accepted debt")
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument("--version", action="version", version=VERSION)
    a = ap.parse_args(argv)

    root = repo_root(Path(a.root).resolve())
    cfg = load_config(root)

    if a.commit_msg:
        return check_commit_msg(Path(a.commit_msg), cfg)
    if a.codeowners:
        arch, err = Architecture.load(root, cfg)
        if not arch:
            sys.stderr.write(f"plumbline: cannot generate CODEOWNERS: {err}\n")
            return 1
        out = root / a.codeowners
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(merge_codeowners(out.read_text() if out.exists() else "", codeowners_block(arch, cfg)))
        print(f"plumbline: wrote {a.codeowners}")
        return 0

    numstat: dict[str, int] = {}
    copilot_cli = False
    if a.hook:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            return 0
        copilot_cli = "toolName" in payload
        paths = hook_files(payload)
        if not paths:
            return 0
        cwd = Path(payload.get("cwd") or Path.cwd())
        paths = [p if p.is_absolute() else cwd / p for p in paths]
        root = repo_root(Path(payload.get("cwd") or paths[0].parent).resolve())
        cfg = load_config(root)
        files = []
        for p in paths:
            try:
                files.append(p.resolve().relative_to(root).as_posix())
            except ValueError:
                continue
        if not files:
            return 0
        scope_desc = f"agent edit {', '.join(files)}"
    elif a.files:
        files = [Path(f).resolve().relative_to(root).as_posix() for f in a.files]
        scope_desc = "selected files"
    elif a.staged:
        files, numstat = changed_files(root, "staged", None)
        scope_desc = "staged changes"
    elif a.diff:
        files, numstat = changed_files(root, "diff", a.diff)
        scope_desc = f"changes vs {a.diff}"
    else:
        files = all_files(root, cfg)
        scope_desc = "whole repository"

    sc = Scanner(root, cfg)
    contents = {f: sc.scan_file(f) for f in files}
    sc.duplicates({k: v for k, v in contents.items() if v})
    if a.staged or a.diff:
        sc.change_shape(files, numstat)
    if a.diff or a.all or not (a.staged or a.files or a.hook):
        sc.governance()

    findings = sc.findings
    base_path = root / a.baseline
    # shared-context and architecture-change findings are never debt: they must be fixed, not baselined
    never_baseline = {"PL014", "PL015"}
    if a.write_baseline:
        debt = [f for f in findings if f.rule not in never_baseline]
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(json.dumps(sorted({f.fingerprint for f in debt}), indent=1))
        print(f"plumbline: baselined {len(debt)} finding(s) -> {base_path.relative_to(root)}")
        return 0
    if base_path.exists():
        known = set(json.loads(base_path.read_text() or "[]"))
        findings = [f for f in findings if f.fingerprint not in known or f.rule in never_baseline]

    s = score(findings)
    threshold = cfg["fail_on"]
    failed = threshold != "never" and any(SEVERITY_RANK[f.severity] >= SEVERITY_RANK[threshold] for f in findings)
    failed = failed or s < int(cfg.get("min_score", 0))

    if a.hook:
        if findings:
            msg = ("Plumbline found issues in the file you just wrote. Fix them before continuing:\n"
                   + to_text(findings, s, not failed) + "\n")
            if copilot_cli:  # Copilot CLI / cloud agent: only stdout additionalContext reaches the model
                print(json.dumps({"additionalContext": msg}))
                return 0
            sys.stderr.write(msg)
            return 2 if failed else 0
        return 0

    if a.format == "json":
        body = json.dumps({"version": VERSION, "scope": scope_desc, "score": s, "passed": not failed,
                           "files_scanned": len(files), "findings": [asdict(f) for f in findings]}, indent=2)
    elif a.format == "sarif":
        body = json.dumps(to_sarif(findings, sc.catalogue), indent=2)
    elif a.format == "markdown":
        body = to_markdown(findings, s, not failed, scope_desc, sc.catalogue)
    else:
        body = to_text(findings, s, not failed)

    if a.output:
        Path(a.output).write_text(body + "\n")
    else:
        print(body)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
