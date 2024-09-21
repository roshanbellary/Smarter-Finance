import streamlit as st
import streamlit_authenticator as stauth
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import yaml
from yaml.loader import SafeLoader

# Load configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create an authentication object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Add login widget
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # User is logged in
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    
    st.title('Receipt OCR')

    processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
    model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

    uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        pixel_values = processor(image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        st.write(generated_text)

elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

