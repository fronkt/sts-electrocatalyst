param([Parameter(Mandatory=$true)][string]$SourcePath,
      [Parameter(Mandatory=$true)][string]$TargetPath)
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $TargetPath) { throw 'Refusing existing conversion target' }
Add-Type -AssemblyName PresentationCore
$taskStream = [System.IO.File]::OpenRead($SourcePath)
try {
    $taskDecoder = [System.Windows.Media.Imaging.BitmapDecoder]::Create(
        $taskStream,
        [System.Windows.Media.Imaging.BitmapCreateOptions]::PreservePixelFormat,
        [System.Windows.Media.Imaging.BitmapCacheOption]::OnLoad)
    if ($taskDecoder.Frames.Count -ne 1) { throw 'Unexpected multi-frame WDP' }
    $taskEncoder = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
    $taskEncoder.Frames.Add($taskDecoder.Frames[0])
    $taskOutput = [System.IO.File]::Open($TargetPath, [System.IO.FileMode]::CreateNew)
    try { $taskEncoder.Save($taskOutput) } finally { $taskOutput.Dispose() }
    Write-Output ('Decoded WDP ' + $taskDecoder.Frames[0].PixelWidth + 'x' + $taskDecoder.Frames[0].PixelHeight)
} finally { $taskStream.Dispose() }
