import gradio as gr
from assignment_chat.__main__ import therapy_chat
from dotenv import load_dotenv

from utils.logger import get_logger

_logs = get_logger(__name__)

load_dotenv('.secrets')

chat = gr.ChatInterface(
    fn=therapy_chat,
    type="messages"
)

if __name__ == "__main__":
    _logs.info('Starting Therapy Chat App...')
    chat.launch()
