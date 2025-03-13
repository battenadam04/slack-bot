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
        data = request.get_json()
        if data.get("type") == "url_verification":
            challenge_response = {
                "challenge": data.get("challenge")
            }
            return jsonify(challenge_response), 200, {'Content-Type': 'application/json'}

    # If not JSON, try parsing as URL-encoded
    else: 
        data = request.get_data()
        parsed_data = parse_qs(data.decode())
        if "challenge" in parsed_data:
            challenge_response = {
                "challenge": parsed_data["challenge"][0]
            }
            return jsonify(challenge_response), 200, {'Content-Type': 'application/json'}

        # ... (Your existing code for signature verification and event handling)
        # This block will ONLY execute if the request is NOT a challenge request
        return jsonify({'status': 'processed_non_challenge'}), 201 

if __name__ == "__main__":
    app.run(port=3000)