$ErrorActionPreference = "Stop"

$StartupDir = [Environment]::GetFolderPath("Startup")
$ShortcutPath = Join-Path $StartupDir "Screen2LaTeX Server.lnk"

if (Test-Path $ShortcutPath) {
    Remove-Item $ShortcutPath -Force
    Write-Host "已删除开机启动快捷方式："
    Write-Host $ShortcutPath
}
else {
    Write-Host "未找到 Screen2LaTeX 开机启动快捷方式。"
}
