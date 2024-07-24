import streamlit as st
from utils.api_calls import add_text_to_image, generate_wolverinn_realistic_background, generate_logerzhu_adinpaint_images, analyze_product_description
from utils.file_upload import FileUpload
from dotenv import load_dotenv
from utils.image_processing import remove_background, resize_image
import os
import sentry_sdk
from utils.utils import get_dominant_color, display_colors
import threading
from loguru import logger

load_dotenv()  # loads variables from .env file

STYLE = """
<style>
img {
  max-width: 100%;
  width: 300px;
}
</style>
"""

if os.environ['ENVIRONMENT'] != "DEVELOPMENT":
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

def main():
    st.markdown("<h1 style='text-align: center; color: grey;'>Image Optimization Tool</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("Get Background"):
            st.session_state.task = "Get Background"
    with col2:
        if st.button("Change Callouts"):
            st.session_state.task = "Change Callouts"
    if 'task' not in st.session_state:
        st.session_state.task = "Get Background"
    if st.session_state.task == "Get Background":
        file = st.file_uploader("Upload file", type=["csv", "png", "jpg"])
        show_file = st.empty()
        if not file:
            show_file.info("Please upload a file of type: csv, png, jpg")
            return
        
        helper = FileUpload()
        
        original_image, resized_original_image = helper.load_and_display_file(file)
        
        if original_image:
            bg_removed_image = remove_background(original_image)
            resized_bg_removed_image = resize_image(bg_removed_image)
            
            # Output: (width, height)
            st.session_state.output_image = resized_bg_removed_image
            helper.display_side_by_side_images(resized_original_image, "Original Image", resized_bg_removed_image, "Background Removed")

            input_prompt = st.text_input("Enter the prompt")
            if st.button("Generate Background") and 'output_image' in st.session_state:
                generate_wolverinn_realistic_background(input_prompt, file)
        file.close()
        
    if st.session_state.task == "Change Callouts":
        logger.info("Change Callouts Clicked")
        product_description = st.text_area("Enter the product description")
        if st.button("Analyze product description"):
            description = analyze_product_description(product_description)
            if description:
                st.session_state.title = description.get('title', '')
                st.session_state.subtitle = description.get('titleSub', '')
                st.session_state.features = description.get('callouts', [])

        if 'title' in st.session_state:
            text_title = st.text_input("Enter the title", value=st.session_state.title)
            text_subtitle = st.text_input("Enter the subtitle", value=st.session_state.subtitle)
            text_feature1 = st.text_input("Callout 1", value=st.session_state.features[0] if len(st.session_state.features) > 0 else "")
            text_feature2 = st.text_input("Callout 2", value=st.session_state.features[1] if len(st.session_state.features) > 1 else "")
            text_feature3 = st.text_input("Callout 3", value=st.session_state.features[2] if len(st.session_state.features) > 2 else "")
            st.markdown(STYLE, unsafe_allow_html=True)
            if st.button("Generate Infographics"):
                url = add_text_to_image(
                    text_title,
                    text_subtitle,
                    text_feature1,
                    text_feature2,
                    text_feature3,
                    "Inputs/ForAnyOccasion.psd"
                )
                st.image(url, caption='Image from S3', use_column_width=True)

if __name__ == "__main__":
    main()
