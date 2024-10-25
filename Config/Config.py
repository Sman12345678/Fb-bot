import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PREFIX = os.getenv("PREFIX")  # The prefix for commands
    BOT_ADMIN = os.getenv("BOT_ADMIN")  # Bot admin's ID
