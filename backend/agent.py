# Guava voice agent, from https://docs.goguava.ai/guides/webrtc-calls
# Run with: python agent.py  (blocks and answers browser calls until stopped)
import os

import guava
from dotenv import load_dotenv
from guava import logging_utils

load_dotenv()  # loads GUAVA_API_KEY and GUAVA_WEBRTC_CODE from backend/.env

agent = guava.Agent(
    purpose="You are a friendly guide for a simple grid game.",
    name="Hannah",
)


@agent.on_call_start
def on_call_start(call: guava.Call):
    # Set your first task here using call.set_task(...)
    pass


if __name__ == "__main__":
    logging_utils.configure_logging()
    agent.listen_webrtc(os.environ["GUAVA_WEBRTC_CODE"])
