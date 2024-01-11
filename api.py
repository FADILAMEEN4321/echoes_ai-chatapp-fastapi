from fastapi import FastAPI, WebSocket
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image



load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
chat_model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

chat = chat_model.start_chat(history=[])


app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        message = await websocket.receive()
        print(message)

        if isinstance(message, bytes):
            message = json.loads(message.decode())
        else:
            if message == "<FIN>":
                await websocket.close()
                break

            response = chat.send_message([message["text"]], stream=True)
            # img = PIL.Image.open('matrix_profile.jpg')   
            # response = vision_model.generate_content([message["text"], img], stream=True)
            # response.resolve() 
            
            print(response)

        for chunk in response:
            await websocket.send_text(chunk.text)
        await websocket.send_text("<FIN>")        

@app.get('/fetch-messages', response_model=list[dict])
async def fetch_messages():
    return [{'role': message.role, "text": message.parts[0].text} for message in chat.history]

@app.get('/')
def hello():
    return {'hello'}


