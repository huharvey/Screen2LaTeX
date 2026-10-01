import sys
import urllib.error
import urllib.request

from settings import load_settings


def main():
    settings = load_settings()
    host = settings["server_host"]
    port = settings["server_port"]
    timeout = settings["request_timeout_seconds"]

    url = f"http://{host}:{port}/ocr"

    try:
        request = urllib.request.Request(
            url,
            data=b"ocr",
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = response.read().decode("utf-8")

        if result != "OK":
            raise RuntimeError(result)

    except urllib.error.URLError as exc:
        print(f"公式识别失败：无法连接本地服务：{exc}")
        return 1
    except Exception as exc:
        print(f"公式识别失败：{exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
