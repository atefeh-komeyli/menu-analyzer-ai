import logging
import sys
import importlib.util
from ai import extract_menu_items, generate_next_question, recommend_dishes


# CONFIGURE LOGGING
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)-5s| %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("menu_analyzer")

real_gradio_spec = importlib.util.find_spec("gradio", None)
for path in sys.path:
    if "__pycache__" in path or "/menu-analyzer-ai" in path:
        continue
    try:
        real_gradio_spec = importlib.util.find_spec("gradio", [path])
        if real_gradio_spec:
            break
    except (ImportError, AttributeError):
        continue

if real_gradio_spec:
    real_gradio = importlib.util.module_from_spec(real_gradio_spec)
    real_gradio_spec.loader.exec_module(real_gradio)
    gr = real_gradio
else:
    # Fallback
    import gradio as gr

# Constants
MAX_QUESTIONS = 5


# USER INTERFACE
def build_ui():
    with gr.Blocks(
        css="footer{display:none}; .gradio-container{max-width:900px;margin:auto}"
    ) as demo:
        gr.Markdown("### 📸 Not Sure What to Order? Let AI Recommend!")
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                menu_gallery = gr.Gallery(label="Menu photo(s)", type="pil", height=600)
                language_dropdown = gr.Dropdown(
                    label="Conversation language",
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
                chat_interface = gr.Chatbot(height=700)
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
            first_question = generate_next_question(
                extracted_dishes, [], selected_language
            )
            current_state.update(
                stage="asking", dishes=extracted_dishes, qa=[first_question]
            )
            logger.info("Conversation initialized successfully")
            return gr.update(value=[[None, first_question]]), current_state

        start_button.click(
            initialize_conversation,
            [language_dropdown, menu_gallery, app_state],
            [chat_interface, app_state],
        )

        def process_conversation(user_message, current_state):
            if current_state["stage"] != "asking":
                logger.debug("Ignoring input - conversation not in asking stage")
                return current_state, gr.update()

            logger.info("Processing user response")
            question_answer_list = current_state["qa"] + [user_message]
            current_state["qa"] = question_answer_list

            if len(question_answer_list) // 2 >= MAX_QUESTIONS:
                logger.info(
                    f"Reached max questions ({MAX_QUESTIONS}), generating final recommendations"
                )
                bot_response = recommend_dishes(
                    current_state["dishes"], question_answer_list, current_state["lang"]
                )
                current_state["stage"] = "done"
                logger.info("Conversation completed")
            else:
                question_number = len(question_answer_list) // 2 + 1
                logger.info(f"Generating question {question_number}/{MAX_QUESTIONS}")
                bot_response = generate_next_question(
                    current_state["dishes"], question_answer_list, current_state["lang"]
                )

            question_answer_list.append(bot_response)
            conversation_pairs = [[None, question_answer_list[0]]] + [
                [question_answer_list[i], question_answer_list[i + 1]]
                for i in range(1, len(question_answer_list), 2)
            ]
            return current_state, gr.update(value=conversation_pairs)

        user_input.submit(
            process_conversation, [user_input, app_state], [app_state, chat_interface]
        ).then(lambda: "", None, user_input)
        send_button.click(
            process_conversation, [user_input, app_state], [app_state, chat_interface]
        ).then(lambda: "", None, user_input)
    return demo
