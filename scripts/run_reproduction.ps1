param(
    [string]$Python = '.venv/reproduction/Scripts/python.exe',
    [ValidateSet('Agent2','Consolidated')][string]$Scope = 'Agent2'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    function Invoke-CheckedPython {
        param([string[]]$Arguments)
        & $Python @Arguments
        if ($LASTEXITCODE -ne 0) { throw "Python failed ($LASTEXITCODE): $Arguments" }
    }
    if ($Scope -eq 'Consolidated') {
        foreach ($requiredPath in @('tests/test_remote_sensing_grid.py','tests/agent3','scripts/run_agent3_pipeline.py')) {
            if (-not (Test-Path -LiteralPath $requiredPath)) { throw "IN-01 candidate incomplete: $requiredPath absent. Consolidated verification NOT TESTED." }
        }
        Invoke-CheckedPython -Arguments @('scripts/run_rc1.py')
        return
    }
    Invoke-CheckedPython -Arguments @('-m','pip','check')
    # Boundary/grid, source masks, frozen OSM graph and export identities are
    # verified before derived outputs; this is the offline/frozen-input lane.
    Invoke-CheckedPython -Arguments @('scripts/agent2_freeze_inputs.py')
    $commonArgs = @('--population','data/raw/worldpop/idn_pop_2024.tif')
    Invoke-CheckedPython -Arguments (@('scripts/aggregate_demographics.py') + $commonArgs + @(
        '--pop-child','data/raw/worldpop/age/jakarta_child_2024.tif',
        '--pop-elderly','data/raw/worldpop/age/jakarta_elderly_2024.tif',
        '--support-version','agent2-DM-01-v1-original-masks',
        '--output-dir','outputs/qa/remediation_agent2/original_masks',
        '--qa-dir','outputs/qa/remediation_agent2/original_masks'))
    Invoke-CheckedPython -Arguments (@('scripts/aggregate_demographics.py') + $commonArgs + @(
        '--pop-child','data/raw/worldpop/age_buffered/jakarta_child_2024_buffered.tif',
        '--pop-elderly','data/raw/worldpop/age_buffered/jakarta_elderly_2024_buffered.tif',
        '--support-version','agent2-DM-01-v1-buffered-age'))
    Invoke-CheckedPython -Arguments @('scripts/07_integrate_spatial.py',
        '--demographics','data/processed/demographic_features_corrected.csv',
        '--support','data/processed/demographic_support.csv')
    Invoke-CheckedPython -Arguments @('scripts/agent2_park_evidence.py')
    Invoke-CheckedPython -Arguments @('scripts/agent2_connector_remediation.py')
    Invoke-CheckedPython -Arguments @('scripts/agent2_remediation_effects.py')
    Invoke-CheckedPython -Arguments @('scripts/agent2_integration_manifest.py')
    Invoke-CheckedPython -Arguments @('-m','pytest','-q','-p','no:cacheprovider',
        'tests/test_demographic_support.py','tests/test_agent2_remediation.py','tests/test_agent2_gis.py','tests/test_walking_pipeline.py',
        '--junitxml=outputs/qa/remediation_agent2/fresh_environment_tests.xml')
    if ($Scope -eq 'Consolidated') {
        Invoke-CheckedPython -Arguments @('-m','pytest','-q','-p','no:cacheprovider','tests/test_remote_sensing_grid.py','tests/test_agent2_gis.py','tests/test_walking_pipeline.py','tests/agent3')
        Invoke-CheckedPython -Arguments @('scripts/run_agent3_pipeline.py','--status')
        Invoke-CheckedPython -Arguments @('scripts/run_agent3_pipeline.py')
        Invoke-CheckedPython -Arguments @('scripts/run_agent3_pipeline.py','--p2-only')
    }
} finally { Pop-Location }
