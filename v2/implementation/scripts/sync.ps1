# Cross-platform PowerShell wrapper for emage.code sync.
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
node "$here/sync.mjs" @args
