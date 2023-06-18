import sqlite3
import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, Response, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect("messages.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create the messages table if it doesn't exist
def create_messages_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_file TEXT NOT NULL,
            tags TEXT

        )
    """)
    conn.commit()
    conn.close()

# Create the messages folder if it doesn't exist
def create_messages_folder(conversation_id):
    folder_path = os.path.join("messages", conversation_id)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Function to generate a unique conversation ID
def generate_conversation_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")  # Format: YYYYMMDDHHMMSSffffff
    uuid_part = str(uuid.uuid4()).replace("-", "")  # Remove hyphens from UUID
    return f"{timestamp}_{uuid_part}"

# Function to generate a unique filename for the message file
def generate_message_filename(conversation_id, sender):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")  # Format: YYYYMMDDHHMMSSffffff
    unique_id = str(uuid.uuid4()).replace("-", "")  # Remove hyphens from UUID
    return f"{conversation_id}_{sender}_{timestamp}_{unique_id}.txt"

# Function to store a message in the database and file system
def store_message(conversation_id, sender, message, tags):
    conn = get_db_connection()
    c = conn.cursor()

    # Generate a unique filename for the message file
    message_file = generate_message_filename(conversation_id, sender)

    # Create the conversation folder if it doesn't exist
    create_messages_folder(conversation_id)

    # Write the message to a file
    with open(os.path.join("messages", conversation_id, message_file), "w") as f:
        f.write(message)

    # Serialize the message tags
    serialized_tags = json.dumps(tags)
    c.execute("INSERT INTO messages (conversation_id, sender, message_file, tags) VALUES (?, ?, ?, ?)",
              (conversation_id, sender, message_file, serialized_tags))
    conn.commit()
    conn.close()


@app.route("/messages/<string:conversation_id>", methods=["POST"])
def add_message(conversation_id):
    data = request.get_json(force=True)
    message = data["message"]
    tags = data["tags"]  # Get the tags from the request data, default to an empty list if not provided

    store_message(conversation_id, "user", message, tags)  # Store the user's message
    return Response(response="OK", status=200)

@app.route("/messages/<string:conversation_id>", methods=["GET"])
def get_messages(conversation_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT message_file FROM messages WHERE conversation_id=?", (conversation_id,))
    message_files = [row[0] for row in c.fetchall()]
    conn.close()

    messages = []
    for message_file in message_files:
        with open(os.path.join("messages", conversation_id, message_file), "r") as f:
            message = f.read()
            messages.append(message)

    return Response(response=json.dumps(messages), status=200)

@app.route("/logo.png")
def plugin_logo():
    filename = "logo.png"
    return send_file(filename, mimetype="image/png")

@app.route("/.well-known/ai-plugin.json")
def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return Response(response=text, mimetype="text/json")

@app.route("/openapi.yaml")
def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(response=text, mimetype="text/yaml")

if __name__ == "__main__":
    create_messages_table()  # Initialize the messages table
    app.run(debug=True, host="0.0.0.0", port=5003)
