param(
  [Parameter(Mandatory = $true)][string]$Voice,
  [Parameter(Mandatory = $true)][string]$Text,
  [int]$Rate = 0
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.Rate = $Rate
$chosen = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Name -like "*$Voice*" } | Select-Object -First 1
if ($chosen) { $s.SelectVoice($chosen.VoiceInfo.Name) }
$s.Speak($Text)
$s.Dispose()