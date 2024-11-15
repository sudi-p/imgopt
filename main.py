import os
import streamlit as st
from dotenv import load_dotenv
from ps.aws import get_signed_upload_url, get_signed_download_url
from ps.ps import validate_psd_structure_local
from utils.api_calls import add_text_to_image, analyze_product_description
from ps.ps import getAdobeAccessToken
from loguru import logger
import requests

# Load environment variables
load_dotenv()

STYLE = """
<style>
img {
  max-width: 100%;
  width: 300px;
}
</style>
"""

import random

def upload_psd(uploaded_psd):
    """
    Handles the PSD upload process and local validation.

    Args:
        uploaded_psd: The uploaded PSD file object.
    Returns:
        str: The S3 key of the uploaded template if successful, else None.
    """
    if not uploaded_psd:
        st.error("No PSD file uploaded.")
        return None

    # Save uploaded file temporarily
    temp_folder = "temp"
    os.makedirs(temp_folder, exist_ok=True)
    local_path = os.path.join(temp_folder, uploaded_psd.name)

    with open(local_path, "wb") as f:
        f.write(uploaded_psd.getbuffer())

    # Validate PSD locally
    is_valid, validation_message = validate_psd_structure_local(local_path)
    if is_valid:
        st.success(validation_message)
    else:
        st.error(validation_message)
        return None

    # Generate a random name for the uploaded file
    random_id = random.randint(1, 1000)
    s3_key = f"Inputs/Template_{random_id}.psd"
    upload_url = get_signed_upload_url(s3_key)
    if not upload_url:
        st.error("Failed to generate signed upload URL.")
        return None

    # Upload to S3
    try:
        with open(local_path, "rb") as f:
            response = requests.put(upload_url, data=f)
            if response.status_code == 200:
                st.success(f"PSD template '{uploaded_psd.name}' uploaded successfully!")
                return s3_key
            else:
                st.error(f"Failed to upload PSD to S3. Status code: {response.status_code}")
                logger.error(f"Upload error: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error uploading PSD to S3: {e}")
        st.error("Failed to upload PSD template. Please try again.")
        return None



def main():
    st.markdown("<h1 style='text-align: center; color: grey;'>Image Optimization Tool</h1>", unsafe_allow_html=True)
    st.markdown(STYLE, unsafe_allow_html=True)

    # Initialize default template in session state
    if "psd_s3_key" not in st.session_state:
        st.session_state.psd_s3_key = "Inputs/theone.psd"  # Default template

    # Sidebar for PSD upload functionality
    st.sidebar.header("Upload PSD Template")
    uploaded_psd = st.sidebar.file_uploader("Upload a PSD Template", type=["psd"])
    if st.sidebar.button("Upload and Validate PSD"):
        uploaded_key = upload_psd(uploaded_psd)
        if uploaded_key:
            st.session_state.psd_s3_key = uploaded_key  # Update template in session state

    # Infographic generation section
    st.header("Generate Infographics")

    # Input for product description
    product_description = st.text_area("Enter the product description for auto-generated callouts")
    if st.button("Generate Callouts from Description"):
        with st.spinner("Analyzing product description..."):
            try:
                description_data = analyze_product_description(product_description)
                if description_data:
                    st.session_state.title = description_data.get("title", "")
                    st.session_state.subtitle = description_data.get("titleSub", "")
                    st.session_state.features = description_data.get("callouts", [])
                    st.success("Generated callouts successfully!")
                else:
                    st.error("Failed to generate callouts. Please try again.")
            except Exception as e:
                logger.error(f"Error generating callouts: {e}")
                st.error("An error occurred while generating callouts.")

    # Display generated or manual inputs
    text_title = st.text_input("Enter the title", value=st.session_state.get("title", ""))
    text_subtitle = st.text_input("Enter the subtitle", value=st.session_state.get("subtitle", ""))
    text_feature1 = st.text_input("Callout 1", value=st.session_state.get("features", [""])[0])
    text_feature2 = st.text_input("Callout 2", value=st.session_state.get("features", ["", ""])[1])
    text_feature3 = st.text_input("Callout 3", value=st.session_state.get("features", ["", "", ""])[2])

    # Generate infographics using the uploaded or default PSD template
    if st.button("Generate Infographics"):
        with st.spinner("Generating infographic..."):
            try:
                url = add_text_to_image(
                    text_title,
                    text_subtitle,
                    text_feature1,
                    text_feature2,
                    text_feature3,
                    st.session_state.psd_s3_key  # Use persistent PSD key
                )
                if url:
                    st.image(url, caption="Generated Image from PSD", use_column_width=True)
                else:
                    st.error("Failed to generate infographic. Please try again.")
            except Exception as e:
                logger.error(f"Error generating infographic: {e}")
                st.error("An error occurred while generating the infographic.")



if __name__ == "__main__":
    main()
