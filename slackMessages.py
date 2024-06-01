from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

def get_conversations():
    channel_id = "C0761TU0VNZ"
    slack_token = ""

    if not channel_id:
        return jsonify({"error": "channel_id parameter is required"}), 400
    if not slack_token:
        return jsonify({"error": "token parameter is required"}), 400

    try:
        client = WebClient(token=slack_token)

        # Fetch conversations from the specified channel
        try:
            history_response = client.conversations_history(
                channel=channel_id,
                limit=100  # Increase limit to fetch more messages
            )
            messages = history_response['messages']
            thread_messages = []

            # Check for threads
            for message in messages:
                if 'thread_ts' in message:
                    # Fetch thread messages
                    thread_response = client.conversations_replies(
                        channel=channel_id,
                        ts=message['thread_ts']
                    )
                    thread_messages.extend(thread_response['messages'])

            # Combine main messages and thread messages
            all_messages = messages + thread_messages

        except SlackApiError as e:
            print(f"Error fetching conversation history: {e.response['error']}")
            return jsonify({"error": e.response['error']}), 500

        return all_messages

    except SlackApiError as e:
        return jsonify({"error": e.response['error']}), 500

def messages_to_paragraph(messages):
    paragraph = ""
    for message in reversed(messages):  # Iterate over messages in reverse order
        if 'text' in message:
            paragraph += message['text'] + "\n"
    return paragraph

@app.route('/conversations', methods=['GET'])
def conversations_route():
    messages = get_conversations()
    paragraph = messages_to_paragraph(messages)
    return jsonify(paragraph)

if __name__ == '__main__':
    app.run(port=5000)
