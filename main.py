#Importamos las bibliotecas que vamos a utilizar
from fastapi import FastAPI, WebSocket, WebSocketDisconnect #Para la creación de la API y el manejo de WebSockets
from fastapi.responses import HTMLResponse #para responder con HTML
from fastapi.middleware.cors import CORSMiddleware #para permitir el acceso a la API desde cualquier origen
from dotenv import load_dotenv #para cargar las variables de entorno desde el archivo .env
import google.generativeai as genai #para interactuar con la API de Generative AI
import os #para interactuar con el sistema operativo

# Cargar las variables del entorno del archivo .env
load_dotenv()

# Valida que las claves esten configuradas en el entorno
REQUIRED_KEYS = [AIzaSyBst5Xo9-k-PlELiTDiCoP11CP908OO-pI] #Lista de claves requeridas
os.getenv(REQUIRED_KEYS)

# for key in REQUIRED_KEYS:
#     if not os.getenv(key): #En el caso de que no este configurada una clase
#         raise EnvironmentError(f"La clave {key} es requerida, pero no está configurada.") #Error si no hay clave

# Configurar Gemini con la clave del entorno
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI() #Crear una instancia de FastAPI

# Agregar middleware CORS para permitir todos los orígenes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, WS, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

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
            /* Estilos para la página HTML */
            body { font-family: Arial, sans-serif; }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            html, body { height: 100%; font-family: Arial, sans-serif; }
            .chat-container { display: flex; flex-direction: column; height: 100vh; max-width: 800px; margin: 0 auto; padding: 10px; }
            .chat-box { flex-grow: 1; border: 1px solid #ccc; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; }
            .message { margin: 10px 0; max-width: 80%; word-wrap: break-word; }
            .bot-message { background-color: #f1f1f1; align-self: flex-start; border-radius: 5px; padding: 10px; }
            .user-message { background-color: #d4f7d4; align-self: flex-end; border-radius: 5px; padding: 10px; }
            .input-container { display: flex; margin-top: 10px; }
            #user-input { flex-grow: 1; padding: 10px; margin-right: 10px; }
            button { padding: 10px 20px; }
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
            /* Script para manejar el WebSocket y la interfaz del chatbot */
            const socket = new WebSocket(`${window.location.origin.replace("http", "ws")}/ws`);

            socket.onopen = function(event) { //Conexión correcta al servidor
                console.log("WebSocket conectado");
            };

            socket.onmessage = function(event) { //Respuesta del servidor
                const chatBox = document.getElementById("chat-box");
                const botMessage = document.createElement("div");
                botMessage.classList.add("message", "bot-message");
                botMessage.innerText = event.data; //Muestra la respuesta del servidor
                chatBox.appendChild(botMessage);
                chatBox.scrollTop = chatBox.scrollHeight; //Mueve la barra de desplazamiento hacia abajo
            };

            socket.onclose = function(event) { //Cierre de la conexión
                console.log("WebSocket cerrado:", event);
                alert("La conexión con el servidor se ha cerrado.");
            };

            socket.onerror = function(event) { //Error
                console.error("Error en WebSocket:", event);
            };

            function sendMessage() { //Función para enviar mensajes
                const userInput = document.getElementById("user-input").value;
                if (userInput.trim() === "") return; //No envía un mensaje vacío
 
                if (socket.readyState !== WebSocket.OPEN) { //Verifica si la conexión es abierta
                    alert("La conexión con el servidor no está abierta. Por favor, recarga la página.");
                    return;
                }

                const chatBox = document.getElementById("chat-box");

                const userMessage = document.createElement("div");
                userMessage.classList.add("message", "user-message");
                userMessage.innerText = userInput;
                chatBox.appendChild(userMessage);

                document.getElementById("user-input").value = ""; //Limpia el campo de entrada

                socket.send(userInput); //Envía el mensaje al servidor mediante WebSocket
            } 
        </script>

    </body>
    </html>
    """)

# Conexión WebSocket para manejar los mensajes del chatbot
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # Aceptar la conexión
    message_history = []    # Almacena el historial de mensajes

    # Contexto inicial más robusto
    system_prompt = """
    Eres un asistente conversacional inteligente y versátil que:
    - Mantiene un contexto de conversación completo y coherente
    - Adapta tus respuestas al tipo de solicitud
    - Ofrece respuestas creativas y específicas
    - Evita repetir contenido idéntico
    - Muestra personalidad y flexibilidad
    """

    try:
        while True: # Ciclo infinito para mantener la conexión abierta
            try:
                data = await websocket.receive_text() #Espera un mensaje del cliente
                print(f"Mensaje recibido del cliente:\n {data}")
                
                #Prepara el contexto de la conversación con los 6 últimos mensajes
                conversation_context = system_prompt + "\n\nHistorial reciente:\n" + "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in message_history[-6:]  # Limita a los 6 últimos mensajes 
                ])
                
                # Construir prompt completo para la generación de respuestas
                full_prompt = f"""{conversation_context}
                
                Solicitud actual: {data}
                
                Instrucciones:
                - Responde de manera natural y específica
                - Mantén la coherencia con el contexto previo
                """
                
                # Configuración de generación más flexible
                generation_config = {
                    "max_output_tokens": 1500,  # Aumentar longitud de respuesta
                    "temperature": 0.8,  # Más creatividad
                    "top_p": 0.9  # Diversidad de respuestas
                }
                
                # Inicializar modelo de google gemini
                model = genai.GenerativeModel("gemini-2.0-flash-exp")
                
                # Generar respuesta
                response = model.generate_content(
                    full_prompt, 
                    generation_config=generation_config
                )
                result = response.text
                
                print(f"Respuesta generada:\n {result}")
                
                # Actualizar historial de mensajes
                message_history.append({"role": "user", "content": data})
                message_history.append({"role": "assistant", "content": result})
                
                # Enviar respuesta al cliente
                await websocket.send_text(result)
            
            except Exception as generate_error: # Captura cualquier error de generación
                print(f"Error al procesar mensaje: {generate_error}")
                error_message = "Disculpa, ha ocurrido un error al procesar tu solicitud."
                await websocket.send_text(error_message)
    
    except WebSocketDisconnect: # Manejo de desconexión
        print("Cliente desconectado")
    except Exception as e: # Manejo de otros errores
        print(f"Error inesperado en WebSocket: {e}")