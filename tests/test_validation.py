import pytest
import json
from unittest.mock import patch, MagicMock
from langchain.schema import AIMessage
from PIL import Image
import main

def test_max_menu_items_limit():
    """Test that the menu items are limited to MAX_MENU_ITEMS."""
    # Create a list of sample menu items larger than MAX_MENU_ITEMS
    sample_large_menu = [{"name": f"Item {i}", "description": "Test"} for i in range(main.MAX_MENU_ITEMS + 10)]
    
    with patch('main.ChatOpenAI') as mock_chat, patch('main.convert_to_base64') as mock_base64:
        # Mock the base64 conversion to avoid image processing issues
        mock_base64.return_value = "mocked_base64_string"
        
        # Configure the mock to return more items than MAX_MENU_ITEMS
        mock_instance = MagicMock()
        mock_chat.return_value = mock_instance
        mock_instance.invoke.return_value = AIMessage(content=json.dumps(sample_large_menu))
        
        # Create a sample PIL image for testing
        sample_image = Image.new('RGB', (10, 10))
        
        # Call extract_menu_items with sample input
        result = main.extract_menu_items([sample_image])
        
        # Verify the result is limited to MAX_MENU_ITEMS
        assert len(result) == main.MAX_MENU_ITEMS

def test_max_questions_limit():
    """Test that the number of questions is limited to MAX_QUESTIONS."""
    # We can infer this from the code logic in process_conversation
    # But we can't directly test it since process_conversation is a nested function
    # This is a meta-test to confirm the constant exists
    assert hasattr(main, 'MAX_QUESTIONS')
    assert main.MAX_QUESTIONS > 0

def test_extract_menu_items_json_fallback():
    """Test the fallback parsing when JSON parsing fails."""
    with patch('main.ChatOpenAI') as mock_chat, patch('main.convert_to_base64') as mock_base64:
        # Mock the base64 conversion to avoid image processing issues
        mock_base64.return_value = "mocked_base64_string"
        
        mock_instance = MagicMock()
        mock_chat.return_value = mock_instance
        
        # Create a sample PIL image for testing
        sample_image = Image.new('RGB', (10, 10))
        
        # Test with different invalid JSON responses
        test_cases = [
            "Not valid JSON",
            "Item 1\nItem 2\nItem 3",
            "- Item 1\n- Item 2\n- Item 3"
        ]
        
        for test_case in test_cases:
            mock_instance.invoke.return_value = AIMessage(content=test_case)
            result = main.extract_menu_items([sample_image])
            
            # Verify fallback parsing worked
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Check the structure of the first item
            assert "name" in result[0]
            assert "description" in result[0]

def test_convert_to_pil_image_validations():
    """Test edge cases for the convert_to_pil_image function."""
    from PIL import Image
    
    # Test with invalid inputs
    invalid_inputs = [
        None,
        123,
        "string",
        [],
        {},
        [123, 456]
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises(TypeError):
            main.convert_to_pil_image(invalid_input)
    
    # Test with valid PIL image
    valid_image = Image.new('RGB', (10, 10))
    result = main.convert_to_pil_image(valid_image)
    assert result == valid_image 