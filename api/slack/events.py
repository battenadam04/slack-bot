import os
import json
from slack_bolt import App
from slack_bolt.adapter.vercel import VercelAdapter

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)
    event = body.get("event", {})

    if event.get("subtype") is None and "text" in event:
        channel_id = event.get("channel")
        user_id = event.get("user")
        text = event.get("text")
        app.client.chat_postMessage(channel=channel_id, text=f"Hello <@{user_id}>! You said: {text}")

# Initialize the Vercel adapter
vercel_adapter = VercelAdapter(app)

# Export the handler function for Vercel
handler = vercel_adapter.handler