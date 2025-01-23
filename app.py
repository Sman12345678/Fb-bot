
import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv
from fbchat import Client
from fbchat.models import Message, ThreadType
import messageHandler

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KORA-Bot")

# Facebook credentials
FB_EMAIL = os.getenv("FB_EMAIL")
FB_PASSWORD = os.getenv("FB_PASSWORD")
BOT_OWNER_ID = os.getenv("BOT_OWNER_ID")

# Initialize fbchat client
class KoraBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        try:
            # Avoid responding to the bot's own messages
            if author_id == self.uid:
                return

            logger.info(f"Message from {author_id}: {message_object.text}")

            # Check if the message starts with a prefix for a command
            if message_object.text and message_object.text.startswith("!"):
                command_name = message_object.text[1:].split(" ")[0]
                command_response = messageHandler.handle_text_command(
                    command_name, author_id, thread_id, self
                )
                if command_response:
                    self.send(Message(text=command_response), thread_id=thread_id, thread_type=thread_type)
            elif message_object.attachments:  # Handle attachments (e.g., images)
                for attachment in message_object.attachments:
                    response = messageHandler.handle_attachment(attachment.url)
                    self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)
            else:  # Handle normal text messages
                response = messageHandler.handle_text_message(message_object.text)
                self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

# Initialize the bot
kora_bot = KoraBot(FB_EMAIL, FB_PASSWORD)

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "KORA Bot is running"}), 200

# Start the bot listener when the app starts
@app.before_first_request
def start_bot():
    logger.info("Starting the bot listener...")
    kora_bot.listen()

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
