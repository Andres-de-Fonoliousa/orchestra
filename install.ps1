$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $MyInvocation.MyCommand.Path

python "$Repo\orchestra.py" install "$Repo"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$Brain = Join-Path $HOME ".config\opencode"
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$Brain*") {
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$Brain", "User")
    Write-Output "Added $Brain to your user PATH -- use 'orchestra <cmd>' in NEW terminals."
}

python "$Repo\orchestra.py" doctor
exit $LASTEXITCODE