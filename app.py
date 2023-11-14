import streamlit as st
import openai
import base64
from io import BytesIO
from PIL import Image
import requests


# Set your OpenAI API key
openai.api_key = st.secrets['openai_key']

# Function to encode image to base64
def encode_image_to_base64(image):
    buffered = BytesIO()
    # Convert RGBA to RGB
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


# Function to get image description from GPT-4 Vision API
def get_image_description(base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        # "model": "gpt-4-1106-preview",
         
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": """Jawab pertanyaan di gambar ini dengan penjelasannya. 
                Usahakan untuk menjawab tanpa alat bantuan apapun, kamu harus memberikan jawaban. Jawab secara terstruktur, pelan-pelan saja.
                Jawab semuanya dalam plain text."""
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 4096
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    # return response.json().choices[0].message['content']
    # Check if the response was successful
    if response.status_code == 200:
        # Parse the response JSON and extract the description
        try:
            return response.json()['choices'][0]['message']['content']#['text']
        except KeyError as e:
            # If the expected keys are not in the JSON response, print the error
            st.error(f"KeyError: {str(e)} - the structure of the response JSON is not as expected.")
            return None
    else:
        # If the response is not OK, print the status code and content for debugging
        st.error(f"Failed to get description. Status Code: {response.status_code} - Response: {response.content}")
        return None


# Function to generate an image using DALL·E 3 API with the description

# Streamlit app
st.title('Robot Solver')
st.write("Upload foto/screenshot soal apapun (matematika, pemrograman, elektro, biologi, fisika, kimia, dll), saya akan mencoba menjawabnya lengkap dengan penjelasannya.")

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload foto soal.", type=["png", "jpg", "jpeg"])
st.text("Penjelasan soal harus sudah ada di foto/gambar ya gan.")

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Display the uploaded image
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    if st.button('Jawab!'):
        # Encode the uploaded image to base64
        base64_image = encode_image_to_base64(image)
        # st.write(base64_image)

        with st.spinner('Sebentar saya mikir dulu...'):
            # Get a description of the image from GPT-4 Vision
            description = get_image_description(base64_image)
            st.write(description)
