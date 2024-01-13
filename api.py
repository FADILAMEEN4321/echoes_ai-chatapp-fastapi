from fastapi import FastAPI, WebSocket
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image
import io
import base64


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
chat_model = genai.GenerativeModel("gemini-pro")
vision_model = genai.GenerativeModel("gemini-pro-vision")

chat = chat_model.start_chat(history=[])


app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        message = await websocket.receive_json()
        print(message)

        print(type(message), "---------------message type=-----")

        checking = message.get("text")
        print(type(checking), "----------------->text-type<---------")

        if message.get("text") and message.get("image"):
            print("yes------->image hai")
            text = message.get("text")
            image = message.get("image")
            # image_bytes = image.encode('utf-8')
            image_bytes = base64.b64decode(image)

            if text == "<FIN>":
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

            print("-------------no image")

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
def hello():
    return {"hello"}
