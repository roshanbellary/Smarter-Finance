# import streamlit as st
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel
# from PIL import Image
# from properlauth import auth

# user = auth.get_user()
# if user is None:
#     st.error('Unauthorized')
#     st.stop()
# if authentication_status:
#     # User is logged in
#     authenticator.logout('Logout', 'main')
#     st.write(f'Welcome *{name}*')
    
#     st.title('Receipt OCR')

#     processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
#     model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

#     uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "png", "jpeg"])
#     if uploaded_file is not None:
#         image = Image.open(uploaded_file).convert("RGB")
#         pixel_values = processor(image, return_tensors="pt").pixel_values
#         generated_ids = model.generate(pixel_values)
#         generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
#         st.write(generated_text)

# elif authentication_status == False:
#     st.error('Username/password is incorrect')
# elif authentication_status == None:
#     st.warning('Please enter your username and password')

import streamlit as st

from propelauth import auth

user = auth.get_user()
if user is None:
    st.error('Unauthorized')
    st.stop()

with st.sidebar:
    st.link_button('Account', auth.get_account_url(), use_container_width=True)

st.text("Logged in as " + user.email + " with user ID " + user.user_id)