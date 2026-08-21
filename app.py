import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")  # Token permanente o temporal de Meta

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
    try:
        data = request.get_json()
        print("--- PAQUETE RECIBIDO DE META ---")
        print(data)
        
        if data and "entry" in data:
            entry = data["entry"][0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages")
            
            if messages:
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                from_number = messages[0].get("from")
                msg_type = messages[0].get("type")
                
                # Validar si el mensaje es de texto para evitar errores si mandan otra cosa
                if msg_type == "text":
                    msg_body = messages[0].get("text", {}).get("body")
                    print(f"De: {from_number} | Mensaje de texto: {msg_body}")
                    
                    # Opcional: Responder automáticamente de vuelta al usuario
                    if WHATSAPP_TOKEN and phone_number_id:
                        enviar_respuesta(phone_number_id, from_number, f"Hola, recibí tu mensaje: '{msg_body}'")
                else:
                    print(f"De: {from_number} | Mensaje de tipo no textual: {msg_type}")
                    
    except Exception as e:
        print("Error crítico al procesar el mensaje:", e)
        
    return jsonify({"status": "recibido"}), 200

def enviar_respuesta(phone_number_id, to_number, mensaje):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": mensaje}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        print("Respuesta enviada a Meta:", response.status_code, response.text)
    except Exception as e:
        print("Error al enviar respuesta:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
