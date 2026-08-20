param(
  [string]$Title,
  [string]$Message,
  [string]$Sound = "Default",
  [string]$Color = "0969DA"
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$tones = @{
  "Notification.Reminder"     = 660, 300
  "Notification.SMS"          = 880, 200
  "Notification.Mail"         = 440, 400
  "Notification.Alarm"        = 990, 500
  "Notification.Message"      = 520, 200
  "Notification.Looping.Call" = 880, 600
  "Default"                   = 660, 150
}
if ($tones.ContainsKey($Sound)) {
  $freq, $ms = $tones[$Sound]
  [console]::beep($freq, $ms)
}

$accent = $null
try { $accent = [System.Drawing.ColorTranslator]::FromHtml("#$Color") } catch {}
if (-not $accent) { $accent = [System.Drawing.Color]::FromArgb(9, 105, 218) }

$form = New-Object System.Windows.Forms.Form
$form.Text = $Title
$form.StartPosition = "Manual"
$form.FormBorderStyle = "None"
$form.ShowInTaskbar = $false
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(40, 44, 52)
$form.Size = New-Object System.Drawing.Size(360, 100)
$wa = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$form.Location = New-Object System.Drawing.Point(($wa.Width - 380), ($wa.Height - 120))

$radius = 14
$path = New-Object System.Drawing.Drawing2D.GraphicsPath
$rect = New-Object System.Drawing.Rectangle 0, 0, ($form.Width - 1), ($form.Height - 1)
$d = $radius * 2
$path.AddArc($rect.X, $rect.Y, $d, $d, 180, 90)
$path.AddArc($rect.Right - $d, $rect.Y, $d, $d, 270, 90)
$path.AddArc($rect.Right - $d, $rect.Bottom - $d, $d, $d, 0, 90)
$path.AddArc($rect.X, $rect.Bottom - $d, $d, $d, 90, 90)
$path.CloseFigure()
$form.Region = New-Object System.Drawing.Region $path

$bar = New-Object System.Windows.Forms.Panel
$bar.BackColor = $accent
$bar.Size = New-Object System.Drawing.Size(6, $form.Height)
$bar.Location = New-Object System.Drawing.Point(0, 0)
$bar.Anchor = "Left, Top, Bottom"
$form.Controls.Add($bar)

$lblTitle = New-Object System.Windows.Forms.Label
$lblTitle.Text = $Title
$lblTitle.ForeColor = "White"
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 10.5, [System.Drawing.FontStyle]::Bold)
$lblTitle.Location = New-Object System.Drawing.Point(20, 10)
$lblTitle.AutoSize = $true
$form.Controls.Add($lblTitle)

$lblMsg = New-Object System.Windows.Forms.Label
$lblMsg.Text = $Message
$lblMsg.ForeColor = [System.Drawing.Color]::FromArgb(190, 194, 200)
$lblMsg.Font = New-Object System.Drawing.Font("Segoe UI", 9.5)
$lblMsg.Location = New-Object System.Drawing.Point(20, 38)
$lblMsg.Size = New-Object System.Drawing.Size(330, 52)
$lblMsg.AutoEllipsis = $true
$form.Controls.Add($lblMsg)

$form.Add_Click({ $form.Close() })

$form.Opacity = 0
$fadeIn = New-Object System.Windows.Forms.Timer
$fadeIn.Interval = 20
$fadeIn.Add_Tick({
  if ($form.Opacity -lt 0.95) { $form.Opacity += 0.15 } else { $form.Opacity = 1; $fadeIn.Stop() }
})
$fadeIn.Start()

$auto = New-Object System.Windows.Forms.Timer
$auto.Interval = 5500
$auto.Add_Tick({
  $auto.Stop()
  $fadeOut = New-Object System.Windows.Forms.Timer
  $fadeOut.Interval = 30
  $fadeOut.Add_Tick({
    if ($form.Opacity -gt 0.05) { $form.Opacity -= 0.15 } else { $form.Close() }
  })
  $fadeOut.Start()
})
$auto.Start()

[System.Windows.Forms.Application]::Run($form) | Out-Null