import pytest
import requests
import os
from unittest.mock import patch, MagicMock

# API base URL - allow overriding from environment variable
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def api_base_url():
    """Return the base URL for the API."""
    # Check if the API is available
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            return BASE_URL
        else:
            pytest.skip(f"API health check failed: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        pytest.skip(f"Could not connect to the API at {BASE_URL}. Make sure the API server is running.")


@pytest.fixture
def sample_menu_image():
    """Return a path to a sample menu image."""
    image_path = "images/sample_menu.png"
    if not os.path.exists(image_path):
        pytest.skip(f"Sample menu image not found at {image_path}")
    return image_path


@pytest.fixture
def mock_api_responses():
    """Mock responses for API tests without hitting real endpoints."""
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        # Configure mock responses
        mock_health = MagicMock()
        mock_health.status_code = 200
        mock_health.json.return_value = {"status": "ok", "model": "test-model"}
        mock_get.return_value = mock_health

        # Extract menu mock
        mock_extract = MagicMock()
        mock_extract.status_code = 200
        mock_extract.json.return_value = {
            "dishes": [
                {"name": "Test Dish 1", "description": "A test dish", "price": "$10.00"},
                {"name": "Test Dish 2", "description": "Another test dish", "price": "$12.00"}
            ]
        }

        # Next question mock
        mock_question = MagicMock()
        mock_question.status_code = 200
        mock_question.json.return_value = {"question": "Would you prefer something spicy?"}

        # Recommendations mock
        mock_recommend = MagicMock()
        mock_recommend.status_code = 200
        mock_recommend.json.return_value = {
            "recommendations": "1. Test Dish 1 - Perfect for testing.\n2. Test Dish 2 - Another great option."
        }

        # Error mock
        mock_error = MagicMock()
        mock_error.status_code = 400
        mock_error.json.return_value = {"detail": "Invalid input data"}

        # Server error mock
        mock_server_error = MagicMock()
        mock_server_error.status_code = 500
        mock_server_error.json.return_value = {"detail": "Internal server error"}

        # Configure mock_post to return different responses based on URL path
        def side_effect(url, **kwargs):
            if "/extract_menu" in url:
                # Check for error conditions
                if not kwargs.get("files"):
                    return mock_error
                return mock_extract
            elif "/next_question" in url:
                # Check payload for error conditions
                payload = kwargs.get("json", {})
                if not payload.get("dishes"):
                    return mock_error
                # Handle different languages
                if payload.get("language") == "es":
                    mock_lang = MagicMock()
                    mock_lang.status_code = 200
                    mock_lang.json.return_value = {"question": "¿Prefieres algo picante?"}
                    return mock_lang
                return mock_question
            elif "/recommend" in url:
                # Check payload for error conditions
                payload = kwargs.get("json", {})
                if not payload.get("dishes") or not payload.get("qa"):
                    return mock_error
                return mock_recommend
            return MagicMock(status_code=404)

        mock_post.side_effect = side_effect
        yield mock_post, mock_get


# To run real API tests, exclude the mock_api_responses fixture
def test_health_check(api_base_url):
    """Test the health check endpoint."""
    response = requests.get(f"{api_base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model" in data
    
    # Verify the format of the returned JSON
    assert isinstance(data, dict)
    assert len(data) >= 2
    assert isinstance(data["status"], str)
    assert isinstance(data["model"], str)


# Mock-based tests 
def test_extract_menu_mocked(mock_api_responses):
    """Test the extract_menu endpoint with mocked responses."""
    mock_post, _ = mock_api_responses
    
    # Use any file as placeholder, the request is mocked
    files = [("files", ("sample_menu.png", open("tests/conftest.py", "rb"), "image/png"))]
    response = requests.post(f"{BASE_URL}/extract_menu", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "dishes" in data
    assert len(data["dishes"]) == 2
    assert data["dishes"][0]["name"] == "Test Dish 1"
    
    # Verify the mock was called correctly
    mock_post.assert_called_once()
    args, _ = mock_post.call_args
    assert "/extract_menu" in args[0]


def test_extract_menu_no_files(mock_api_responses):
    """Test the extract_menu endpoint with no files (should error)."""
    mock_post, _ = mock_api_responses
    
    # No files provided
    response = requests.post(f"{BASE_URL}/extract_menu", files=[])
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Invalid" in data["detail"]


def test_next_question_mocked(mock_api_responses):
    """Test the next_question endpoint with mocked responses."""
    mock_post, _ = mock_api_responses
    
    payload = {
        "dishes": [{"name": "Test Dish", "description": "A test dish", "price": "$10.00"}],
        "qa": ["What do you like?", "I like spicy food"],
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/next_question", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert data["question"] == "Would you prefer something spicy?"
    
    # Verify the mock was called correctly
    assert mock_post.call_count == 1
    args, kwargs = mock_post.call_args
    assert "/next_question" in args[0]
    assert kwargs["json"] == payload


def test_next_question_spanish(mock_api_responses):
    """Test the next_question endpoint with Spanish language."""
    mock_post, _ = mock_api_responses
    
    payload = {
        "dishes": [{"name": "Test Dish", "description": "A test dish", "price": "$10.00"}],
        "qa": ["What do you like?", "I like spicy food"],
        "language": "es"
    }
    
    response = requests.post(f"{BASE_URL}/next_question", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert data["question"] == "¿Prefieres algo picante?"
    
    # Verify the mock was called correctly
    assert mock_post.call_count == 1
    args, kwargs = mock_post.call_args
    assert "/next_question" in args[0]
    assert kwargs["json"]["language"] == "es"


def test_next_question_invalid_payload(mock_api_responses):
    """Test the next_question endpoint with invalid payload."""
    mock_post, _ = mock_api_responses
    
    # Missing dishes
    payload = {
        "qa": ["What do you like?", "I like spicy food"],
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/next_question", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_recommend_mocked(mock_api_responses):
    """Test the recommend endpoint with mocked responses."""
    mock_post, _ = mock_api_responses
    
    payload = {
        "dishes": [{"name": "Test Dish", "description": "A test dish", "price": "$10.00"}],
        "qa": ["What do you like?", "I like spicy food"],
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "Test Dish 1" in data["recommendations"]
    
    # Verify the mock was called correctly
    assert mock_post.call_count == 1
    args, kwargs = mock_post.call_args
    assert "/recommend" in args[0]
    assert kwargs["json"] == payload


def test_recommend_invalid_payload(mock_api_responses):
    """Test the recommend endpoint with invalid payload."""
    mock_post, _ = mock_api_responses
    
    # Missing dishes
    payload = {
        "qa": ["What do you like?", "I like spicy food"],
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_recommend_empty_qa(mock_api_responses):
    """Test the recommend endpoint with empty QA history."""
    mock_post, _ = mock_api_responses
    
    payload = {
        "dishes": [{"name": "Test Dish", "description": "A test dish", "price": "$10.00"}],
        "qa": [],
        "language": "en"
    }
    
    response = requests.post(f"{BASE_URL}/recommend", json=payload)
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


# Real API tests - will be skipped if API is not available
def test_extract_menu_real(api_base_url, sample_menu_image):
    """Test the extract_menu endpoint with real API and image."""
    # Skip for CI or when API is not running
    if os.getenv("CI") == "true":
        pytest.skip("Skipping real API test in CI environment")
        
    files = [("files", (os.path.basename(sample_menu_image), 
                       open(sample_menu_image, "rb"), "image/png"))]
                   
    response = requests.post(f"{api_base_url}/extract_menu", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "dishes" in data
    assert len(data["dishes"]) > 0
    # Verify the structure of each dish
    for dish in data["dishes"]:
        assert "name" in dish
        assert "description" in dish
        assert "price" in dish


def test_next_question_real(api_base_url, sample_menu_image):
    """Test the next_question endpoint with real API."""
    # Skip for CI or when API is not running
    if os.getenv("CI") == "true":
        pytest.skip("Skipping real API test in CI environment")
    
    # First extract the menu
    files = [("files", (os.path.basename(sample_menu_image), 
                       open(sample_menu_image, "rb"), "image/png"))]
    extract_response = requests.post(f"{api_base_url}/extract_menu", files=files)
    assert extract_response.status_code == 200
    
    dishes = extract_response.json()["dishes"]
    
    # Then get a question
    payload = {
        "dishes": dishes, 
        "qa": [], 
        "language": "en"
    }
    
    response = requests.post(f"{api_base_url}/next_question", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert len(data["question"]) > 0


def test_recommend_real(api_base_url, sample_menu_image):
    """Test the recommend endpoint with real API."""
    # Skip for CI or when API is not running
    if os.getenv("CI") == "true":
        pytest.skip("Skipping real API test in CI environment")
    
    # First extract the menu
    files = [("files", (os.path.basename(sample_menu_image), 
                       open(sample_menu_image, "rb"), "image/png"))]
    extract_response = requests.post(f"{api_base_url}/extract_menu", files=files)
    assert extract_response.status_code == 200
    
    dishes = extract_response.json()["dishes"]
    
    # Create a simple Q&A history
    qa_history = ["Do you have any dietary restrictions?", "I'm vegetarian"]
    
    # Then get recommendations
    payload = {
        "dishes": dishes, 
        "qa": qa_history, 
        "language": "en"
    }
    
    response = requests.post(f"{api_base_url}/recommend", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0


def test_api_conversation_flow(mock_api_responses):
    """Test a complete conversation flow using the API."""
    mock_post, _ = mock_api_responses
    
    # 1. Extract menu items 
    files = [("files", ("sample_menu.png", open("tests/conftest.py", "rb"), "image/png"))]
    extract_response = requests.post(f"{BASE_URL}/extract_menu", files=files)
    assert extract_response.status_code == 200
    dishes = extract_response.json()["dishes"]
    
    # 2. Get first question
    qa_history = []
    question_payload = {"dishes": dishes, "qa": qa_history, "language": "en"}
    q1_response = requests.post(f"{BASE_URL}/next_question", json=question_payload)
    assert q1_response.status_code == 200
    q1 = q1_response.json()["question"]
    qa_history.extend([q1, "I prefer spicy food"])
    
    # 3. Get second question
    question_payload = {"dishes": dishes, "qa": qa_history, "language": "en"}
    q2_response = requests.post(f"{BASE_URL}/next_question", json=question_payload)
    assert q2_response.status_code == 200
    q2 = q2_response.json()["question"]
    qa_history.extend([q2, "I eat meat"])
    
    # 4. Get recommendations
    recommend_payload = {"dishes": dishes, "qa": qa_history, "language": "en"}
    rec_response = requests.post(f"{BASE_URL}/recommend", json=recommend_payload)
    assert rec_response.status_code == 200
    recommendations = rec_response.json()["recommendations"]
    assert recommendations
    
    # Verify the correct number of API calls were made
    assert mock_post.call_count == 4


def test_api_conversation_flow_real(api_base_url, sample_menu_image):
    """Test a complete conversation flow using the real API."""
    # Skip for CI or when API is not running
    if os.getenv("CI") == "true":
        pytest.skip("Skipping real API test in CI environment")
    
    # 1. Extract menu items
    files = [("files", (os.path.basename(sample_menu_image), 
                       open(sample_menu_image, "rb"), "image/png"))]
    extract_response = requests.post(f"{api_base_url}/extract_menu", files=files)
    assert extract_response.status_code == 200
    dishes = extract_response.json()["dishes"]
    
    # 2. Get first question
    qa_history = []
    question_payload = {"dishes": dishes, "qa": qa_history, "language": "en"}
    q1_response = requests.post(f"{api_base_url}/next_question", json=question_payload)
    assert q1_response.status_code == 200
    q1 = q1_response.json()["question"]
    qa_history.extend([q1, "I prefer vegetarian options"])
    
    # 3. Get second question
    question_payload = {"dishes": dishes, "qa": qa_history, "language": "en"}
    q2_response = requests.post(f"{api_base_url}/next_question", json=question_payload)
    assert q2_response.status_code == 200
    q2 = q2_response.json()["question"]
    qa_history.extend([q2, "I like spicy food"])
    
    # 4. Get recommendations
    recommend_payload = {"dishes": dishes, "qa": qa_history, "language": "en"}
    rec_response = requests.post(f"{api_base_url}/recommend", json=recommend_payload)
    assert rec_response.status_code == 200
    recommendations = rec_response.json()["recommendations"]
    assert recommendations
    assert len(recommendations) > 0


def test_nonexistent_endpoint(mock_api_responses):
    """Test a non-existent endpoint."""
    mock_post, mock_get = mock_api_responses
    
    # Configure mock_get to return 404 for nonexistent endpoints
    mock_not_found = MagicMock()
    mock_not_found.status_code = 404
    mock_not_found.json.return_value = {"detail": "Not Found"}
    
    def side_effect(url, **kwargs):
        if "/health" in url:
            return mock_get.return_value
        return mock_not_found
    
    mock_get.side_effect = side_effect
    
    response = requests.get(f"{BASE_URL}/nonexistent")
    assert response.status_code == 404
    assert "detail" in response.json() 