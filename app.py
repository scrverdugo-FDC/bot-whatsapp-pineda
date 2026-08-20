import os
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_123")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp en línea", 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Token incorrecto", 403
    return "Parámetros inválidos", 400

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("Datos recibidos de WhatsApp:", data)
    
    try:
        # Aquí es donde el bot procesa el mensaje que te envían
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages")
        
        if messages:
            phone_number_id = value.get("metadata", {}).get("phone_number_id")
            from_number = messages[0].get("from")
            msg_body = messages[0].get("text", {}).get("body")
            
            print(f"Mensaje de {from_number}: {msg_body}")
            # Aquí puedes agregar la lógica para responder de vuelta si lo deseas
            
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
