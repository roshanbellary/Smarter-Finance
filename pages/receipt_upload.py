import streamlit as st
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

st.title('Receipt Processing')

if 'user' not in st.session_state:
    st.error("Unauthorized. Please create an account to continue.")
    st.stop()
else:
    user = st.session_state['user']
    
    # Add option for user to choose input method
    input_method = st.radio("Choose input method:", ["Manual Entry", "Upload Receipt Image"])
    
    if input_method == "Manual Entry":
        # Manual entry form
        st.subheader("Manual Purchase Entry")
        date = st.date_input("Purchase Date")
        amount = st.number_input("Purchase Amount", min_value=0.01, step=0.01)
        description = st.text_input("Purchase Description")
        
        if st.button("Submit Purchase"):
            # Here you would add code to save the manually entered purchase
            st.success("Purchase submitted successfully!")
    
    else:
        # OCR processing
        st.subheader("Receipt OCR")
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
        uploaded_file = st.file_uploader("Upload a receipt image", type=["jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            pixel_values = processor(image, return_tensors="pt").pixel_values
            generated_ids = model.generate(pixel_values)
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            st.write("OCR Result:")
            st.write(generated_text)
            
            # Add option to confirm or edit OCR result
            if st.button("Confirm OCR Result"):
                # Here you would add code to save the OCR result
                st.success("OCR result saved successfully!")