import os
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_123")

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp en línea", 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFICADO EXITOSAMENTE")
        return Response(response=challenge, status=200, mimetype="text/plain")
    
    return Response(response="Token invalido", status=403)

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("MENSAJE RECIBIDO:", data)
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
