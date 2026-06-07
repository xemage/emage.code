# Regenerate platform mirrors from canonical knowledge.
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here '..')
node "$here/sync.mjs" --root $root @args
