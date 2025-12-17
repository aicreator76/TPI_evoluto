Set-Location "E:\CLONAZIONE\tpi_evoluto"

if(-not (Test-Path "E:\CLONAZIONE\tpi_evoluto\.git")){ Write-Host "FAIL: non sei nel repo"; exit 1 }

$ts=(Get-Date -Format "yyyy-MM-dd_HHmmss")
$bk="E:\CLONAZIONE\BACKUP_EMERGENZA\DEMO_BEFORE_COMMIT_$ts"
New-Item -ItemType Directory -Force -Path "$bk\app\routers","$bk\app\data","$bk\scripts\CESARE" | Out-Null

Copy-Item "E:\CLONAZIONE\tpi_evoluto\app\main.py" "$bk\app\main.py" -Force -ErrorAction SilentlyContinue
Copy-Item "E:\CLONAZIONE\tpi_evoluto\app\routers\demo_real.py" "$bk\app\routers\demo_real.py" -Force -ErrorAction SilentlyContinue
Copy-Item "E:\CLONAZIONE\tpi_evoluto\app\data\demo_products.json" "$bk\app\data\demo_products.json" -Force -ErrorAction SilentlyContinue

# 1) pre-commit finché non smette di toccare file (2 giri bastano quasi sempre)
if(Get-Command pre-commit -ErrorAction SilentlyContinue){
  pre-commit run -a
  pre-commit run -a
}

# 2) stage (FORZA il json ignorato)
git add "app/main.py" "app/routers/demo_real.py"
git add -f "app/data/demo_products.json"

if(Test-Path "E:\CLONAZIONE\tpi_evoluto\scripts\CESARE\ops_api_8010_2025-12-17.ps1"){
  git add "scripts\CESARE\ops_api_8010_2025-12-17.ps1"
}

# 3) commit + push
git commit -m "demo api: demo_real mount-safe + ops 8010 (clean)"
if($LASTEXITCODE -ne 0){
  Write-Host "COMMIT FAIL -> rieseguo pre-commit e riprovo"
  if(Get-Command pre-commit -ErrorAction SilentlyContinue){
    pre-commit run -a
    pre-commit run -a
  }
  git add "app/main.py" "app/routers/demo_real.py"
  git add -f "app/data/demo_products.json"
  if(Test-Path "E:\CLONAZIONE\tpi_evoluto\scripts\CESARE\ops_api_8010_2025-12-17.ps1"){
    git add "scripts\CESARE\ops_api_8010_2025-12-17.ps1"
  }
  git commit -m "demo api: demo_real mount-safe + ops 8010 (clean)"
}

git push

Write-Host "OK BACKUP=$bk"
git status
