"""Tests de get_security_code: sin código por defecto."""

from server import config_loader


def test_security_code_empty_without_env_or_config(monkeypatch):
    monkeypatch.delenv("PRINTER_SECURITY_CODE", raising=False)
    monkeypatch.setattr(config_loader.ConfigManager, "get_config", classmethod(lambda cls: {"security": {}}))
    assert config_loader.get_security_code() == ""


def test_security_code_from_config(monkeypatch):
    monkeypatch.delenv("PRINTER_SECURITY_CODE", raising=False)
    monkeypatch.setattr(
        config_loader.ConfigManager, "get_config", classmethod(lambda cls: {"security": {"security_code": "abc"}})
    )
    assert config_loader.get_security_code() == "abc"


def test_security_code_env_var_wins(monkeypatch):
    monkeypatch.setenv("PRINTER_SECURITY_CODE", "from-env")
    monkeypatch.setattr(config_loader.ConfigManager, "get_config", classmethod(lambda cls: {"security": {}}))
    assert config_loader.get_security_code() == "from-env"
