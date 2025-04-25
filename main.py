import base64
import os
import io
import json
import logging
from typing import List, Dict, Any
import gradio as gr
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)-5s| %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("menu_analyzer")

LLM_MODEL = os.getenv("OPENAI_API_MODEL")
MAX_QUESTIONS = 5
MAX_MENU_ITEMS = 50

# === HELPER FUNCTIONS ===

def convert_to_pil_image(image_input):
    if isinstance(image_input, Image.Image):
        return image_input
    if isinstance(image_input, (list, tuple)) and image_input and isinstance(image_input[0], Image.Image):
        return image_input[0]
    raise TypeError("Unsupported image type from Gallery")


def convert_to_base64(image):
    buffer = io.BytesIO()
    convert_to_pil_image(image).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


# === LLM WRAPPERS ===


def extract_menu_items(menu_images: List[Any]) -> List[Dict[str, str]]:
    if not menu_images:
        logger.warning("No menu images provided for extraction")
        return []
    
    logger.info(f"Processing {len(menu_images)} menu images for extraction")
    image_parts = [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{convert_to_base64(img)}"}}
        for img in menu_images[:MAX_QUESTIONS]
    ]
    system_message = SystemMessage(
        content=("""
            You are an advanced menu parser. From one or more restaurant-menu photos, output ONLY a raw minified JSON array where each element has: 
            `name`, `description` - **every textual or symbolic detail** that accompanies the dish: ingredients, cooking style, allergens, icons (e.g. 🌶️ for spicy, 🥦 vegetarian), dietary_tags,calories, region, side notes, etc. Consolidate them into one sentence in the _original menu language. `price` (string with currency)
                 """
        )
    )
    human_message = HumanMessage(content=[*image_parts, {"type": "text", "text": "Extract now."}])
    
    logger.info("Calling LLM to extract menu items")
    try:
        response_text = ChatOpenAI(model=LLM_MODEL, temperature=0).invoke([system_message, human_message]).content
        menu_items = json.loads(response_text)[:MAX_MENU_ITEMS]
        logger.info(f"Successfully extracted {len(menu_items)} menu items")
        return menu_items
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON response, falling back to line-by-line parsing")
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


def generate_next_question(dishes: List[Dict[str, str]], question_answer_history: List[str], language: str) -> str:
    question_number = len(question_answer_history) // 2 + 1
    logger.info(f"Generating question #{question_number} in {language}")
    
    menu_summary = "; ".join(f"{dish['name']}: {dish.get('description', '')}" for dish in dishes)
    conversation_history = "\n".join(
        f"Q{i + 1}: {question}\nA{i + 1}: {answer}"
        for i, (question, answer) in enumerate(zip(question_answer_history[0::2], question_answer_history[1::2]))
    )
    system_message = SystemMessage(content=f"Reply ONLY in {language} as an attentive waiter.")
    prompt_text = (
        f"Menu excerpt: {menu_summary}.\n{conversation_history}\n"
        "Ask ONE concise new question that targets an undecided preference. Avoid repeating topics. Return only the sentence."
    )
    
    try:
        question_response = (
            ChatOpenAI(model=LLM_MODEL, temperature=0.6)
            .invoke([system_message, HumanMessage(content=prompt_text)])
            .content.strip()
        )
        if not question_response.endswith("?"):
            question_response += "?"
        logger.info(f"Generated question: {question_response[:50]}...")
        return question_response
    except Exception as e:
        logger.error(f"Error generating question: {str(e)}")
        return "What would you like to eat today?"


def recommend_dishes(dishes: List[Dict[str, str]], question_answer_history: List[str], language: str) -> str:
    logger.info(f"Generating dish recommendations in {language} based on {len(dishes)} dishes and {len(question_answer_history)//2} Q&A pairs")
    
    user_answers = question_answer_history[1::2]
    formatted_menu = "\n".join(f"- {dish['name']}: {dish.get('description', '')}" for dish in dishes)
    user_profile = "\n".join(f"A{i + 1}: {answer}" for i, answer in enumerate(user_answers))
    system_message = SystemMessage(content=f"Reply ONLY in {language} as a helpful waiter.")
    prompt_text = (
        "Using the menu and guest profile, pick the TOP 3 matching dishes (ranked) and justify each in ≤30 words. Respond markdown.\n\n"
        f"Menu:\n{formatted_menu}\n\nGuest:\n{user_profile}"
    )
    
    try:
        response = (
            ChatOpenAI(model=LLM_MODEL, temperature=0.4)
            .invoke([system_message, HumanMessage(content=prompt_text)])
            .content
        )
        logger.info("Successfully generated dish recommendations")
        return response
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return "I apologize, but I couldn't generate recommendations at this time."


# === USER INTERFACE ===


def build_ui():
    with gr.Blocks(
        css="footer{display:none}; .gradio-container{max-width:900px;margin:auto}"
    ) as demo:
        gr.Markdown("### 📸 Not Sure What to Order? Let AI Recommend!")
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                menu_gallery = gr.Gallery(
                    label="Menu photo(s)", type="pil", height=600
                )
                language_dropdown = gr.Dropdown(
                    label="Language",
                    choices=[
                        "English",
                        "فارسی",
                        "Deutsch",
                        "Español",
                        "Français",
                        "العربية",
                        "Italiano",
                    ],
                    value="English",
                )
                start_button = gr.Button("Start", variant="primary")
                
            with gr.Column(scale=2):
                chat_interface = gr.Chatbot(height=700, show_copy_button=True)
                with gr.Row():
                    user_input = gr.Textbox(
                        show_label=False,
                        placeholder="Type answer & press Enter",
                        container=False,
                        scale=5,
                    )
                    send_button = gr.Button("Send", scale=1)

        app_state = gr.State(
            value={"stage": "await", "lang": "English", "dishes": [], "qa": []}
        )

        def initialize_conversation(selected_language, menu_images, current_state):
            logger.info(f"Initializing conversation in {selected_language}")
            current_state.update(lang=selected_language)
            
            if not menu_images:
                logger.warning("No menu images provided")
                return gr.Warning("Please upload menu photo(s)."), current_state
                
            extracted_dishes = extract_menu_items(menu_images)
            if not extracted_dishes:
                logger.warning("No dishes could be extracted from images")
                return gr.Warning("Couldn't parse dishes."), current_state
                
            logger.info(f"Successfully extracted {len(extracted_dishes)} dishes")
            first_question = generate_next_question(extracted_dishes, [], selected_language)
            current_state.update(stage="asking", dishes=extracted_dishes, qa=[first_question])
            logger.info("Conversation initialized successfully")
            return gr.update(value=[[None, first_question]]), current_state

        start_button.click(initialize_conversation, [language_dropdown, menu_gallery, app_state], [chat_interface, app_state])

        def process_conversation(user_message, current_state):
            if current_state["stage"] != "asking":
                logger.debug("Ignoring input - conversation not in asking stage")
                return current_state, gr.update()
                
            logger.info("Processing user response")
            question_answer_list = current_state["qa"] + [user_message]
            current_state["qa"] = question_answer_list
            
            if len(question_answer_list) // 2 >= MAX_QUESTIONS:
                logger.info(f"Reached max questions ({MAX_QUESTIONS}), generating final recommendations")
                bot_response = recommend_dishes(current_state["dishes"], question_answer_list, current_state["lang"])
                current_state["stage"] = "done"
                logger.info("Conversation completed")
            else:
                question_number = len(question_answer_list) // 2 + 1
                logger.info(f"Generating question {question_number}/{MAX_QUESTIONS}")
                bot_response = generate_next_question(current_state["dishes"], question_answer_list, current_state["lang"])
                
            question_answer_list.append(bot_response)
            conversation_pairs = [[None, question_answer_list[0]]] + [[question_answer_list[i], question_answer_list[i + 1]] for i in range(1, len(question_answer_list), 2)]
            return current_state, gr.update(value=conversation_pairs)

        user_input.submit(process_conversation, [user_input, app_state], [app_state, chat_interface]).then(
            lambda: "", None, user_input
        )
        send_button.click(process_conversation, [user_input, app_state], [app_state, chat_interface]).then(
            lambda: "", None, user_input
        )
    return demo


if __name__ == "__main__":
    logger.info("Starting Menu Analyzer AI application")
    if "OPENAI_API_KEY" not in os.environ:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise EnvironmentError("Set OPENAI_API_KEY")
    
    logger.info(f"Using LLM model: {LLM_MODEL or 'default'}")
    logger.info("Launching Gradio interface")
    build_ui().launch()
