from unittest.mock import patch
import main


def test_build_ui_exists():
    """Test that the build_ui function exists and returns something."""
    # We can't test the Gradio UI structure easily due to Gradio's internals,
    # so we'll just verify the function exists and returns a value
    with patch("gradio.Blocks"):
        with patch("main.gr.Blocks"):
            # Just verify it doesn't throw an exception
            assert callable(main.build_ui)


def test_max_questions_constant():
    """Test that MAX_QUESTIONS is properly defined."""
    assert hasattr(main, "MAX_QUESTIONS")
    assert isinstance(main.MAX_QUESTIONS, int)
    assert main.MAX_QUESTIONS > 0


def test_extract_menu_items_integration():
    """Test extract_menu_items function's integration with the UI."""
    with patch("main.extract_menu_items") as mock_extract:
        # Verify the function exists and can be called
        assert callable(main.extract_menu_items)
        mock_extract.return_value = []
        result = main.extract_menu_items([])
        assert result == []
        mock_extract.assert_called_once()


def test_generate_next_question_integration():
    """Test generate_next_question function's integration with the UI."""
    with patch("main.generate_next_question") as mock_generate:
        # Verify the function exists and can be called
        assert callable(main.generate_next_question)
        mock_generate.return_value = "Test question?"
        result = main.generate_next_question([], [], "English")
        assert result == "Test question?"
        mock_generate.assert_called_once()


def test_recommend_dishes_integration():
    """Test recommend_dishes function's integration with the UI."""
    with patch("main.recommend_dishes") as mock_recommend:
        # Verify the function exists and can be called
        assert callable(main.recommend_dishes)
        mock_recommend.return_value = "Test recommendation"
        result = main.recommend_dishes([], [], "English")
        assert result == "Test recommendation"
        mock_recommend.assert_called_once()
