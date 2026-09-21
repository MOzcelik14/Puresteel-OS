$ErrorActionPreference = 'Stop'

$BootstrapUrl = 'https://raw.githubusercontent.com/MOzcelik14/Puresteel-OS/main/bootstrap.sh'
$TargetDistro = 'Debian'

function Step([string]$Message) {
    Write-Host "`n[Puresteel] $Message" -ForegroundColor Cyan
}

function Stop-WithMessage([string]$Message) {
    Write-Host "`n[Puresteel] $Message" -ForegroundColor Red
    exit 1
}

Step 'Windows Plasma 6 ISO builder'

if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    Step 'WSL is not enabled. Windows will ask for administrator permission.'
    Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
        '-NoProfile',
        '-Command',
        "wsl --install -d $TargetDistro"
    )

    Write-Host "`nWSL installation was started." -ForegroundColor Yellow
    Write-Host 'If Windows asks you to restart, restart the PC and run the same Puresteel command again.'
    exit 0
}

$Distros = @(& wsl.exe -l -q 2>$null) | ForEach-Object { ($_ -replace "`0", '').Trim() } | Where-Object { $_ }

$Distro = $null
if ($Distros -contains $TargetDistro) {
    $Distro = $TargetDistro
} elseif ($Distros.Count -gt 0) {
    $Preferred = $Distros | Where-Object { $_ -match 'Debian|Ubuntu' } | Select-Object -First 1
    if ($Preferred) { $Distro = $Preferred }
}

if (-not $Distro) {
    Step 'No Debian/Ubuntu WSL distribution was found. Installing Debian.'
    Start-Process powershell.exe -Verb RunAs -Wait -ArgumentList @(
        '-NoProfile',
        '-Command',
        "wsl --install -d $TargetDistro"
    )

    Write-Host "`nDebian installation was started." -ForegroundColor Yellow
    Write-Host 'Open Debian once if Windows asks you to create a Linux user, then run the same Puresteel command again.'
    exit 0
}

Step "Using WSL distribution: $Distro"

try {
    & wsl.exe --set-version $Distro 2 2>$null | Out-Null
} catch {
    Write-Host 'Could not force WSL2 automatically; continuing with the existing WSL configuration.' -ForegroundColor Yellow
}

$OutputWindows = (Get-Location).Path
$OutputWsl = (& wsl.exe -d $Distro -- wslpath -a $OutputWindows).Trim()
if (-not $OutputWsl) {
    Stop-WithMessage 'Could not translate the current Windows folder into a WSL path.'
}

$DriveName = [System.IO.Path]::GetPathRoot($OutputWindows).TrimEnd('\').TrimEnd(':')
$Drive = Get-PSDrive -Name $DriveName -ErrorAction SilentlyContinue
if ($Drive -and $Drive.Free -lt 35GB) {
    Stop-WithMessage 'At least 35 GB of free space is recommended on the current drive.'
}

Step 'Preparing the Linux build environment'
& wsl.exe -d $Distro -u root -- bash -lc 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y sudo ca-certificates'
if ($LASTEXITCODE -ne 0) {
    Stop-WithMessage 'Could not prepare the WSL environment.'
}

$TempScript = Join-Path $env:TEMP 'puresteel-bootstrap.sh'
Step 'Downloading the Puresteel builder'
Invoke-WebRequest -UseBasicParsing -Uri $BootstrapUrl -OutFile $TempScript

$TempScriptWsl = (& wsl.exe -d $Distro -- wslpath -a $TempScript).Trim()
$EscapedOutput = $OutputWsl.Replace("'", "'\''")
$EscapedScript = $TempScriptWsl.Replace("'", "'\''")

Step 'Building Puresteel inside WSL2'
Write-Host "The ISO will be copied to: $OutputWindows" -ForegroundColor DarkGray
Write-Host 'The Linux build may ask for your WSL user password for sudo.' -ForegroundColor DarkGray

& wsl.exe -d $Distro -- bash -lc "cd '$EscapedOutput' && bash '$EscapedScript' --build
if ($LASTEXITCODE -ne 0) {
    Stop-WithMessage 'The Puresteel build failed. Review the output above for the first error.'
}

Step 'Done'
Write-Host "Check $OutputWindows for Puresteel-Plasma-amd64.iso and its SHA256 file." -ForegroundColor Green
