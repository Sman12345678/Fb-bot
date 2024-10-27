import os
import subprocess
from Config import Config  # Import configuration
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

def display_kora_logo():
    kora_art = """
     ██╗  ██╗ ██████╗ ██████╗  █████╗ 
     ██║ ██╔╝██╔═══██╗██╔══██╗██╔══██╗
     █████╔╝ ██║   ██║██║  ██║███████║
     ██╔═██╗ ██║   ██║██║  ██║██╔══██║
     ██║  ██╗╚██████╔╝██████╔╝██║  ██║
     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
    """
    print(kora_art)
    print("KORA AI Bot is now running...")

def start_facebook_bot():
    # Start the Node.js bot as a subprocess
    subprocess.Popen(["node", "fb-bot-node/bot.js"])

if __name__ == "__main__":
    # Display the KORA logo and start the bot
    display_kora_logo()
    start_facebook_bot()
    
    port=3000
   
    
