# Quicker 配置

Screen2LaTeX 推荐让 Quicker 只负责三件事：截图、调用 client、提示完成。

## 组合动作

### 1. 屏幕截图

添加“屏幕截图”模块：

~~~text
截图类型：选择区域
写入剪贴板：开启
截图前延迟：200 ms（可选）
运行后延迟：300 ms 左右
~~~

Screen2LaTeX 的 clipboard_ocr.py 已兼容 Quicker 常见的 PNG 剪贴板格式。

### 2. 运行 formula_client.py

添加“运行或打开”模块。

程序填写安装 UniMERNet 的 Python 环境，例如：

~~~text
D:\deeplearning\envs\unimernet\python.exe
~~~

参数填写 Screen2LaTeX 的 client，例如：

~~~text
"E:\Tools\Screen2LaTeX\src\formula_client.py"
~~~

推荐：

~~~text
等待进程结束：开启
等待启动完成：关闭
窗口：隐藏
~~~

不要运行 clipboard_ocr.py。日常使用应运行 formula_client.py，由后台常驻 server 持有模型。

### 3. 提示消息

在 client 后添加“提示消息”：

~~~text
公式识别完成，已复制到剪贴板
~~~

client 会等到 OCR 完成、LaTeX 已经写回剪贴板后才退出，因此这条提示可以准确表示转录已经完成。

不建议自动发送 Ctrl+V：截图窗口与 Markdown 笔记窗口通常不同。看到完成提示后，切到目标笔记再手动粘贴更可靠。

## 推荐触发方式

普通截图可以继续保留原快捷键，例如 F11。

公式 OCR 单独绑定触发方式，例如：

~~~text
F11：普通截图
鼠标 X2：公式 OCR
~~~

Quicker 免费版可以使用高级鼠标触发，把 X2 直接映射到这个组合动作。

## 最终动作链

~~~text
X2
 ↓
选择区域截图
 ↓
formula_client.py
 ↓
本地 UniMERNet server
 ↓
剪贴板变为 $$...$$
 ↓
提示“公式识别完成，已复制到剪贴板”
~~~
