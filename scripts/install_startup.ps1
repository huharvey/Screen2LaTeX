param(
    [string]$PythonwPath = "",
    [switch]$StartNow
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ServerScript = Join-Path $ProjectRoot "src\formula_server.py"
$ConfigPath = Join-Path $ProjectRoot "config.json"

if (-not (Test-Path $ServerScript)) {
    throw "未找到 server 脚本：$ServerScript"
}

if (-not (Test-Path $ConfigPath)) {
    throw "未找到 config.json。请先复制 config.example.json 并完成配置。"
}

if ([string]::IsNullOrWhiteSpace($PythonwPath)) {
    $PythonExe = (Get-Command python.exe -ErrorAction Stop).Source
    $Candidate = Join-Path (Split-Path $PythonExe -Parent) "pythonw.exe"

    if (-not (Test-Path $Candidate)) {
        throw "当前 Python 环境中未找到 pythonw.exe。可通过 -PythonwPath 手动指定。"
    }

    $PythonwPath = $Candidate
}

$StartupDir = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir "Screen2LaTeX Server.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $PythonwPath
$Shortcut.Arguments = '"' + $ServerScript + '"'
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = "Screen2LaTeX background OCR server"
$Shortcut.Save()

Write-Host "已创建开机启动快捷方式："
Write-Host $ShortcutPath
Write-Host "Pythonw: $PythonwPath"

if ($StartNow) {
    Start-Process -FilePath $PythonwPath -ArgumentList ('"' + $ServerScript + '"') -WorkingDirectory $ProjectRoot
    Write-Host "已启动 Screen2LaTeX server。"
}
