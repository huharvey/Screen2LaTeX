import logging
import warnings
from http.server import BaseHTTPRequestHandler, HTTPServer

import pyperclip

from settings import PROJECT_ROOT, load_settings


warnings.filterwarnings("ignore")

SETTINGS = load_settings()

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "formula_server.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

from clipboard_ocr import FormulaOCR, clean_latex, get_clipboard_image


logging.info("开始加载 UniMERNet")
ocr = FormulaOCR()
logging.info("UniMERNet 加载完成，Server Ready")


class Handler(BaseHTTPRequestHandler):
    def _respond(self, status: int, body: str):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, "READY")
            return

        self._respond(404, "NOT FOUND")

    def do_POST(self):
        if self.path != "/ocr":
            self._respond(404, "NOT FOUND")
            return

        try:
            image = get_clipboard_image()

            if image is None:
                raise RuntimeError("剪贴板里没有可读取的图片")

            latex = clean_latex(ocr.recognize(image))
            markdown = f"$$\n{latex}\n$$"
            pyperclip.copy(markdown)

            logging.info("公式识别完成")
            self._respond(200, "OK")

        except Exception as exc:
            logging.exception("公式识别失败")
            self._respond(500, str(exc))

    def log_message(self, format, *args):
        pass


def main():
    host = SETTINGS["server_host"]
    port = SETTINGS["server_port"]

    server = HTTPServer((host, port), Handler)
    logging.info("Screen2LaTeX server listening on %s:%s", host, port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Screen2LaTeX server stopped by user")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
