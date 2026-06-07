# Regenerate platform mirrors from canonical knowledge (v3 sync engine).
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here '..')
node "$here/sync-v3.mjs" --root $root @args
