param(
    [Parameter(Position=0, Mandatory=$true)]
    [string]$Command
)

# Get the project root directory
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Path to the virtual environment's Python executable
$venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"

# Check if virtual environment exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found. Creating one..."
    python -m venv venv
}

# Run the command using the virtual environment's Python
& $venvPython $Command 