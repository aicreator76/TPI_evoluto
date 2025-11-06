[CmdletBinding()]
param([int]$Limit=10)
gh run list --status failure --limit $Limit --json databaseId --jq '.[].databaseId' | ForEach-Object { gh run rerun $_ }
