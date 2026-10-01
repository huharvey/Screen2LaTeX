import urllib.request
import sys

URL = "http://127.0.0.1:8765/ocr"

try:
    request = urllib.request.Request(
        URL,
        data=b"ocr",
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        result = response.read().decode("utf-8")

    if result != "OK":
        raise RuntimeError(result)

except Exception as e:
    print(f"公式识别失败：{e}")
    sys.exit(1)

sys.exit(0)