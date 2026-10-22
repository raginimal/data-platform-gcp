#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

mkdir -p dist
commit_sha="${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || printf 'local')}"
version="${PROJECT_VERSION:-${GITHUB_REF_NAME:-0.0.0-dev}}"
version="${version//\//-}"
repository="${GITHUB_REPOSITORY:-local/ai-delivery-foundation}"
short_sha="${commit_sha:0:12}"
artifact="dist/project-template-${version}-${short_sha}.tar.gz"

rm -f dist/project-template-*.tar.gz dist/artifact-manifest.json dist/artifact.sha256

tar -czf "$artifact" --exclude=.git --exclude=dist .
digest="$(sha256sum "$artifact" | awk '{print $1}')"
python3 - "$artifact" "$digest" "$commit_sha" "$version" "$repository" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

artifact = Path(sys.argv[1])
manifest = {
    "artifact": artifact.name,
    "sha256": sys.argv[2],
    "commit_sha": sys.argv[3],
    "version": sys.argv[4],
    "repository": sys.argv[5],
    "workflow_run": os.environ.get("GITHUB_RUN_ID", "local"),
    "built_at": datetime.now(timezone.utc).isoformat(),
}
Path("dist/artifact-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
Path("dist/artifact.sha256").write_text(f"{manifest['sha256']}  {artifact.name}\n")
PY

echo "Built immutable artifact: $artifact"
echo "Artifact digest: $digest"
