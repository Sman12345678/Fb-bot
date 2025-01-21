import os
import google.generativeai as genai
import importlib
import logging
from dotenv import load_dotenv
from io import BytesIO
import requests
import urllib3
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# System instruction for text conversations
time_now = time.asctime(time.localtime(time.time()))
system_instruction = f"""
*System Name:* Your name is KORA AI, an AI Assistant created by Kolawole Suleiman. You are running on Sman V1.0.
*Owner:* Kolawole Suleiman
*Note:* Respond helpfully and informatively to a wide range of prompts and questions. Be professional and accurate. 
Today date is: {time_now}
"""

# Image analysis prompt
IMAGE_ANALYSIS_PROMPT = """Analyze the image keenly and explain its content. If it's text, translate it and identify the language used."""


def initialize_text_model():
    """Initialize Gemini text model."""
    genai.configure(api_key=os.getenv("GEMINI_TEXT_API_KEY"))
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 30,
            "max_output_tokens": 8192,
        }
    )


def initialize_image_model():
    """Initialize Gemini image model."""
    genai.configure(api_key=os.getenv("GEMINI_IMAGE_API_KEY"))
    return genai.GenerativeModel("gemini-1.5-pro")


def handle_text_message(user_message):
    """Process normal text messages."""
    try:
        logger.info("Processing text message: %s", user_message)
        
        # Initialize text model and start chat
        chat = initialize_text_model().start_chat(history=[])
        
        # Generate response
        response = chat.send_message(f"{system_instruction}\n\nHuman: {user_message}")
        return response.text
    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "😔 Sorry, I encountered an error processing your message."


def handle_text_command(command_name, message, author_id=None, thread_id=None, bot_client=None):
    """
    Handle text commands dynamically using modules in the CMD folder.
    Special logic for commands can also be added here, like '!leave'.
    """
    try:
        # Check if command module exists in CMD folder
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute(message, author_id, thread_id, bot_client)
    except ImportError:
        logger.warning("Command %s not found.", command_name)
        return "🚫 The Command you are using does not exist. Type !help to view available commands."
    except Exception as e:
        logger.error("Error executing command %s: %s", command_name, str(e))
        return "🚨 An error occurred while executing your command. Please try again."


def handle_attachment(attachment_data, attachment_type="image"):
    """
    Handle attachments (images) using Gemini's image processing model.
    """
    if attachment_type != "image":
        return "🚫 Unsupported attachment type. Please send an image."

    logger.info("Processing image attachment")
    
    try:
        # Upload to im.ge
        upload_url = "https://im.ge/api/1/upload"
        api_key = os.getenv('IMGE_API_KEY')

        files = {"source": ("attachment.jpg", attachment_data, "image/jpeg")}
        headers = {"X-API-Key": api_key}

        # Upload image
        upload_response = requests.post(upload_url, files=files, headers=headers, verify=False)
        upload_response.raise_for_status()

        # Get image URL
        image_url = upload_response.json()['image']['url']
        logger.info(f"Image uploaded successfully: {image_url}")

        # Download image for Gemini processing
        image_response = requests.get(image_url, verify=False)
        image_response.raise_for_status()
        image_data = BytesIO(image_response.content).getvalue()

        # Initialize image model and analyze
        model = initialize_image_model()
        response = model.generate_content([
            IMAGE_ANALYSIS_PROMPT,
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])

        return f"""🖼️ Image Analysis:
{response.text}

🔗 View Image: {image_url}"""

    except requests.RequestException as e:
        logger.error(f"Image upload/download error: {str(e)}")
        return "🚨 Error processing the image. Please try again later."
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return "🚨 Error analyzing the image. Please try again later."
