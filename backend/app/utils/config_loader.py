from pathlib import Path

import yaml


def load_shifts_config(config_path: str | Path | None = None) -> dict:
    if config_path is not None:
        base_path = Path(config_path)
    else:
        candidates = [
            Path(__file__).resolve().parents[2] / "shifts_config.yaml",
            Path(__file__).resolve().parents[1] / "shifts_config.yaml",
            Path.cwd() / "backend" / "shifts_config.yaml",
            Path.cwd() / "shifts_config.yaml",
        ]
        base_path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
    with base_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
