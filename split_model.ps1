# PowerShell script to split phi-2-model.zip into email-friendly chunks
param(
    [string]$InputFile = "phi-2-model.zip",
    [int]$ChunkSizeMB = 20
)

Write-Host "🔄 Splitting $InputFile into ${ChunkSizeMB}MB chunks..."

$chunkSize = $ChunkSizeMB * 1024 * 1024  # Convert MB to bytes
$buffer = New-Object byte[] $chunkSize
$chunkNumber = 1

try {
    $reader = [System.IO.File]::OpenRead($InputFile)
    
    while (($bytesRead = $reader.Read($buffer, 0, $chunkSize)) -gt 0) {
        $outputFile = "phi-2-model.part$("{0:D2}" -f $chunkNumber).zip"
        
        # Write only the bytes that were actually read
        $actualBuffer = New-Object byte[] $bytesRead
        [Array]::Copy($buffer, $actualBuffer, $bytesRead)
        [System.IO.File]::WriteAllBytes($outputFile, $actualBuffer)
        
        $sizeMB = [math]::Round($bytesRead / 1MB, 2)
        Write-Host "✅ Created: $outputFile ($sizeMB MB)"
        $chunkNumber++
    }
    
    $reader.Close()
    Write-Host "🎉 Successfully split into $($chunkNumber - 1) parts!"
    
    # Show all created parts
    Write-Host "`n📦 Created files:"
    Get-ChildItem "phi-2-model.part*.zip" | ForEach-Object {
        $sizeMB = [math]::Round($_.Length / 1MB, 2)
        Write-Host "   $($_.Name) - $sizeMB MB"
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
    if ($reader) { $reader.Close() }
}
