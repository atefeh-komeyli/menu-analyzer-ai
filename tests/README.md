# Menu Analyzer AI - Test Suite

This directory contains tests for the Menu Analyzer AI application.

## Test Structure

The test suite is organized into the following files:

- `conftest.py`: Contains pytest fixtures shared across test files
- `test_helpers.py`: Tests for helper functions (image conversion, base64 encoding)
- `test_llm_wrappers.py`: Tests for LLM wrapper functions (menu extraction, question generation, recommendations)
- `test_ui.py`: Basic tests for UI components
- `test_env.py`: Tests for environment variables and application constants
- `test_validation.py`: Tests for input validation and error handling

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run a specific test file:

```bash
python -m pytest tests/test_helpers.py
```

To run a specific test:

```bash
python -m pytest tests/test_helpers.py::test_convert_to_base64
```

To run tests with verbose output:

```bash
python -m pytest -v
```

## Test Coverage

The tests cover:

1. **Helper Functions**
   - Image conversion
   - Base64 encoding

2. **LLM Interactions**
   - Menu item extraction
   - Question generation
   - Dish recommendations

3. **Error Handling**
   - JSON parsing errors
   - LLM exceptions
   - Input validation

4. **Configuration**
   - Environment variables
   - Application constants

## Mocking Strategy

The tests use the `unittest.mock` module to mock:

1. OpenAI API calls via the `ChatOpenAI` class
2. Image processing to avoid actual image operations
3. Environment variables to test configuration

This ensures tests can run quickly and without external dependencies. 