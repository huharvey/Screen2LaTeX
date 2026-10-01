# Screen2LaTeX

Screen2LaTeX 是一个面向 Windows 的本地公式 OCR 工作流：截图后调用本地常驻的 UniMERNet，把公式识别为 LaTeX，并以 Markdown 行间公式格式写回剪贴板。

核心目标不是重新实现公式识别模型，而是把“截图 → OCR → Markdown → 剪贴板”这条桌面工作流做得足够顺手。

## 工作流

~~~text
Quicker / 其他截图工具
        ↓
框选公式并写入 Windows 剪贴板
        ↓
Screen2LaTeX client
        ↓
本地常驻 UniMERNet server
        ↓
$$
LaTeX
$$
        ↓
Windows 剪贴板
~~~

推荐搭配 Quicker 使用。普通截图和公式 OCR 可以使用不同触发方式，例如 F11 保留普通截图，鼠标 X2 触发公式 OCR。

## 特性

- 完全本地推理，不按次调用云端 OCR。
- UniMERNet 模型常驻内存，避免每次截图都重新加载模型。
- 兼容 Quicker 写入的 PNG 剪贴板格式。
- 自动把识别结果包装为 Markdown 行间公式。
- client / server 分离，Quicker 只需等待轻量 client 返回。
- 支持 Windows 登录后静默启动后台 server。

## 依赖

- Windows 10 / 11
- Python 3.10（推荐 Conda）
- UniMERNet
- Git LFS（下载模型时需要）
- Quicker（可选，但推荐）

OCR 后端来自 [OpenDataLab/UniMERNet](https://github.com/opendatalab/UniMERNet)。本仓库不包含 UniMERNet 源码或模型权重。

## 1. 安装 UniMERNet

示例：

~~~powershell
conda create -n unimernet python=3.10 -y
conda activate unimernet

cd E:\Tools
git clone https://github.com/opendatalab/UniMERNet.git
cd UniMERNet

pip install -e ".[full]"
~~~

下载 small 模型：

~~~powershell
git lfs install
cd models
git clone https://huggingface.co/wanderkid/unimernet_small
~~~

完成后应存在类似文件：

~~~text
E:\Tools\UniMERNet\models\unimernet_small\unimernet_small.pth
~~~

Screen2LaTeX 会通过自己的 config.json 覆盖模型路径，因此无需为了本项目修改 UniMERNet 的 configs/demo.yaml。

## 2. 安装 Screen2LaTeX 依赖

克隆本仓库：

~~~powershell
cd E:\Tools
git clone https://github.com/huharvey/Screen2LaTeX.git
cd Screen2LaTeX

conda activate unimernet
pip install -r requirements.txt
~~~

## 3. 创建配置文件

复制示例配置：

~~~powershell
Copy-Item config.example.json config.json
~~~

然后修改 config.json：

~~~json
{
  "unimernet_root": "E:/Tools/UniMERNet",
  "unimernet_config": "configs/demo.yaml",
  "model_dir": "models/unimernet_small",
  "checkpoint": "models/unimernet_small/unimernet_small.pth",
  "device": "auto",
  "server": {
    "host": "127.0.0.1",
    "port": 8765,
    "request_timeout_seconds": 60
  }
}
~~~

通常只需要修改 unimernet_root。

device 支持 auto、cpu、cuda。auto 会在 CUDA 可用时优先使用 CUDA，否则使用 CPU。

也可以通过环境变量 SCREEN2LATEX_CONFIG 指定另一份配置文件。

## 4. 先测试单次 OCR

先用 Win + Shift + S 或 Quicker 截一张公式到剪贴板，然后运行：

~~~powershell
conda activate unimernet
python src\clipboard_ocr.py
~~~

成功后，剪贴板会变成：

~~~markdown
$$
x_{t+1}=Ax_t+Bu_t
$$
~~~

## 5. 启动常驻后台服务

调试时先前台运行：

~~~powershell
python src\formula_server.py
~~~

服务器默认监听 http://127.0.0.1:8765。

可以检查：

~~~powershell
Invoke-WebRequest http://127.0.0.1:8765/health
~~~

返回 READY 表示模型已经加载完成。

另开一个终端，截图后运行：

~~~powershell
python src\formula_client.py
~~~

client 只有在 OCR 完成并把 LaTeX 写回剪贴板后才会退出。

## 6. Quicker 配置

详细配置见 [quicker/README.md](quicker/README.md)。

推荐组合动作只有三步：

~~~text
1. 屏幕截图
2. 运行 formula_client.py
3. 提示消息：公式识别完成，已复制到剪贴板
~~~

不建议自动 Ctrl+V，因为截图页面和笔记页面经常不是同一个窗口。收到完成提示后，再切到笔记页面手动粘贴即可。

## 7. Windows 登录后静默启动

先激活安装 UniMERNet 的 Conda 环境，再运行：

~~~powershell
conda activate unimernet
powershell -ExecutionPolicy Bypass -File scripts\install_startup.ps1
~~~

脚本会在当前用户的 Startup 文件夹创建快捷方式，目标是当前环境里的 pythonw.exe，因此登录后不会出现 PowerShell / CMD 黑窗口。

如果希望安装后立即启动：

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts\install_startup.ps1 -StartNow
~~~

删除开机启动：

~~~powershell
powershell -ExecutionPolicy Bypass -File scripts\uninstall_startup.ps1
~~~

后台日志保存在 logs\formula_server.log。

## 常见问题

### Quicker 截图后 Python 提示“剪贴板里没有可读取的图片”

Quicker 有时以 PNG 自定义剪贴板格式写入截图。Screen2LaTeX 已包含 pywin32 fallback；请确认已经安装 requirements.txt 中的依赖。

### server 启动很慢

首次启动需要加载 UniMERNet 模型。常驻 server 的意义就是只承担一次加载成本；后续每次截图只做推理。

### client 提示无法连接

确认 formula_server.py 正在运行，或者检查 logs\formula_server.log。默认端口是 8765。

### 端口被占用

修改 config.json 中的 server.port，然后重启 server。client 会读取同一配置。

## 项目边界

Screen2LaTeX 不实现数学公式识别模型。识别能力由 UniMERNet 提供；本项目主要负责 Windows 剪贴板、Markdown 包装、常驻本地服务、Quicker 集成和开机自启。

## Credits

- [UniMERNet](https://github.com/opendatalab/UniMERNet) — mathematical expression recognition backend, Apache-2.0 licensed.
- [Quicker](https://getquicker.net/) — recommended Windows workflow / trigger tool.

## License

Screen2LaTeX 自有代码使用 MIT License。UniMERNet 及其模型遵循其上游项目自己的许可证与使用条款。
