from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar las variables del entorno
load_dotenv()

# Validar claves necesarias
REQUIRED_KEYS = ["GEMINI_API_KEY"]
for key in REQUIRED_KEYS:
    if not os.getenv(key):
        raise EnvironmentError(f"La clave {key} es requerida, pero no está configurada.")

# Configurar Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# Página principal con el frontend HTML para el chat
@app.get("/", response_class=HTMLResponse)
async def chatbot():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; }
            .chat-container { max-width: 600px; margin: 0 auto; }
            .chat-box { border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; height: 300px; overflow-y: auto; }
            .message { margin: 10px 0; }
            .bot-message { background-color: #f1f1f1; padding: 10px; border-radius: 5px; }
            .user-message { background-color: #d4f7d4; padding: 10px; border-radius: 5px; }
            .input-container { display: flex; }
            input[type="text"] { width: 100%; padding: 10px; margin-right: 10px; }
            button { padding: 10px; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-box" id="chat-box">
                <div class="message bot-message">Hola, ¿en qué puedo ayudarte?</div>
            </div>
            <div class="input-container">
                <input type="text" id="user-input" placeholder="Escribe tu mensaje..." />
                <button onclick="sendMessage()">Enviar</button>
            </div>
        </div>

        <script>
            const socket = new WebSocket("ws://localhost:8000/ws");

            socket.onopen = function(event) {
                console.log("WebSocket conectado");
            };

            socket.onmessage = function(event) {
                const chatBox = document.getElementById("chat-box");
                const botMessage = document.createElement("div");
                botMessage.classList.add("message", "bot-message");
                botMessage.innerText = event.data;
                chatBox.appendChild(botMessage);
                chatBox.scrollTop = chatBox.scrollHeight;
            };

            socket.onclose = function(event) {
                console.log("WebSocket cerrado:", event);
                alert("La conexión con el servidor se ha cerrado.");
            };

            socket.onerror = function(event) {
                console.error("Error en WebSocket:", event);
            };

            function sendMessage() {
                const userInput = document.getElementById("user-input").value;
                if (userInput.trim() === "") return;

                if (socket.readyState !== WebSocket.OPEN) {
                    alert("La conexión con el servidor no está abierta. Por favor, recarga la página.");
                    return;
                }

                const chatBox = document.getElementById("chat-box");

                const userMessage = document.createElement("div");
                userMessage.classList.add("message", "user-message");
                userMessage.innerText = userInput;
                chatBox.appendChild(userMessage);

                document.getElementById("user-input").value = "";

                socket.send(userInput);
            }
        </script>
    </body>
    </html>
    """)

# Conexión WebSocket para manejar los mensajes del chatbot
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    message_history = []
    
    # Definir un contexto inicial para guiar la conversación
    initial_context = """
    Eres un asistente conversacional amigable que:
    - Mantiene un contexto de conversación
    - Responde de manera natural y coherente
    - Sigue el hilo de la conversación
    - Evita respuestas genéricas o repetitivas
    """
    
    try:
        async for data in websocket.iter_text():
            print(f"Mensaje recibido del cliente: {data}")
            
            # Preparar el contexto de la conversación
            conversation_context = initial_context + "\n\nHistorial de conversación:\n" + "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in message_history[-10:]  # Limitar a los últimos 10 mensajes
            ])
            
            # Combinar el contexto con el nuevo mensaje
            full_prompt = f"{conversation_context}\n\nNuevo mensaje: {data}"
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Configurar parámetros para generar respuestas más coherentes
            generation_config = {
                "max_output_tokens": 150,  # Limitar longitud de respuesta
                "temperature": 0.7,  # Creatividad moderada
                "top_p": 0.9  # Diversidad de respuestas
            }
            
            # Generar respuesta con todo el contexto
            response = model.generate_content(
                full_prompt, 
                generation_config=generation_config
            )
            result = response.text
            
            print(f"Respuesta generada: {result}")
            
            # Actualizar el historial de mensajes
            message_history.append({"role": "user", "content": data})
            message_history.append({"role": "assistant", "content": result})
            
            await websocket.send_text(result)
    except WebSocketDisconnect:
        print("Cliente desconectado")
    except Exception as e:
        print(f"Error inesperado: {e}")