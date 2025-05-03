import json
from langchain.schema import AIMessage
import main


class TestExtractMenuItems:
    def test_extract_menu_items_success(self, sample_image_list, mock_openai):
        """Test successful extraction of menu items."""
        # Sample menu items that would be returned by the LLM
        sample_menu_items = [
            {
                "name": "Pasta Carbonara",
                "description": "Pasta with eggs, cheese, pancetta, and pepper",
                "price": "$12.99",
            },
            {
                "name": "Caesar Salad",
                "description": "Romaine lettuce with Caesar dressing and croutons",
                "price": "$8.99",
            },
        ]

        # Mock the LLM response
        mock_instance = mock_openai.return_value
        mock_instance.invoke.return_value = AIMessage(
            content=json.dumps(sample_menu_items)
        )

        # Call the function
        result = main.extract_menu_items(sample_image_list)

        # Assert the function was called with the right arguments
        mock_openai.assert_called_once()

        # Assert the result matches our sample data
        assert result == sample_menu_items
        assert len(result) == 2
        assert result[0]["name"] == "Pasta Carbonara"
        assert result[1]["name"] == "Caesar Salad"

    def test_extract_menu_items_empty_input(self):
        """Test extract_menu_items with empty input."""
        result = main.extract_menu_items([])
        assert result == []

    def test_extract_menu_items_json_error(self, sample_image_list, mock_openai):
        """Test extract_menu_items with a JSON parsing error."""
        # Mock a response that will cause a JSONDecodeError
        mock_instance = mock_openai.return_value
        mock_instance.invoke.return_value = AIMessage(content="This is not valid JSON")

        # Call the function
        result = main.extract_menu_items(sample_image_list)

        # Assert that the fallback parsing worked
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "This is not valid JSON"

    def test_extract_menu_items_exception(self, sample_image_list, mock_openai):
        """Test extract_menu_items with a general exception."""
        # Mock to raise an exception
        mock_instance = mock_openai.return_value
        mock_instance.invoke.side_effect = Exception("Test exception")

        # Call the function
        result = main.extract_menu_items(sample_image_list)

        # Assert an empty list is returned
        assert result == []


class TestGenerateNextQuestion:
    def test_generate_next_question(self, mock_openai):
        """Test generating a next question."""
        # Sample data
        dishes = [{"name": "Pasta", "description": "Italian dish"}]
        qa_history = ["What cuisine do you prefer?", "I like Italian"]
        language = "English"

        # Mock response
        mock_instance = mock_openai.return_value
        mock_instance.invoke.return_value = AIMessage(
            content="Would you prefer a vegetarian option?"
        )

        # Call the function
        result = main.generate_next_question(dishes, qa_history, language)

        # Assert
        assert result == "Would you prefer a vegetarian option?"
        mock_openai.assert_called_once()

    def test_generate_next_question_no_question_mark(self, mock_openai):
        """Test generating a next question without a question mark."""
        # Sample data
        dishes = [{"name": "Pasta", "description": "Italian dish"}]
        qa_history = []
        language = "English"

        # Mock response without question mark
        mock_instance = mock_openai.return_value
        mock_instance.invoke.return_value = AIMessage(
            content="Tell me about your dietary preferences"
        )

        # Call the function
        result = main.generate_next_question(dishes, qa_history, language)

        # Assert question mark is added
        assert result == "Tell me about your dietary preferences?"

    def test_generate_next_question_exception(self, mock_openai):
        """Test generating a next question with an exception."""
        # Sample data
        dishes = [{"name": "Pasta", "description": "Italian dish"}]
        qa_history = []
        language = "English"

        # Mock exception
        mock_instance = mock_openai.return_value
        mock_instance.invoke.side_effect = Exception("Test exception")

        # Call the function
        result = main.generate_next_question(dishes, qa_history, language)

        # Assert default question is returned
        assert result == "What would you like to eat today?"


class TestRecommendDishes:
    def test_recommend_dishes(self, mock_openai):
        """Test recommending dishes."""
        # Sample data
        dishes = [
            {"name": "Pasta", "description": "Italian dish"},
            {"name": "Pizza", "description": "Another Italian favorite"},
        ]
        qa_history = ["Do you like Italian food?", "Yes, I love it!"]
        language = "English"

        # Mock response
        expected_recommendation = "1. Pasta - Perfect Italian dish for pasta lovers.\n2. Pizza - Classic choice for Italian cuisine enthusiasts."
        mock_instance = mock_openai.return_value
        mock_instance.invoke.return_value = AIMessage(content=expected_recommendation)

        # Call the function
        result = main.recommend_dishes(dishes, qa_history, language)

        # Assert
        assert result == expected_recommendation
        mock_openai.assert_called_once()

    def test_recommend_dishes_exception(self, mock_openai):
        """Test recommending dishes with an exception."""
        # Sample data
        dishes = [{"name": "Pasta", "description": "Italian dish"}]
        qa_history = []
        language = "English"

        # Mock exception
        mock_instance = mock_openai.return_value
        mock_instance.invoke.side_effect = Exception("Test exception")

        # Call the function
        result = main.recommend_dishes(dishes, qa_history, language)

        # Assert error message is returned
        assert "I apologize" in result
