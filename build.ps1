# Build script for mail_generator.exe

Write-Host "Building mail_generator.exe..." -ForegroundColor Green

# Check if pyinstaller is installed
$checkPyinstaller = python -c "import pyinstaller" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing pyinstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
}

# Create build command
$buildCommand = "python -m PyInstaller --noconfirm --onefile --windowed " +
                "--name `"TempMail`" " +
                "--hidden-import `"ttkbootstrap`" " +
                "--hidden-import `"webdriver_manager`" " +
                "--hidden-import `"selenium`" " +
                "mail_generator.py"

Write-Host "Running build command..." -ForegroundColor Yellow
Write-Host $buildCommand -ForegroundColor Gray

# Execute the build
try {
    Invoke-Expression $buildCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nBuild completed successfully!" -ForegroundColor Green
        Write-Host "Executable can be found in the 'dist' folder" -ForegroundColor Yellow
    } else {
        Write-Host "`nBuild failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "`nBuild failed with error: $_" -ForegroundColor Red
}

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} 