# Menu Analyzer AI

A smart restaurant menu assistant that helps you choose the perfect dish based on your preferences.

![Menu Analyzer in action](images/menu-screenshot.png)

## Overview

Menu Analyzer AI is an interactive tool that:
1. Analyzes restaurant menu photos
2. Asks you personalized questions about your preferences
3. Recommends the top 3 dishes tailored to your tastes

Perfect for tourists, food enthusiasts, or anyone facing decision paralysis when ordering!

## Features

- 📸 **Menu Photo Recognition**: Upload one or multiple menu photos
- 🔍 **Intelligent Extraction**: Automatically identifies dishes, descriptions, and prices
- 💬 **Interactive Q&A**: Answers 5 personalized questions to understand your preferences
- 🍽️ **Smart Recommendations**: Suggests 3 dishes ranked by how well they match your profile
- 🌐 **Multi-language Support**: Works in English, Arabic, German, Spanish, French, Persian, and Italian

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/menu-analyzer-ai.git
cd menu-analyzer-ai
```

2. Install the required dependencies:

using uv:
```bash
uv sync 
```

3. Create a `.env` file in the root directory with your OpenAI credentials:
```
OPENAI_API_KEY=your-api-key
OPENAI_API_MODEL=gpt-4.1-nano
```

## Usage

1. Start the application:
```bash
uv run main.py
```

2. Open the provided local URL in your browser (typically http://127.0.0.1:7860)

3. Upload menu photo(s)

4. Select your preferred language

5. Click "Start" to begin the conversation

6. Answer the assistant's questions honestly about your preferences

7. Receive personalized dish recommendations!


## Privacy

Your menu photos and conversation are processed via the OpenAI API but are not permanently stored.

