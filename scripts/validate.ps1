$ErrorActionPreference = 'Stop'
$requiredFiles = @('README.md','AGENTS.md','CONTRIBUTING.md','ARCHITECTURE.md','SECURITY.md','AI_POLICY.md','DATA_POLICY.md','PROJECT.yaml','Makefile','plumbline.toml','.plumbline/plumbline.py','.plumbline/guard.py')
$requiredDirs = @('.github','docs','src','tests','ai','infrastructure','config','policies')
foreach ($file in $requiredFiles) { if (-not (Test-Path $file -PathType Leaf)) { throw "Missing required file: $file" } }
foreach ($directory in $requiredDirs) { if (-not (Test-Path $directory -PathType Container)) { throw "Missing required directory: $directory" } }
Write-Output 'Repository validation passed.'
