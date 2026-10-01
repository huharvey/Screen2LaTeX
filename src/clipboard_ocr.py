import os
import io
import argparse
import torch
import pyperclip
import win32clipboard

from PIL import Image, ImageGrab

# 必须先切到 UniMERNet 根目录，
# 因为 demo.yaml 里的模型路径是相对路径
ROOT = r"E:\Tools\UniMERNet"
os.chdir(ROOT)

from unimernet.common.config import Config
import unimernet.tasks as tasks
from unimernet.processors import load_processor


CONFIG_PATH = os.path.join(ROOT, "configs", "demo.yaml")


def get_clipboard_image():
    # 1. 先尝试 Pillow 自己读取
    image = ImageGrab.grabclipboard()

    if isinstance(image, Image.Image):
        return image

    # 2. Quicker 有时会把截图以 PNG 剪贴板格式保存
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
    """去掉模型可能自带的公式定界符。"""
    text = text.strip()

    if text.startswith("$$") and text.endswith("$$"):
        text = text[2:-2].strip()

    if text.startswith(r"\[") and text.endswith(r"\]"):
        text = text[2:-2].strip()

    return text


class FormulaOCR:
    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        args = argparse.Namespace(
            cfg_path=CONFIG_PATH,
            options=None
        )

        cfg = Config(args)
        task = tasks.setup_task(cfg)

        self.model = task.build_model(cfg).to(self.device)
        self.model.eval()

        self.processor = load_processor(
            "formula_image_eval",
            cfg.config.datasets.formula_rec_eval.vis_processor.eval
        )

        print(f"UniMERNet loaded on {self.device}")

    @torch.inference_mode()
    def recognize(self, image: Image.Image) -> str:
        image = image.convert("RGB")

        tensor = self.processor(image)
        tensor = tensor.unsqueeze(0).to(self.device)

        output = self.model.generate({
            "image": tensor
        })

        return output["pred_str"][0]


def main():
    image = get_clipboard_image()

    if image is None:
        raise RuntimeError("剪贴板里没有可读取的图片")

    ocr = FormulaOCR()

    latex = ocr.recognize(image)
    latex = clean_latex(latex)

    markdown = f"$$\n{latex}\n$$"

    pyperclip.copy(markdown)

    print("\nRecognition:")
    print(markdown)


if __name__ == "__main__":
    main()