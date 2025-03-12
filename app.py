import os  # Import the 'os' module for interacting with the operating system
import http.server  # Import the 'http.server' module for creating a simple HTTP server
import json  # Import the 'json' module for handling JSON data
from slack_sdk import WebClient  # Import the Slack SDK for interacting with the Slack API
from slack_sdk.signature import SignatureVerifier  # Import the signature verifier for security

# Get Slack tokens from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")

# Initialize Slack client and signature verifier
slack_client = WebClient(token=SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNING_SECRET)

# Define a custom request handler class
class SlackRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):  # Handle incoming POST requests
        # Verify the request signature for security
        if not verifier.is_valid_request(
            self.headers, self.rfile.read(int(self.headers['content-length']))
        ):
            self.send_response(400)  # Send a 400 Bad Request response
            self.end_headers()
            return

        # Read the request body and parse the JSON data
        data = json.loads(self.rfile.read(int(self.headers['content-length'])).decode('utf-8'))

        # Handle Slack's challenge requests (for URL verification)
        if "challenge" in data:
            self.send_response(200)  # Send a 200 OK response
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(data["challenge"].encode())  # Send the challenge response
            return

        # Process incoming Slack events
        event = data.get("event")
        if event and event.get("type") == "message" and not event.get("subtype"):
            channel_id = event.get("channel")  # Get the channel ID
            text = event.get("text")  # Get the message text
            if text:
                # Send a response back to the channel
                slack_client.chat_postMessage(channel=channel_id, text=f"You said: {text}")

        # Send a 200 OK response for successful event processing
        self.send_response(200)
        self.end_headers()

# Start the HTTP server if the script is run directly
if __name__ == "__main__":
    PORT = 8080  # Choose a port for the server
    server_address = ("", PORT)  # Bind to all interfaces on the specified port
    httpd = http.server.HTTPServer(server_address, SlackRequestHandler)  # Create the server
    print(f"Server started on port {PORT}")  # Print a message to the console
    httpd.serve_forever()  # Start the server and listen for requests indefinitely