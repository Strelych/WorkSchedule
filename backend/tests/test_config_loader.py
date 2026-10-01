from app.utils.config_loader import load_shifts_config


def test_load_shifts_config_reads_yaml_file():
    data = load_shifts_config()

    assert "roles" in data
    assert "generation_rules" in data
    assert data["roles"]["valet_night"]["shifts"][0]["id"] == "val_night"
