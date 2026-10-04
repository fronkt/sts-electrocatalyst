param([Parameter(Mandatory=$true)][string]$SourcePath,
      [Parameter(Mandatory=$true)][string]$TargetPath,
      [int]$LongSide = 1600)
# Local GDI+ rendering of a WMF/EMF metafile to PNG on a white background (same role as decode_wdp.ps1 for WDP).
# Pillow's WMF/EMF stub overprints per-character spacing of MathType equation metafiles; GDI+ honours it.
$ErrorActionPreference = 'Stop'
if (Test-Path -LiteralPath $TargetPath) { throw 'Refusing existing conversion target' }
Add-Type -AssemblyName System.Drawing
$taskImage = [System.Drawing.Image]::FromFile($SourcePath)
try {
    $f = [Math]::Min(4.0, $LongSide / [Math]::Max($taskImage.Width, $taskImage.Height))
    $w = [Math]::Max(1, [int][Math]::Ceiling($taskImage.Width * $f))
    $h = [Math]::Max(1, [int][Math]::Ceiling($taskImage.Height * $f))
    $bmp = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    try {
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        try {
            $g.Clear([System.Drawing.Color]::White)
            $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
            $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAlias
            $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $g.DrawImage($taskImage, 0, 0, $w, $h)
        } finally { $g.Dispose() }
        $bmp.Save($TargetPath, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Output ('Rendered metafile ' + $taskImage.Width + 'x' + $taskImage.Height + ' -> ' + $w + 'x' + $h)
    } finally { $bmp.Dispose() }
} finally { $taskImage.Dispose() }
