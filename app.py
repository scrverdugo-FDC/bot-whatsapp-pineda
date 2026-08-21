import os
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_123")

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp de Free Design Colombia en línea", 200

# Ruta exclusiva para que Meta verifique el Webhook (GET)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("¡Webhook verificado exitosamente por Meta!")
            return challenge, 200
        else:
            return "Token incorrecto", 403
    return "Parámetros inválidos", 400

# Ruta exclusiva para recibir los mensajes que te envían (POST)
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("--- PAQUETE RECIBIDO DE META ---")
    print(data)
    
    try:
        if data and "entry" in data:
            entry = data["entry"][0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages")
            
            if messages:
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                from_number = messages[0].get("from")
                msg_body = messages[0].get("text", {}).get("body")
                
                print(f"De: {from_number} | Mensaje: {msg_body}")
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        
    return jsonify({"status": "recibido"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
