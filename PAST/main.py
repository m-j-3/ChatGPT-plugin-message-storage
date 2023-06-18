import sqlite3
import json
from flask import Flask, request, Response, send_file
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def get_connection():
    return sqlite3.connect("messages.db")

def create_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def store_message(user_id, sender, message):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, sender, message) VALUES (?, ?, ?)", (user_id, sender, message))
    conn.commit()
    conn.close()

def get_messages(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    messages = [{"sender": row[0], "message": row[1]} for row in rows]
    conn.close()
    return messages

@app.route("/messages/<string:user_id>", methods=["POST"])
def add_message(user_id):
    data = request.get_json(force=True)
    message = data["message"]
    store_message(user_id, "user", message)
    return Response(response="OK", status=200)

@app.route("/messages/<string:user_id>", methods=["GET"])
def get_user_messages(user_id):
    messages = get_messages(user_id)
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
    create_table()  # Create the table before running the app
    app.run(debug=True, host="0.0.0.0", port=5003)
