from fastapi import FastAPI, WebSocket
import os
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import io
import base64
import requests
from stability_ai import stability_ai_request


load_dotenv()

# Configures the Google API client with the API key loaded from the .env file.
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initializes the Gemini GenerativeModel instances for the chatbot and image vision.
chat_model = genai.GenerativeModel("gemini-pro")
vision_model = genai.GenerativeModel("gemini-pro-vision")

# Starts a new chat session with the chatbot model.
chat = chat_model.start_chat(history=[])

# Initializes the FastAPI app.
app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        message = await websocket.receive_json()

        if message.get("text") == "<FIN>":
            await websocket.close()
            break

        response = chat.send_message([message.get("text")], stream=True)

        for chunk in response:
            await websocket.send_text(chunk.text)

        await websocket.send_text("<FIN>")


@app.websocket("/ws/image-chat")
async def websocket_image_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_json()

        if message.get("text") and message.get("image"):
            text = message.get("text")
            image = message.get("image")
            image_bytes = base64.b64decode(image)

            if message.get("text") == "<FIN>":
                await websocket.close()
                break

            img = PIL.Image.open(io.BytesIO(image_bytes))

            response = vision_model.generate_content([text, img], stream=True)
            response.resolve()
            print(response)

        for chunk in response:
            await websocket.send_text(chunk.text)

        await websocket.send_text("<FIN>")


@app.post("/image-generation")
async def image_generation(prompt: str):
    respone = stability_ai_request(prompt)
    return {"success": True, "image_data_url": respone}


@app.get("/fetch-messages", response_model=list[dict])
async def fetch_messages():
    return [
        {"role": message.role, "text": message.parts[0].text}
        for message in chat.history
    ]


@app.get("/")
def test():
    return {"detail": "Yes, api is working."}
