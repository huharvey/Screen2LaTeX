import argparse
import io
import os
import sys

import pyperclip
import torch
import win32clipboard
from PIL import Image, ImageGrab

from settings import load_settings


SETTINGS = load_settings()
UNIMERNET_ROOT = SETTINGS["unimernet_root"]

# UniMERNet 不是本仓库的一部分。把上游仓库根目录加入 import 路径，
# 并切换工作目录，以兼容 UniMERNet 配置中的相对路径。
if str(UNIMERNET_ROOT) not in sys.path:
    sys.path.insert(0, str(UNIMERNET_ROOT))

os.chdir(UNIMERNET_ROOT)

from unimernet.common.config import Config
import unimernet.tasks as tasks
from unimernet.processors import load_processor


def get_clipboard_image():
    """从 Windows 剪贴板读取图片，兼容 Pillow 和 Quicker 的 PNG 格式。"""
    image = ImageGrab.grabclipboard()

    if isinstance(image, Image.Image):
        return image

    win32clipboard.OpenClipboard()

    try:
        fmt = win32clipboard.EnumClipboardFormats(0)

        while fmt:
            try:
                name = win32clipboard.GetClipboardFormatName(fmt)
            except Exception:
                name = ""

            if name.upper() == "PNG":
                data = win32clipboard.GetClipboardData(fmt)
                return Image.open(io.BytesIO(data)).convert("RGB")

            fmt = win32clipboard.EnumClipboardFormats(fmt)
    finally:
        win32clipboard.CloseClipboard()

    return None


def clean_latex(text: str) -> str:
    """去掉模型可能自带的公式定界符，避免重复包裹。"""
    text = text.strip()

    delimiter_pairs = (
        ("$$", "$$"),
        (r"\[", r"\]"),
        (r"\(", r"\)"),
    )

    for start, end in delimiter_pairs:
        if text.startswith(start) and text.endswith(end):
            return text[len(start) : -len(end)].strip()

    if text.startswith("$") and text.endswith("$") and len(text) >= 2:
        return text[1:-1].strip()

    return text


class FormulaOCR:
    def __init__(self):
        requested_device = SETTINGS["device"]

        if requested_device == "auto":
            requested_device = "cuda" if torch.cuda.is_available() else "cpu"

        if requested_device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("config.json 请求使用 CUDA，但当前 PyTorch 环境不可用")

        self.device = torch.device(requested_device)

        # 不要求用户修改 UniMERNet 的 demo.yaml。
        # 通过 Config.options 覆盖模型目录、checkpoint 和 tokenizer 路径。
        options = [
            f"model.model_config.model_name={SETTINGS['model_dir'].as_posix()}",
            f"model.pretrained={SETTINGS['checkpoint'].as_posix()}",
            f"model.tokenizer_config.path={SETTINGS['model_dir'].as_posix()}",
        ]

        args = argparse.Namespace(
            cfg_path=str(SETTINGS["unimernet_config"]),
            options=options,
        )

        cfg = Config(args)
        task = tasks.setup_task(cfg)

        self.model = task.build_model(cfg).to(self.device)
        self.model.eval()

        self.processor = load_processor(
            "formula_image_eval",
            cfg.config.datasets.formula_rec_eval.vis_processor.eval,
        )

        print(f"UniMERNet loaded on {self.device}")

    @torch.inference_mode()
    def recognize(self, image: Image.Image) -> str:
        image = image.convert("RGB")
        tensor = self.processor(image).unsqueeze(0).to(self.device)
        output = self.model.generate({"image": tensor})
        return output["pred_str"][0]


def main():
    image = get_clipboard_image()

    if image is None:
        raise RuntimeError("剪贴板里没有可读取的图片")

    ocr = FormulaOCR()
    latex = clean_latex(ocr.recognize(image))
    markdown = f"$$\n{latex}\n$$"

    pyperclip.copy(markdown)

    print("\nRecognition:")
    print(markdown)


if __name__ == "__main__":
    main()
