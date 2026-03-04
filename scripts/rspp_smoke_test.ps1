# Script: RSPP Smoke Test for TPI_evoluto
#
# Questo script esegue una serie di test di “smoke” sugli endpoint di staging
# dell’applicazione TPI_evoluto. Per ogni endpoint testato verifica lo status
# HTTP, analizza i contenuti JSON o CSV e produce una tabella finale con i
# risultati. Utilizzare questo script per verificare rapidamente il corretto
# funzionamento del servizio da parte di un tecnico o del RSPP.

param()

# Base URL dello staging
$baseUrl = "https://tpi-evoluto-staging.onrender.com"

# Collezione per i risultati.  Usando lo scope "script" assicuriamo che le funzioni
# modifichino la variabile definita a livello di script anziché creare variabili locali.
$script:results = @()

function Add-Result {
    param(
        [string]$Test,
        [string]$Result
    )
    # Aggiorna la collezione nello scope dello script
    $script:results += [PSCustomObject]@{ Test = $Test; Result = $Result }
}

# Funzione generica per eseguire un test su un endpoint
function Invoke-Test {
    param(
        [string]$Name,
        [string]$Path,
        [scriptblock]$Validate
    )
    $url = "$baseUrl$Path"
    try {
        # Effettua la richiesta HTTP; -UseBasicParsing per compatibilità su sistemi senza IE
        $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec 60
        $status = $response.StatusCode
        if ($status -ne 200) {
            Add-Result -Test $Name -Result ("FAIL (status {0})" -f $status)
            return
        }
        $valid = $false
        try {
            $valid = & $Validate $response
        } catch {
            $valid = $false
        }
        if ($valid) {
            Add-Result -Test $Name -Result "PASS"
        } else {
            Add-Result -Test $Name -Result "FAIL (validation)"
        }
    } catch {
        Add-Result -Test $Name -Result ("FAIL (" + $_.Exception.Message + ")")
    }
}

# Test: /healthz
Invoke-Test -Name "healthz" -Path "/healthz" -Validate {
    param($resp)
    # Nessuna validazione specifica sul corpo; ritorna true se arriva qui
    return $true
}

# Test: /version
Invoke-Test -Name "version" -Path "/version" -Validate {
    param($resp)
    try {
        $json = $resp.Content | ConvertFrom-Json
    } catch {
        return $false
    }
    # Controlla che esista la proprietà "version" o "tag"
    return ($null -ne $json.version -and $json.version.ToString().Length -gt 0) -or ($null -ne $json.tag -and $json.tag.ToString().Length -gt 0)
}

# Test: /openapi.json
Invoke-Test -Name "openapi.json" -Path "/openapi.json" -Validate {
    param($resp)
    try {
        $json = $resp.Content | ConvertFrom-Json
    } catch {
        return $false
    }
    # Verifica che ci sia la chiave "openapi" e che info sia presente
    return ($null -ne $json.openapi -and $null -ne $json.info)
}

# Test: /api/dpi/listino
Invoke-Test -Name "dpi listino" -Path "/api/dpi/listino" -Validate {
    param($resp)
    try {
        $json = $resp.Content | ConvertFrom-Json
    } catch {
        return $false
    }
    # Valida che ci sia un array items e che total sia numerico
    return ($null -ne $json.items -and $json.items -is [System.Collections.IEnumerable]) -and ($json.total -ge 0)
}

# Test: /api/accessori/listino
Invoke-Test -Name "accessori listino" -Path "/api/accessori/listino" -Validate {
    param($resp)
    try {
        $json = $resp.Content | ConvertFrom-Json
    } catch {
        return $false
    }
    return ($null -ne $json.items -and $json.items -is [System.Collections.IEnumerable]) -and ($json.total -ge 0)
}

# Test: /api/accessori/overview
Invoke-Test -Name "accessori overview" -Path "/api/accessori/overview" -Validate {
    param($resp)
    try {
        $json = $resp.Content | ConvertFrom-Json
    } catch {
        return $false
    }
    return ($null -ne $json.source_db) -and ($null -ne $json.summary)
}

# Test: /api/accessori/famiglie
Invoke-Test -Name "accessori famiglie" -Path "/api/accessori/famiglie" -Validate {
    param($resp)
    try {
        $arr = $resp.Content | ConvertFrom-Json
    } catch {
        return $false
    }
    # Deve essere un array di almeno un elemento, oppure zero se nessuna famiglia
    return ($arr -is [System.Collections.IEnumerable])
}

# Test: /api/dpi/csv/template (CSV)
Invoke-Test -Name "dpi csv template" -Path "/api/dpi/csv/template" -Validate {
    param($resp)
    # Verifica il content-type
    $ct = $resp.Headers["Content-Type"]
    if ($ct) {
        return $ct -like "text/csv*"
    }
    return $false
}

# Stampa la tabella dei risultati
Write-Host "TEST`t`tRESULT"
foreach ($r in $results) {
    # format: nome test a sinistra, risultato a destra
    Write-Host ("{0,-25} {1}" -f $r.Test, $r.Result)
}

# Riepilogo finale
$totalTests = $results.Count
$passedTests = ($results | Where-Object { $_.Result -like "PASS*" }).Count
$failedTests = ($results | Where-Object { $_.Result -like "FAIL*" }).Count

Write-Host ""
Write-Host "TOTAL TESTS:`t$($totalTests)"
Write-Host "PASSED:`t`t$($passedTests)"
Write-Host "FAILED:`t`t$($failedTests)"
