import json
import os
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.json"


def _resolve_path(value: str, base: Optional[Path] = None) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(value))
    path = Path(expanded)

    if not path.is_absolute() and base is not None:
        path = base / path

    return path.resolve()


def load_settings() -> dict:
    config_env = os.environ.get("SCREEN2LATEX_CONFIG")

    if config_env:
        config_path = _resolve_path(config_env, PROJECT_ROOT)
    else:
        config_path = DEFAULT_CONFIG_PATH

    if not config_path.is_file():
        raise FileNotFoundError(
            f"未找到配置文件：{config_path}\n"
            f"请先复制 {PROJECT_ROOT / 'config.example.json'} 为 "
            f"{PROJECT_ROOT / 'config.json'} 并修改路径。"
        )

    data = json.loads(config_path.read_text(encoding="utf-8"))

    if "unimernet_root" not in data:
        raise KeyError("config.json 缺少 unimernet_root")

    unimernet_root = _resolve_path(data["unimernet_root"])

    if not unimernet_root.is_dir():
        raise FileNotFoundError(f"UniMERNet 根目录不存在：{unimernet_root}")

    unimernet_config = _resolve_path(
        data.get("unimernet_config", "configs/demo.yaml"),
        unimernet_root,
    )
    model_dir = _resolve_path(
        data.get("model_dir", "models/unimernet_small"),
        unimernet_root,
    )
    checkpoint = _resolve_path(
        data.get(
            "checkpoint",
            "models/unimernet_small/unimernet_small.pth",
        ),
        unimernet_root,
    )

    for label, path in (
        ("UniMERNet 配置", unimernet_config),
        ("模型目录", model_dir),
        ("模型 checkpoint", checkpoint),
    ):
        if not path.exists():
            raise FileNotFoundError(f"{label}不存在：{path}")

    device = str(data.get("device", "auto")).lower()

    if device not in {"auto", "cpu", "cuda"}:
        raise ValueError("device 只能是 auto、cpu 或 cuda")

    server = data.get("server", {})
    host = str(server.get("host", "127.0.0.1"))
    port = int(server.get("port", 8765))
    timeout = float(server.get("request_timeout_seconds", 60))

    return {
        "config_path": config_path,
        "unimernet_root": unimernet_root,
        "unimernet_config": unimernet_config,
        "model_dir": model_dir,
        "checkpoint": checkpoint,
        "device": device,
        "server_host": host,
        "server_port": port,
        "request_timeout_seconds": timeout,
    }
