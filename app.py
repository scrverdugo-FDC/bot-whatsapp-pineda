import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Token de verificación para Meta
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_123")


@app.route("/webhook", methods=["GET"])
def verify_webhook():
  mode = request.args.get("hub.mode")
  token = request.args.get("hub.verify_token")
  challenge = request.args.get("hub.challenge")

  if mode == "subscribe" and token == VERIFY_TOKEN:
    print("WEBHOOK_VERIFICADO")
    return challenge, 200
  else:
    return "Token invalido", 403


@app.route("/webhook", methods=["POST"])
def receive_message():
  data = request.get_json()
  try:
    entries = data.get("entry", [])
    for entry in entries:
      changes = entry.get("changes", [])
      for change in changes:
        value = change.get("value", {})
        messages = value.get("messages", [])
        if messages:
          message = messages[0]
          remitente = message.get("from")
          texto = message.get("text", {}).get("body", "")
          print(f"Mensaje recibido de {remitente}: {texto}")
  except Exception as e:
    print(f"Error procesando mensaje: {e}")

  return jsonify({"status": "received"}), 200


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
