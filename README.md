# Menu Analyzer AI

An AI-powered menu analysis and recommendation system that extracts menu items from images and provides personalized dish recommendations based on interactive Q&A.

## Features

- **Menu Text Extraction**: Upload images of restaurant menus to extract dish names, descriptions, and prices.
- **Interactive Recommendation System**: Engage in a Q&A conversation to refine food preferences.
- **Personalized Dish Recommendations**: Receive tailored dish recommendations based on extracted menu items and conversation history.
- **Multi-language Support**: Get recommendations and conduct conversations in different languages.
- **Dual Interface**: Run as either an API server or with a Gradio web interface.


![MENU ANALYZER AI - Gradio UI](./images/gradio.png) 
![MENU ANALYZER AI - API SWAGGER](./images/swagger.png) 

## Requirements

- Python 3.12+
- uv package manager

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/menu-analyzer-ai.git
cd menu-analyzer-ai
```

2. Install dependencies using uv:

```bash
# Install project dependencies
uv sync
```

3. Setup environment variables:
   - Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_MODEL=gpt-4-turbo  # or your preferred model
   ```

## Running the Application

### Option 1: Run with Gradio Web Interface

The Gradio interface provides an interactive web UI for uploading menu images and getting recommendations.

```bash
uv run main.py --mode gradio
```

Additional options:
- `--port PORT`: Specify a custom port (default: 8000)
- `--host HOST`: Specify a custom host (default: 0.0.0.0)
- `--share`: Create a public URL for sharing the interface

Example:
```bash
uv run main.py --mode gradio --port 8080 --share
```

### Option 2: Run as API Server

The API server provides REST endpoints for programmatic access to the menu analyzer.

```bash
uv run main.py --mode api
```

Additional options:
- `--port PORT`: Specify a custom port (default: 8000)
- `--host HOST`: Specify a custom host (default: 0.0.0.0)

Example:
```bash
uv run main.py --mode api --port 8080
```

## Example Request/Response API

### Extract Menu Items

**Request**:
```bash
curl -X POST "http://localhost:8000/extract_menu" -F "files=@/path/to/menu_image.jpg"
```

**Response**:
```json
{
  "dishes": [
    {
      "name": "Ham & Bacon",
      "description": "Crispy bacon, ham, poached eggs, and hollandaise on toasted challah—rich, hearty, and satisfying for meat lovers.",
      "price": ""
    },
    {
      "name": "Pulled Beef",
      "description": "Poached eggs with grilled pulled beef, aubergine-aioli, and hollandaise—meaty, flavorful, and perfect for a heavy dish.",
      "price": ""
    }
  ]
}
```

### Next Question

**Request**:
```bash
curl -X POST "http://localhost:8000/next_question" \
  -H "Content-Type: application/json" \
  -d '{
    "dishes": [...],
    "qa": ["Would you prefer a lighter option?", "I prefer a more substantial dish, I am quite hungry."],
    "language": "en"
  }'
```

**Response**:
```json
{
  "question": "Would you like to add a side salad or any additional toppings to your main dish?"
}
```

### Recommendations

**Request**:
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "dishes": [...],
    "qa": ["Question 1?", "Answer 1", "Question 2?", "Answer 2"],
    "language": "en"
  }'
```

**Response**:
```json
{
  "recommendations": "1. Pulled Beef – Rich, hearty, and filling with tender beef and poached eggs, perfect for a substantial meal.\n2. Ham & Bacon – Satisfying and hearty, featuring crispy bacon, ham, and hollandaise on challah, ideal for meat lovers.\n3. French Fries – Crispy, classic side that complements the main dishes, adding extra satisfaction for a hungry guest."
}
```

## Testing

Run the included test client to verify the API functionality:

```bash
uv run test_client.py
```
