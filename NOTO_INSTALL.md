如何在 Windows 上快速安装 Noto 字体（以解决 matplotlib 多语言显示问题）

步骤（推荐）：

1) 在 PowerShell 中运行我们仓库内的 helper 脚本（非管理员）：

```powershell
# 从仓库根目录运行
powershell -ExecutionPolicy Bypass -File scripts\download_and_install_noto.ps1
```

该脚本会把以下 ttf 下载到：%LOCALAPPDATA%\Microsoft\Windows\Fonts

- NotoSans-Regular.ttf
- NotoNaskhArabic-Regular.ttf
- NotoSansDevanagari-Regular.ttf

2) 重新启动你的 Python 解释器（或注销/登录），然后重新运行绘图脚本：

```powershell
python scripts\04_release_geo.py
```

3) 如果你希望系统范围安装（所有用户都可用），请以管理员身份运行 PowerShell，并把下载目录改为 `C:\Windows\Fonts` 或手动把下载的 ttf 复制到 `C:\Windows\Fonts`。

手动下载（如果脚本下载失败）：
- 在浏览器打开对应的 GitHub raw 链接并保存文件到本地：
  - https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf
  - https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf
  - https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf

注意
- 安装字体需要网络访问；如果你的环境禁止外网访问，请手动从可以访问网络的机器下载后拷贝到此仓库或目标机器。
- 有些语言（如阿拉伯文）除了字体外，matplotlib 对字形方向（从右向左）的原生支持有限，但大多数字符会正常显示。若需更完善的阿拉伯文呈现，需更复杂的文本渲染（例如使用 PIL + HarfBuzz/Fribidi）——这超出当前任务范围。
