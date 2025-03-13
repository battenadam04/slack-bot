from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs
import logging

# Load environment variables
load_dotenv('.env.development.local') 

# Setup the WebClient and the SignatureVerifier
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
web_client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

if SLACK_BOT_TOKEN is None or SLACK_SIGNING_SECRET is None:
    print("Environment variables not set") 
else:
    print("Environment variables are set")

# Create a new Flask web server
app = Flask(__name__)

# The route for the Slack events
@app.route('/api/slack/events', methods=['POST'])
def slack_events():
    # Check for JSON payload first
    if request.content_type == 'application/json':
        data = request.get_data()
    if not signature_verifier.is_valid_request(data, request.headers):
        return jsonify({'status': 'invalid_request'}), 403

    if request.content_type == 'application/json':
        event = request.get_json()
        if event.get("type") == "event_callback":
            event_type = event.get("event", {}).get("type")
            user_name = event.get("event", {}).get("user", {}).get("username")

            if event_type == "message" and user_name:
                try:
                    web_client.chat_postMessage(
                        channel=event["event"]["channel"],
                        text=f"Hello @{user_name}!"
                    )
                    return jsonify({'status': 'ok'}), 200
                except SlackApiError as e:
                    logging.error(f"Error sending message: {e}")
                    return jsonify({"status": "error", "message": str(e)}), 500
            else:
                logging.info("Ignoring non-message event or missing user_name.")

    return jsonify({'status': 'processed_non_challenge'}), 201

if __name__ == "__main__":
    app.run(port=3000)