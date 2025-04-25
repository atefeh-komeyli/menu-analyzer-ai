import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image
import io
import base64

# Add the parent directory to sys.path to allow imports from the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_pil_image():
    """Create a simple PIL Image for testing."""
    # Create a small 10x10 red image
    return Image.new('RGB', (10, 10), color='red')

@pytest.fixture
def sample_image_list(sample_pil_image):
    """Create a list with a single PIL Image for testing."""
    return [sample_pil_image]

@pytest.fixture
def mock_openai():
    """Mock the ChatOpenAI class."""
    with patch('main.ChatOpenAI') as mock_chat:
        mock_instance = MagicMock()
        mock_chat.return_value = mock_instance
        yield mock_chat 