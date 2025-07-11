# Get the project root directory
$projectRoot = $PSScriptRoot

# Create the custom commands for this session
function py {
    param(
        [Parameter(Position=0)]
        [string]$Command,
        
        [Parameter(Position=1, ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )

    # Path to the virtual environment's Python executable
    $venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"

    if ($Command -eq "run") {
        $scriptPath = Join-Path $projectRoot "scripts\run.ps1"
        & $scriptPath $Arguments
    }
    elseif ($Command -eq "install") {
        # Check if virtual environment exists
        if (-not (Test-Path $venvPython)) {
            Write-Host "Virtual environment not found. Creating one..."
            python -m venv venv
        }
        
        if ($Arguments.Count -eq 0) {
            Write-Host "Installing requirements from requirements.txt..."
            & $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")
        } else {
            Write-Host "Installing package: $Arguments"
            & $venvPython -m pip install $Arguments
        }
    }
    elseif ($Command -eq "test") {
        Write-Host "Running tests..."
        & $venvPython -m pytest $Arguments
    }
    elseif ($Command -eq "start") {
        Write-Host "Starting the application in debug mode..."

        # Ensure the virtual environment exists
        if (-not (Test-Path $venvPython)) {
            Write-Host "Virtual environment not found. Creating one..."
            python -m venv venv
        }
        # Activate the virtual environment
        Write-Host "Activating the virtual environment..."
        . (Join-Path $projectRoot "venv\Scripts\Activate.ps1")

        # Ensure Flask is installed
        $flaskInstalled = $true
        try {
            & $venvPython -c "import flask" > $null 2>&1
        } catch {
            $flaskInstalled = $false
        }
        if (-not $flaskInstalled) {
            Write-Host "Flask not found in venv. Installing Python dependencies..."
            & $venvPython -m pip install --upgrade pip
            & $venvPython -m pip install -r (Join-Path $projectRoot "requirements.txt")
            try {
                & $venvPython -c "import flask" > $null 2>&1
                $flaskInstalled = $true
            } catch {
                $flaskInstalled = $false
            }
        }

        # Check if Tailwind CLI is available
        $tailwindCheck = npx tailwindcss --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Tailwind CSS not found. Running npm install..."
            npm install
        }
        
        # Only rebuild Tailwind CSS if needed
        $cssOutput = Join-Path $projectRoot "app/static/src/input.css"
        $tailwindConfig = Join-Path $projectRoot "tailwind.config.js"
        $jsFiles = Get-ChildItem -Path (Join-Path $projectRoot "app/static/js/") -Recurse -Include *.js
        $templateFiles = Get-ChildItem -Path (Join-Path $projectRoot "app/templates/") -Recurse -Include *.html
        $rebuildNeeded = $false
        if (-not (Test-Path $cssOutput)) {
            $rebuildNeeded = $true
        } else {
            $cssTime = (Get-Item $cssOutput).LastWriteTime
            $allSources = @($tailwindConfig) + $jsFiles.FullName + $templateFiles.FullName
            foreach ($src in $allSources) {
                if ((Get-Item $src).LastWriteTime -gt $cssTime) {
                    $rebuildNeeded = $true
                    break
                }
            }
        }
        if ($rebuildNeeded) {
            Write-Host "Rebuilding Tailwind CSS..."
            npm run build:prod
        } else {
            Write-Host "Tailwind CSS is up to date. Skipping rebuild."
        }
        
        # Set environment variables
        $env:FLASK_APP = "app"
        $env:FLASK_DEBUG = "1"
        # Run the Flask application
        & $venvPython -m flask run
    }
    elseif ($Command -eq "clean") {
        Write-Host "Cleaning Python cache files..."
        Get-ChildItem -Path $projectRoot -Include "__pycache__", "*.pyc" -Recurse | Remove-Item -Force -Recurse
        Write-Host "Clean complete!"
    }
    elseif ($Command -eq "update") {
        Write-Host "Updating pip and all packages..."
        & $venvPython -m pip install --upgrade pip
        & $venvPython -m pip list --outdated --format=freeze | ForEach-Object { $_ -replace '==', '>=' } | & $venvPython -m pip install -r /dev/stdin
        Write-Host "Update complete!"
    }
    elseif ($Command -eq "help") {
        Write-Host "Available commands:"
        Write-Host "  py run <python_command>    - Run a Python command in the virtual environment"
        Write-Host "  py install [package]       - Install requirements.txt or specific package"
        Write-Host "  py test [options]         - Run tests with pytest"
        Write-Host "  py start                  - Start the application in debug mode"
        Write-Host "  py clean                  - Clean Python cache files"
        Write-Host "  py update                 - Update pip and all packages"
        Write-Host "  py help                   - Show this help message"
    }
    else {
        Write-Host "Unknown command: $Command"
        Write-Host "Use 'py help' to see available commands"
    }
}

Write-Host "Project commands have been set up for this session!"
Write-Host "You can now use commands like:"
Write-Host "  py install requests"
Write-Host "  py test"
Write-Host "  py start"
Write-Host "  py clean"
Write-Host "  py update"
Write-Host "  py help" 
