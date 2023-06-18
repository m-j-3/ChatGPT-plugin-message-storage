import sqlite3
import json
from flask import Flask, request, Response, send_file

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect("messages.db")
c = conn.cursor()

# Create a table for storing messages
c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        message TEXT NOT NULL
    )
""")
conn.commit()

@app.route("/messages/<string:user_id>", methods=["POST"])
def add_message(user_id):
    data = request.get_json(force=True)
    message = data["message"]
    
    # Insert the message into the database
    c.execute("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, message))
    conn.commit()
    
    return Response(response="OK", status=200)

@app.route("/messages/<string:user_id>", methods=["GET"])
def get_messages(user_id):
    # Retrieve messages from the database for the given user_id
    c.execute("SELECT message FROM messages WHERE user_id=?", (user_id,))
    messages = [row[0] for row in c.fetchall()]
    
    return Response(response=json.dumps(messages), status=200)

# ... Define other routes for logo, plugin manifest, and openapi ...

# This key can be anything, though you will likely want a randomly generated sequence.
_SERVICE_AUTH_KEY = "REPLACE_ME"

def assert_auth_header():
    auth_header = request.headers.get("Authorization")
    assert auth_header == f"Bearer {_SERVICE_AUTH_KEY}"

@app.route("/logo.png")
def plugin_logo():
    filename = "logo.png"
    return send_file(filename, mimetype="image/png")

@app.route("/.well-known/ai-plugin.json")
def plugin_manifest():
    with open("ai-plugin.json") as f:
        text = f.read()
        return Response(response=text, mimetype="text/json")

@app.route("/openapi.yaml")
def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(response=text, mimetype="text/yaml")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
