import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Cargar las variables de entorno configuradas en Render
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_123")
WHATSAPP_ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")

@app.route("/", methods=["GET"])
def home():
    return "Bot de WhatsApp de Free Design Colombia en línea", 200

@app.route("/webhook_valido", methods=["GET"])
def verify_webhook():
    # Validación que hace Meta al guardar la URL del Webhook
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

@app.route("/webhook_valido", methods=["POST"])
def receive_message():
    # REGLA DE ORO: Capturamos el JSON que manda Meta
    data = request.get_json()
    
    # RESPUESTA INMEDIATA: Le contestamos a Meta con un 200 OK en menos de 1 segundo 
    # para evitar que la plataforma bloquee o silencie nuestros webhooks por timeout.
    response_ack = jsonify({"status": "recibido"}), 200

    try:
        # Analizamos el payload en segundo plano (o inmediatamente después del ACK)
        if data and "entry" in data:
            entry = data["entry"][0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages")
            
            if messages:
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                from_number = messages[0].get("from")
                msg_body = messages[0].get("text", {}).get("body")
                
                print(f"--- NUEVO MENSAJE RECIBIDO ---")
                print(f"De: {from_number}")
                print(f"Mensaje: {msg_body}")
                print(f"Phone Number ID: {phone_number_id}")
            else:
                print("Notificación de Meta recibida (sin mensajes de texto directos).")
    except Exception as e:
        print("Error al procesar el JSON del mensaje:", e)
        
    return response_ack

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
