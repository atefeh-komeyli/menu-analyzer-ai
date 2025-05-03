import pytest
from PIL import Image
import io
import base64
import main


def test_convert_to_pil_image_with_pil_image(sample_pil_image):
    """Test convert_to_pil_image function with a PIL Image input."""
    result = main.convert_to_pil_image(sample_pil_image)
    assert isinstance(result, Image.Image)
    assert result == sample_pil_image


def test_convert_to_pil_image_with_image_list(sample_image_list):
    """Test convert_to_pil_image function with a list of PIL Images."""
    result = main.convert_to_pil_image(sample_image_list)
    assert isinstance(result, Image.Image)
    assert result == sample_image_list[0]


def test_convert_to_pil_image_with_invalid_input():
    """Test convert_to_pil_image function with an invalid input type."""
    with pytest.raises(TypeError):
        main.convert_to_pil_image("not an image")


def test_convert_to_base64(sample_pil_image):
    """Test convert_to_base64 function."""
    # Convert image to base64 using the function
    result = main.convert_to_base64(sample_pil_image)

    # Verify the result is a string
    assert isinstance(result, str)

    # Verify we can decode it back to an image
    image_data = base64.b64decode(result)
    image = Image.open(io.BytesIO(image_data))
    assert isinstance(image, Image.Image)

    # Verify the image dimensions match
    assert image.size == sample_pil_image.size
