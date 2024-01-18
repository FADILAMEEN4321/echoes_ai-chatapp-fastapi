from fastapi import FastAPI, WebSocket
import os
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import io
import base64


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
    """
    websocket_endpoint handles websocket connections.

    It accepts websocket connections, and then enters a loop to handle
    messages received over the websocket.

    If a text and image is received, it generates a response using the
    vision model. Otherwise it just generates a text response using the
    chat model.

    It streams back the response in chunks over the websocket."""

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

        else:
            if message.get("text") == "<FIN>":
                await websocket.close()
                break

            response = chat.send_message([message.get("text")], stream=True)

        for chunk in response:
            await websocket.send_text(chunk.text)

        await websocket.send_text("<FIN>")


@app.get("/fetch-messages", response_model=list[dict])
async def fetch_messages():
    return [
        {"role": message.role, "text": message.parts[0].text}
        for message in chat.history
    ]


@app.get("/")
def test():
    return {"detail": "Yes api is working."}
