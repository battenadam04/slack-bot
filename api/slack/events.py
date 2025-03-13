from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
from urllib.parse import parse_qs

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
    # It's generally safer to access request data directly
    data = request.get_data() 

    # Parse URL-encoded data
    parsed_data = parse_qs(data.decode()) 

    # Check for the challenge in the parsed data
    if "challenge" in parsed_data:
        challenge_response = {
            "challenge": parsed_data["challenge"][0]  # Access the value from the list
        }
        return jsonify(challenge_response).encode(), 200
    
    # Verification should happen before data processing
    if not signature_verifier.is_valid_request(data, request.headers): 
        return jsonify({'status': 'invalid_request'}), 403
    else: 
        event_data = request.json
        event = event_data.get('event')
        return jsonify({'status': 'ok'}), 200 

if __name__ == "__main__":
    app.run(port=3000) 