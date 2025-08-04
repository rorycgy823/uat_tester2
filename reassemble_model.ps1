# PowerShell script to reassemble phi-2-model.zip from email parts
# Run this script after downloading all parts to reconstruct the original model file

Write-Host "🔄 Reassembling phi-2-model.zip from parts..."

# Check if all parts exist
$partFiles = Get-ChildItem "phi-2-model.part*.zip" | Sort-Object Name
$expectedParts = 85

if ($partFiles.Count -ne $expectedParts) {
    Write-Host "❌ Error: Expected $expectedParts parts, but found $($partFiles.Count) parts"
    Write-Host "Missing parts:"
    for ($i = 1; $i -le $expectedParts; $i++) {
        $partName = "phi-2-model.part$("{0:D2}" -f $i).zip"
        if (-not (Test-Path $partName)) {
            Write-Host "   - $partName"
        }
    }
    exit 1
}

Write-Host "✅ Found all $expectedParts parts"

# Reassemble the file
$outputFile = "phi-2-model-reassembled.zip"
$writer = [System.IO.File]::Create($outputFile)

try {
    foreach ($partFile in $partFiles) {
        Write-Host "📦 Processing: $($partFile.Name)"
        $partData = [System.IO.File]::ReadAllBytes($partFile.FullName)
        $writer.Write($partData, 0, $partData.Length)
    }
    
    $writer.Close()
    
    # Verify the reassembled file size
    $reassembledSize = (Get-Item $outputFile).Length
    $originalSize = 477,741,056  # Expected size in bytes (455.59 MB)
    
    Write-Host "🎉 Successfully reassembled: $outputFile"
    Write-Host "📊 File size: $([math]::Round($reassembledSize / 1MB, 2)) MB"
    
    if ($reassembledSize -eq $originalSize) {
        Write-Host "✅ File size matches original - reassembly successful!"
    } else {
        Write-Host "⚠️ Warning: File size differs from expected. Please verify integrity."
    }
    
    Write-Host "`n📝 Next steps:"
    Write-Host "1. Extract the reassembled ZIP file"
    Write-Host "2. You should get: phi-2.Q4_K_M.gguf"
    Write-Host "3. Place this file in your CDSW project root"
    
} catch {
    Write-Host "❌ Error during reassembly: $($_.Exception.Message)"
    if ($writer) { $writer.Close() }
}
