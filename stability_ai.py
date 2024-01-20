import base64
import requests
import os
from dotenv import load_dotenv


load_dotenv()


def stability_ai_request(prompt: str):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    body = {
        "steps": 40,
        "width": 1024,
        "height": 1024,
        "seed": 0,
        "cfg_scale": 5,
        "samples": 1,
        "text_prompts": [
            {"text": prompt, "weight": 1},
            {"text": "blurry, bad", "weight": -1},
        ],
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": os.getenv('STABILITY_AI_API_KEY'),
    }

    response = requests.post(
        url,
        headers=headers,
        json=body,
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    # make sure the out directory exists
    if not os.path.exists("./out"):
        os.makedirs("./out")

    image_paths = []
    for i, image in enumerate(data["artifacts"]):
        image_path = f'./out/txt2img_{image["seed"]}.png'
        with open(f'./out/txt2img_{image["seed"]}.png', "wb") as f:
            f.write(base64.b64decode(image["base64"]))
        image_paths.append(image_path)

    first_image_path = image_paths[0]

    with open(first_image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_data}"

    return data_url
