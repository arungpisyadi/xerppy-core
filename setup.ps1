<#
.SYNOPSIS
    Project Setup Script for xerppy-core
.DESCRIPTION
    This script sets up and runs the xerppy-core project on Windows.
    Supports PowerShell 7+
.PARAMETER Command
    The command to execute (setup, setup-backend, setup-frontend, start-backend, start-frontend, start-all, help)
.EXAMPLE
    .\setup.ps1 setup
    .\setup.ps1 start-backend
#>

param(
    [string]$Command = "setup"
)

# ============================================================================
# Configuration
# ============================================================================

$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$PythonVersionFile = Join-Path $BackendDir ".python-version"

# ============================================================================
# Utility Functions
# ============================================================================

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Test-CommandExists {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# ============================================================================
# Python Setup Functions
# ============================================================================

function Get-RequiredPythonVersion {
    if (Test-Path $PythonVersionFile) {
        Get-Content $PythonVersionFile | Where-Object { $_ -match '\S' } | ForEach-Object { $_.Trim() }
    }
    else {
        Write-Warning "Python version file not found at $PythonVersionFile"
        return "3.11"
    }
}

function Get-InstalledPythonVersion {
    try {
        $pythonCmd = if (Test-CommandExists "python") { "python" } elseif (Test-CommandExists "py") { "py" } else { $null }
        if ($pythonCmd) {
            $version = & $pythonCmd --version 2>&1
            if ($version -match 'Python\s+(\d+\.\d+)') {
                return $matches[1]
            }
        }
    }
    catch {
        return $null
    }
    return $null
}

function Test-PythonVersion {
    param([string]$RequiredVersion)
    
    $installedVersion = Get-InstalledPythonVersion
    
    if (-not $installedVersion) {
        Write-Error "Python is not installed"
        return $false
    }
    
    if ($installedVersion -eq $RequiredVersion) {
        Write-Success "Python $installedVersion is installed (required: $requiredVersion)"
        return $true
    }
    else {
        Write-Warning "Python $installedVersion is installed but $requiredVersion is required"
        return $false
    }
}

function Install-Python {
    param([string]$Version)
    
    Write-Step "Installing Python $Version on Windows..."
    
    # Download Python installer
    $pythonUrl = "https://www.python.org/ftp/python/$Version/python-$Version-amd64.exe"
    $installerPath = Join-Path $env:TEMP "python-installer.exe"
    
    Write-Info "Downloading Python $Version..."
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Info "Running Python installer..."
        # Run installer silently
        $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Success "Python $version installation initiated"
            
            # Refresh environment variables
            $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
            
            return $true
        }
        else {
            Write-Error "Python installation failed with exit code $($process.ExitCode)"
            return $false
        }
    }
    catch {
        Write-Error "Failed to download or run Python installer: $_"
        Write-Info "Please download Python $Version manually from https://python.org"
        return $false
    }
    finally {
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
}

# ============================================================================
# Node.js Setup Functions
# ============================================================================

function Get-InstalledNodeVersion {
    try {
        if (Test-CommandExists "node") {
            $version = node --version
            if ($version -match 'v(\d+\.\d+)') {
                return $matches[1]
            }
        }
    }
    catch {
        return $null
    }
    return $null
}

function Test-NodeVersion {
    if (-not (Test-CommandExists "node")) {
        Write-Error "Node.js is not installed"
        return $false
    }
    
    $installedVersion = Get-InstalledNodeVersion
    if ($installedVersion) {
        Write-Success "Node.js $installedVersion is installed"
        return $true
    }
    return $true
}

function Install-NodeJS {
    Write-Step "Installing Node.js on Windows..."
    
    # Download Node.js installer (LTS version)
    $nodeUrl = "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi"
    $installerPath = Join-Path $env:TEMP "node-installer.msi"
    
    Write-Info "Downloading Node.js..."
    try {
        Invoke-WebRequest -Uri $nodeUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Info "Running Node.js installer..."
        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$installerPath`" /quiet" -Wait -PassThru
        
        if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 3010) {
            Write-Success "Node.js installation initiated"
            
            # Refresh environment variables
            $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
            
            return $true
        }
        else {
            Write-Error "Node.js installation failed with exit code $($process.ExitCode)"
            return $false
        }
    }
    catch {
        Write-Error "Failed to download or run Node.js installer: $_"
        Write-Info "Please download Node.js manually from https://nodejs.org"
        return $false
    }
    finally {
        if (Test-Path $installerPath) {
            Remove-Item $installerPath -Force
        }
    }
}

# ============================================================================
# Backend Setup Functions
# ============================================================================

function Setup-Backend {
    Write-Step "Setting up backend..."
    
    if (-not (Test-Path $BackendDir)) {
        Write-Error "Backend directory not found at $BackendDir"
        return $false
    }
    
    # Check and install Python if needed
    $requiredPythonVersion = Get-RequiredPythonVersion
    
    if (-not (Test-PythonVersion -RequiredVersion $requiredPythonVersion)) {
        if (-not (Install-Python -Version $requiredPythonVersion)) {
            Write-Error "Failed to install Python $requiredPythonVersion"
            return $false
        }
    }
    
    # Check if uv is installed
    if (-not (Test-CommandExists "uv")) {
        Write-Step "Installing uv..."
        try {
            Invoke-WebRequest -Uri "https://astral.sh/uv/install.ps1" -UseBasicParsing | Invoke-Expression
            # Refresh environment variables
            $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
        }
        catch {
            Write-Error "Failed to install uv: $_"
            return $false
        }
    }
    
    # Install dependencies
    Write-Step "Installing backend dependencies with uv sync..."
    Push-Location $BackendDir
    try {
        $uvResult = uv sync
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install backend dependencies"
            return $false
        }
        Write-Success "Backend dependencies installed"
        
        # Create admin user
        Write-Step "Creating admin user..."
        $adminResult = uv run python -m app.scripts.create_admin interactive
        
        Write-Success "Backend setup complete"
        return $true
    }
    catch {
        Write-Error "Backend setup failed: $_"
        return $false
    }
    finally {
        Pop-Location
    }
}

function Start-Backend {
    Write-Step "Starting backend development server..."
    Push-Location $BackendDir
    try {
        uv run python main.py
    }
    finally {
        Pop-Location
    }
}

# ============================================================================
# Frontend Setup Functions
# ============================================================================

function Setup-Frontend {
    Write-Step "Setting up frontend..."
    
    if (-not (Test-Path $FrontendDir)) {
        Write-Error "Frontend directory not found at $FrontendDir"
        return $false
    }
    
    # Check and install Node.js if needed
    if (-not (Test-NodeVersion)) {
        if (-not (Install-NodeJS)) {
            Write-Error "Failed to install Node.js"
            return $false
        }
    }
    
    # Install dependencies
    Write-Step "Installing frontend dependencies with npm..."
    Push-Location $FrontendDir
    try {
        $npmResult = npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install frontend dependencies"
            return $false
        }
        Write-Success "Frontend dependencies installed"
        return $true
    }
    catch {
        Write-Error "Frontend setup failed: $_"
        return $false
    }
    finally {
        Pop-Location
    }
}

function Start-Frontend {
    Write-Step "Starting frontend development server..."
    Push-Location $FrontendDir
    try {
        npm run dev
    }
    finally {
        Pop-Location
    }
}

# ============================================================================
# Main Setup Function
# ============================================================================

function Setup-All {
    Write-Host "========================================" -ForegroundColor White
    Write-Host "  xerppy-core Project Setup" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor White
    Write-Host ""
    
    Write-Info "PowerShell Version: $($PSVersionTable.PSVersion)"
    Write-Host ""
    
    # Setup backend
    if (-not (Setup-Backend)) {
        Write-Error "Backend setup failed"
        exit 1
    }
    
    Write-Host ""
    
    # Setup frontend
    if (-not (Setup-Frontend)) {
        Write-Error "Frontend setup failed"
        exit 1
    }
    
    Write-Host ""
    Write-Success "All setup complete!"
    Write-Host ""
    Write-Host "To start the development servers:" -ForegroundColor White
    Write-Host "  1. In one terminal: .\setup.ps1 start-backend"
    Write-Host "  2. In another terminal: .\setup.ps1 start-frontend"
    Write-Host ""
    Write-Host "Or start both in background:" -ForegroundColor White
    Write-Host "  .\setup.ps1 start-all"
}

function Start-AllServices {
    Write-Step "Starting all services..."
    
    # Start backend in background
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:BackendDir
        uv run python main.py
    }
    
    Write-Info "Backend started (Job ID: $($backendJob.Id))"
    
    # Start frontend in background
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:FrontendDir
        npm run dev
    }
    
    Write-Info "Frontend started (Job ID: $($frontendJob.Id))"
    Write-Info "Press Ctrl+C to stop all services"
    
    # Wait for both jobs
    try {
        Wait-Job -Job $backendJob, $frontendJob
    }
    catch {
        Write-Warning "Stopping all services..."
        Stop-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    }
}

function Show-Help {
    Write-Host "Usage: .\setup.ps1 [command]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor White
    Write-Host "  setup         Set up the entire project (backend + frontend)"
    Write-Host "  setup-backend Set up only the backend"
    Write-Host "  setup-frontend Set up only the frontend"
    Write-Host "  start-backend Start the backend development server"
    Write-Host "  start-frontend Start the frontend development server"
    Write-Host "  start-all     Start both backend and frontend servers"
    Write-Host "  help          Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\setup.ps1 setup"
    Write-Host "  .\setup.ps1 start-backend"
    Write-Host "  .\setup.ps1 start-frontend"
}

# ============================================================================
# Script Entry Point
# ============================================================================

switch ($Command.ToLower()) {
    "setup" {
        Setup-All
    }
    "setup-backend" {
        Setup-Backend
    }
    "setup-frontend" {
        Setup-Frontend
    }
    "start-backend" {
        Start-Backend
    }
    "start-frontend" {
        Start-Frontend
    }
    "start-all" {
        Start-AllServices
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
}
