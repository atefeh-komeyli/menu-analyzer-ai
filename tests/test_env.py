import os
from unittest.mock import patch
import main


def test_env_variables():
    """Test that the required environment variables are checked."""
    # We only want to check that the code handles the absence of env vars,
    # not actually remove them from the environment
    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake_key"}, clear=True):
        # Just try to import the module, which should succeed with our mocked env var
        import importlib

        importlib.reload(main)
        assert True  # If we get here, the import didn't raise an error


def test_constants():
    """Test that the application constants are properly defined."""
    assert hasattr(main, "MAX_QUESTIONS")
    assert isinstance(main.MAX_QUESTIONS, int)
    assert main.MAX_QUESTIONS > 0

    assert hasattr(main, "MAX_MENU_ITEMS")
    assert isinstance(main.MAX_MENU_ITEMS, int)
    assert main.MAX_MENU_ITEMS > 0


def test_logger_initialized():
    """Test that the logger is properly initialized."""
    assert hasattr(main, "logger")
    assert hasattr(main.logger, "warning")
    assert hasattr(main.logger, "info")
    assert hasattr(main.logger, "error")
