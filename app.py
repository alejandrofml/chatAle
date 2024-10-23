from flask import Flask, request
import requests
import json

app = Flask(__name__)

# Token y URL de la API de WhatsApp Business
ACCESS_TOKEN = 'EAAQhQjvSy4wBOzT46LCoiOa5VgQLAD6aJYpfJ2viqUjDy0vz2bRjmEZBa8SAOs9TPUr47O2mYHFzQstwXoOgZB8CAeR0JwmkdwJ8jBbo93l84RkRfuncy126FZAfvARNZAXO4LvLkXLnkwZBXvkmJRgH8AI9f9jGScu7X79WWpk1XaTLvOgjluFITsm29LUJS3lOEen3fiBJpSWCzX2aReu8uyGZAEphAcguUZD'
PHONE_NUMBER_ID = '477992922059513'
WHATSAPP_API_URL = f"https://graph.facebook.com/v20.0/477992922059513/messages"


# Ruta para verificar el webhook
@app.route('/webhook', methods=['GET'])
def webhook_verify():
    verify_token = 'tu_token_de_verificacion'  # Crea un token de verificación único
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if token == verify_token:
        return challenge
    else:
        return 'Token de verificación incorrecto', 403

# Ruta para manejar los mensajes entrantes
@app.route('/webhook', methods=['POST'])
def webhook_receive():
    data = request.get_json()
    
    # Procesa el mensaje recibido
    if 'messages' in data['entry'][0]['changes'][0]['value']:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        phone_number = message['from']
        
        # Si el mensaje es un texto simple
        if 'text' in message:
            message_text = message['text']['body']
            if 'hola' in message_text.lower():
                send_interactive_message(phone_number)
            else:
                response_message = handle_message(message_text)
                send_message(phone_number, response_message)

        # Si el usuario ha seleccionado una respuesta interactiva
        elif 'interactive' in message:
            interactive_type = message['interactive']['type']
            
            if interactive_type == 'button_reply':
                selection_id = message['interactive']['button_reply']['id']
                handle_button_reply(phone_number, selection_id)

    return "EVENT_RECEIVED", 200

# Función para enviar un mensaje interactivo con botones
def send_interactive_message(phone_number):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "¿Cómo te podemos ayudar?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "prices",
                            "title": "Consultar Precios"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "location",
                            "title": "Ver Ubicación"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "contact",
                            "title": "Contactar"
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

# Manejar las respuestas del usuario a los botones
def handle_button_reply(phone_number, selection_id):
    if selection_id == 'prices':
        send_message(phone_number, "Los precios de los cursos de música son:\n- Clase individual: $50\n- Clase grupal: $30")
    elif selection_id == 'location':
        send_message(phone_number, "Nos encontramos en:\nCalle de la Música 123, Ciudad Musical.")
    elif selection_id == 'contact':
        send_message(phone_number, "Para más información, contáctanos al +1 234 567 890.")

# Función para manejar mensajes de texto sin botones
def handle_message(message_text):
    """Maneja el contenido del mensaje recibido."""
    if 'hola' in message_text.lower():
        return "Hola, ¿cómo te podemos ayudar?"
    else:
        return "Lo siento, no entendí tu mensaje."

# Función para enviar un mensaje de texto simple
def send_message(phone_number, message_text):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': phone_number,
        'type': 'text',
        'text': {
            'body': message_text
        }
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

if __name__ == '__main__':
    app.run(debug=True)