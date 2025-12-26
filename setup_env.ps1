# Add FFmpeg to PATH
$ffmpegPath = "D:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
$env:PATH = "$env:PATH;$ffmpegPath"

# Verify ffmpeg is accessible
$testffmpeg = & ffmpeg -version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "FFmpeg is now available in PATH"
} else {
    Write-Host "FFmpeg path added but may need PowerShell restart"
}
