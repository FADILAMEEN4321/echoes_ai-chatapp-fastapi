import base64
import pickle
import PIL.Image

with open('matrix_profile.jpg', 'rb') as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
print(encoded_image)
# img = PIL.Image.open('matrix_profile.JPG')
# data = {
#   "text": "Explain this image?",
#   "image": img
# }

# binary_data = pickle.dumps(data)
# print(binary_data)

# text = "Explain the image."
# encoded_text = base64.b64encode(text.encode("utf-8"))
# print(encoded_text,'------>')
# print(encoded_text.decode("utf-8"))