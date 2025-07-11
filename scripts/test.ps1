param(
    [Parameter(Position=0, Mandatory=$false)]
    [string]$TestPath = "app/tests"
)

# Get the project root directory
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Path to the virtual environment's Python executable
$venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"

# Check if virtual environment exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found. Creating one..."
    python -m venv venv
    
    # Activate virtual environment and install requirements
    Write-Host "Installing requirements..."
    & $venvPython -m pip install -r requirements.txt
}

# Check if Chrome WebDriver is installed
try {
    $chromeDriver = Get-Command chromedriver -ErrorAction Stop
    Write-Host "Chrome WebDriver found at: $($chromeDriver.Source)"
} catch {
    Write-Host "Chrome WebDriver not found. Installing..."
    & $venvPython -m pip install webdriver-manager
    & $venvPython -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
}

# Run the tests
Write-Host "Running tests from: $TestPath"
& $venvPython -m pytest $TestPath -v 