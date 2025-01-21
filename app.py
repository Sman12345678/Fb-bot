from flask import Flask, request
from fbchat import Client, log
from fbchat.models import *
from collections import deque
from dotenv import load_dotenv
import os
import logging
import messageHandler

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Facebook Messenger bot configuration
EMAIL = os.getenv('FB_EMAIL')
PASSWORD = os.getenv('FB_PASSWORD')
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')


class MessengerBot(Client):
    def __init__(self, email, password):
        super().__init__(email, password)
        self.user_message_history = {}

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        text = message_object.text
        attachments = message_object.attachments

        # Maintain last 3 messages for the user
        if thread_id not in self.user_message_history:
            self.user_message_history[thread_id] = deque(maxlen=3)
        if text:
            self.user_message_history[thread_id].append(text)

        # Log received message
        log.info(f"Message from {author_id}: {text}")

        # Handle commands prefixed with '!'
        if text.startswith("!"):
            command_name = text[1:].strip()
            response = messageHandler.handle_text_command(command_name, author_id, thread_id, self)
            if response:
                self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)

        # Handle attachments (e.g., images)
        elif attachments:
            for attachment in attachments:
                if isinstance(attachment, ImageAttachment):
                    image_data = self.fetchImage(attachment.uid)
                    response = messageHandler.handle_attachment(image_data)
                    self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)
                else:
                    self.send(Message(text="🚫 Unsupported attachment type. Please send an image."),
                              thread_id=thread_id, thread_type=thread_type)

        # Handle normal text messages
        else:
            response = messageHandler.handle_text_message(text)
            self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)


# Flask route to keep the bot running
@app.route('/')
def home():
    return "Facebook Messenger Bot is running!"


# Flask route to start the bot
@app.route('/start', methods=['POST'])
def start_bot():
    global bot
    bot = MessengerBot(EMAIL, PASSWORD)
    bot.listen()
    return "Bot started successfully!", 200


# Flask route to stop the bot
@app.route('/stop', methods=['POST'])
def stop_bot():
    global bot
    bot.logout()
    return "Bot stopped successfully!", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
