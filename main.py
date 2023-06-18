import json
from flask import Flask, request, Response, send_file

app = Flask(__name__)

# This key can be anything, though you will likely want a randomly generated sequence.
_SERVICE_AUTH_KEY = "REPLACE_ME"
_MESSAGES = {}

def assert_auth_header():
    auth_header = request.headers.get("Authorization")
    assert auth_header == f"Bearer {_SERVICE_AUTH_KEY}"

@app.route("/messages/<string:user_id>", methods=["POST"])
def add_message(user_id):
    assert_auth_header()
    data = request.get_json(force=True)
    if user_id not in _MESSAGES:
        _MESSAGES[user_id] = []
    _MESSAGES[user_id].append(data["message"])
    return Response(response="OK", status=200)

@app.route("/messages/<string:user_id>", methods=["GET"])
def get_messages(user_id):
    assert_auth_header()
    messages = _MESSAGES.get(user_id, [])
    return Response(response=json.dumps(messages), status=200)

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
