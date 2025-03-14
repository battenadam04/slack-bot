from flask import Flask, request, jsonify, redirect
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs
import logging

# Load environment variables
load_dotenv('.env.development.local') 

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
SLACK_AUTH_SECRET=os.getenv("SLACK_AUTH_SECRET")
web_client = WebClient(token=SLACK_BOT_TOKEN)
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

if any(var is None for var in [SLACK_CLIENT_ID, SLACK_CLIENT_SECRET, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET]):
    print("Error: Environment variables not set correctly.")

# Create a new Flask web server
app = Flask(__name__)

# The route for the Slack events
@app.route('/api/slack/events', methods=['POST'])
def slack_events():

      # --- Signature Verification ---
    request_body = request.get_data()
    slack_signature = request.headers['X-Slack-Signature']
    timestamp = request.headers['X-Slack-Request-Timestamp']

    if not signature_verifier.is_valid_request(request_body, slack_signature, timestamp):
        return jsonify({'status': 'invalid_request'}), 403
    
     # --- Challenge Handling ---
    if request.content_type == 'application/json':
        data = request.get_json()

        if data.get("type") == "url_verification":
            challenge_response = {"challenge": data.get("challenge")}
            return jsonify(challenge_response), 200, {'Content-Type': 'application/json'}

         # --- Event Handling ---
        if data.get("type") == "event_callback":
            event_type = data.get("event", {}).get("type")
            user_id = data.get("event", {}).get("user")
            text = data.get("event", {}).get("text", "").lower()
            channel_id = data.get("event", {}).get("channel")

        # Respond to "hello" in any channel or DM
        if event_type == "message" and text == "hello":
            try:
                # Log user_id before fetching user info
                logging.info(f"User ID: {user_id}") 

                user_info = web_client.users_info(user=user_id)
                user_name = user_info["user"]["real_name"]

                # Log user_name and channel_id before sending the message
                logging.info(f"User Name: {user_name}")
                logging.info(f"Channel ID: {channel_id}")

                web_client.chat_postMessage(
                    channel=channel_id,
                    text=f"Hello, {user_name}! Nice one, I work as expected."
                )
                return jsonify({'status': 'ok'}), 200

            except SlackApiError as e:
                logging.error(f"Error responding to message: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({'status': 'event_not_processed'}), 200  


if __name__ == "__main__":
    app.run(port=3000)