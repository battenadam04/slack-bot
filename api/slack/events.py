import os
import json
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
slack_client = WebClient(token=SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

async def handler(req, res):
    # Verify the request signature
    if not verifier.is_valid_request(
        req.headers, req.body.read()
    ):
        return res.status(400).send("Invalid request")

    # Parse the request body
    data = json.loads(req.body.decode('utf-8'))

    # Handle the challenge request
    if "challenge" in data:
        return res.status(200).send(data["challenge"])

    # Process events (only for message events in this example)
    event = data.get("event")
    if event and event.get("type") == "message" and not event.get("subtype"):
        channel_id = event.get("channel")
        text = event.get("text")
        if text:
            slack_client.chat_postMessage(channel=channel_id, text=f"You said: {text}")

    return res.status(200).send("")