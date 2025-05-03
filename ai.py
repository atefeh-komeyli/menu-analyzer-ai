import base64
import os
import io
import json
import logging
from typing import List, Dict, Any
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# CONFIGURE LOGGING
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)-5s| %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("menu_analyzer")

LLM_MODEL = os.getenv("OPENAI_API_MODEL")
MAX_QUESTIONS = 5
MAX_MENU_ITEMS = 100


# HELPER FUNCTIONS
def convert_to_pil_image(image_input):
    if isinstance(image_input, Image.Image):
        return image_input
    if (
        isinstance(image_input, (list, tuple))
        and image_input
        and isinstance(image_input[0], Image.Image)
    ):
        return image_input[0]
    raise TypeError("Unsupported image type from Gallery")


def convert_to_base64(image):
    buffer = io.BytesIO()
    convert_to_pil_image(image).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


# LLM WRAPPERS
def extract_menu_items(menu_images: List[Any]) -> List[Dict[str, str]]:
    if not menu_images:
        logger.warning("No menu images provided for extraction")
        return []

    logger.info(f"Processing {len(menu_images)} menu images for extraction")
    image_parts = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{convert_to_base64(img)}"},
        }
        for img in menu_images[:MAX_QUESTIONS]
    ]
    system_message = SystemMessage(
        content=(
            """
            You are an advanced menu parser. From one or more restaurant-menu photos, output ONLY a raw minified JSON array where each element has: 
            `name`, `description` - **every textual or symbolic detail** that accompanies the dish: ingredients, cooking style, allergens, icons (e.g. 🌶️ for spicy, 🥦 vegetarian), dietary_tags,calories, region, side notes, etc. Consolidate them into one sentence in the _original menu language. `price` (string with currency)
                 """
        )
    )
    human_message = HumanMessage(
        content=[*image_parts, {"type": "text", "text": "Extract now."}]
    )

    logger.info("Calling LLM to extract menu items")
    try:
        response_text = (
            ChatOpenAI(model=LLM_MODEL, temperature=0)
            .invoke([system_message, human_message])
            .content
        )
        menu_items = json.loads(response_text)[:MAX_MENU_ITEMS]
        logger.info(f"Successfully extracted {len(menu_items)} menu items")
        return menu_items
    except json.JSONDecodeError:
        logger.warning(
            "Failed to parse JSON response, falling back to line-by-line parsing"
        )
        parsed_items = [
            {"name": line.strip("- •"), "description": ""}
            for line in response_text.split("\n")
            if line.strip()
        ][:MAX_MENU_ITEMS]
        logger.info(f"Extracted {len(parsed_items)} items using fallback method")
        return parsed_items
    except Exception as e:
        logger.error(f"Error extracting menu items: {str(e)}")
        return []


def generate_next_question(
    dishes: List[Dict[str, str]], question_answer_history: List[str], language: str
) -> str:
    question_number = len(question_answer_history) // 2 + 1
    logger.info(f"Generating question #{question_number} in {language}")

    menu_summary = "; ".join(
        f"{dish['name']}: {dish.get('description', '')}" for dish in dishes
    )
    conversation_history = "\n".join(
        f"Q{i + 1}: {question}\nA{i + 1}: {answer}"
        for i, (question, answer) in enumerate(
            zip(question_answer_history[0::2], question_answer_history[1::2])
        )
    )
    system_message = SystemMessage(
        content=f"Reply ONLY in {language} as an attentive waiter."
    )
    prompt_text = (
        f"Menu excerpt: {menu_summary}.\n{conversation_history}\n"
        "Ask ONE concise new question that targets an undecided preference. Avoid repeating topics. Return only the sentence."
    )

    question_response = (
        ChatOpenAI(model=LLM_MODEL, temperature=0.6)
        .invoke([system_message, HumanMessage(content=prompt_text)])
        .content.strip()
    )
    logger.info(f"Generated question: {question_response[:50]}...")
    return question_response


def recommend_dishes(
    dishes: List[Dict[str, str]], question_answer_history: List[str], language: str
) -> str:
    logger.info(
        f"Generating dish recommendations in {language} based on {len(dishes)} dishes and {len(question_answer_history) // 2} Q&A pairs"
    )

    user_answers = question_answer_history[1::2]
    formatted_menu = "\n".join(
        f"- {dish['name']}: {dish.get('description', '')}" for dish in dishes
    )
    user_profile = "\n".join(
        f"A{i + 1}: {answer}" for i, answer in enumerate(user_answers)
    )
    system_message = SystemMessage(
        content=f"Reply ONLY in {language} as a helpful waiter."
    )
    prompt_text = (
        "Using the menu and guest profile, pick the TOP 3 matching dishes (ranked) and justify each in ≤30 words. Respond markdown without backticks and without any beginning or ending notes.\n\n"
        f"Menu:\n{formatted_menu}\n\nGuest:\n{user_profile}"
    )

    response = (
        ChatOpenAI(model=LLM_MODEL, temperature=0.4)
        .invoke([system_message, HumanMessage(content=prompt_text)])
        .content
    )
    logger.info("Successfully generated dish recommendations")
    return response


if __name__ == "__main__":
    logger.info("Starting Menu Analyzer AI application")
    if "OPENAI_API_KEY" not in os.environ:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise EnvironmentError("Set OPENAI_API_KEY")

    logger.info(f"Using LLM model: {LLM_MODEL or 'default'}")
    logger.info("Launching Gradio interface")
    # Import here to avoid circular imports
    from gradio_ui import build_ui

    build_ui().launch()
