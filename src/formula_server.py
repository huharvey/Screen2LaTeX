import os
import warnings
import pyperclip
import logging


from http.server import BaseHTTPRequestHandler, HTTPServer



warnings.filterwarnings("ignore")

ROOT = r"E:\Tools\UniMERNet"
os.chdir(ROOT)

# 直接复用你已经跑通的代码
from clipboard_ocr import FormulaOCR, get_clipboard_image, clean_latex


LOG_FILE = os.path.join(ROOT, "formula_server.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)


logging.info("开始加载 UniMERNet")

ocr = FormulaOCR()

logging.info("UniMERNet 加载完成，Server Ready")


class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/ocr":
            self.send_response(404)
            self.end_headers()
            return

        try:
            image = get_clipboard_image()

            if image is None:
                raise RuntimeError("剪贴板里没有可读取的图片")

            latex = ocr.recognize(image)
            latex = clean_latex(latex)

            markdown = f"$$\n{latex}\n$$"

            pyperclip.copy(markdown)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

            print("\n识别完成：")
            logging.info("公式识别完成")
            print(markdown)

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))

            print("识别失败：", e)
            logging.exception("公式识别失败")

    def log_message(self, format, *args):
        # 不打印 HTTP 日志
        pass


server = HTTPServer(("127.0.0.1", 8765), Handler)

print("Formula OCR Server:")
print("http://127.0.0.1:8765")

server.serve_forever()