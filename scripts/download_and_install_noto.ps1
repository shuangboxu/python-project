<#
PowerShell helper: 下载并（为当前用户）安装部分 Noto 字体以改善 matplotlib 的多语言显示

说明：
- 该脚本会把字体下载到当前用户的本地字体文件夹 (%LOCALAPPDATA%\Microsoft\Windows\Fonts)
- 若要系统范围安装（C:\Windows\Fonts），请以管理员身份运行并修改目标路径
- 运行后，最好注销/登录或重启 Python 会话以使 matplotlib 识别新字体

注意：下载来源为 GitHub 仓库的 raw 链接（googlefonts/noto-fonts）。若网络受限，请手动在浏览器下载下面列出的 ttf 文件并放到相同目录。
#>

param(
    [string]$OutDir = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
)

Write-Host "目标字体目录： $OutDir"
if (-not (Test-Path $OutDir)){
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
}

$files = @(
    @{ url = 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf'; name = 'NotoSans-Regular.ttf' },
    @{ url = 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf'; name = 'NotoNaskhArabic-Regular.ttf' },
    @{ url = 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf'; name = 'NotoSansDevanagari-Regular.ttf' }
)

foreach ($f in $files) {
    $dest = Join-Path $OutDir $($f.name)
    try {
        Write-Host "Downloading $($f.url) -> $dest"
        Invoke-WebRequest -Uri $f.url -OutFile $dest -UseBasicParsing -ErrorAction Stop
        Write-Host "Downloaded: $dest"
    } catch {
        Write-Warning "无法下载 $($f.url). 请检查网络或手动下载并放到 $OutDir"
    }
}

Write-Host "下载完成。请注销/重新登录或重启 Python 解释器，然后重新运行绘图脚本（例如： python scripts/04_release_geo.py ）以应用新字体。"
Write-Host "如果你希望把字体安装到系统字体目录(C:\\Windows\\Fonts)，以管理员身份运行并把`$OutDir`改为 'C:\\Windows\\Fonts'，然后复制 ttf 文件到该目录。"
