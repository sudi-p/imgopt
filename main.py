import streamlit as st
from api_calls import add_text_to_image, generate_wolverinn_realistic_background, generate_logerzhu_adinpaint_images, analyze_product_description
from file_upload import FileUpload
from dotenv import load_dotenv
from image_processing import remove_background
import os
import sentry_sdk
from utils import get_dominant_color

load_dotenv()  # loads variables from .env file

STYLE = """
<style>
img {
  max-width: 100%;
  width: 300px;
}
</style>
"""

if (os.environ['ENVIRONMENT'] != "DEVELOPMENT"):
  sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
  )

def main():
    st.markdown("<h1 style='text-align: center; color: grey;'>Image Optimization Tool</h1>", unsafe_allow_html=True)
    input_prompt = st.text_input("Enter the prompt")
    product_description = st.text_area("Enter the product description")
    if product_description and st.button("Analyze product description"):
      description = analyze_product_description(product_description)
      if (description):
        print(f'Description: {description}')
        st.write(f"Title: {description['title']}")
        st.write(f"Subtitle: {description['subtitle']}")
        st.write('Features:')
        for feature in description['features']:
          st.write(f'- {feature}')
    # text_title = st.text_input("Enter the title")
    # text_subtitle = st.text_input("Enter the subtitle")
    # text_feature1 = st.text_input("Enter feature 1")
    # text_feature2 = st.text_input("Enter feature 2")
    # text_feature3 = st.text_input("Enter feature 3")
    
    st.markdown(STYLE, unsafe_allow_html=True)
    
    file = st.file_uploader("Upload file", type=["csv", "png", "jpg"])
    show_file = st.empty()
    
    if not file:
        show_file.info("Please upload a file of type: csv, png, jpg")
        return
    
    helper = FileUpload()
    
    original_image, resized_image = helper.load_and_display_file(file)
    
    if 'output_image' not in st.session_state:
        st.session_state.output_image = original_image
    
    if original_image:
        st.session_state.output_image = remove_background(original_image)
        helper.display_side_by_side_images(resized_image, "Original Image", st.session_state.output_image, "Background Removed")
        
        # caption = helper.generate_prompt(file)
        # st.write(caption)
        if st.button("Generate Background") and st.session_state.output_image:
          # generate_logerzhu_adinpaint_images(input_prompt, file)
          generate_wolverinn_realistic_background(input_prompt, file)
        
        if st.button("Get Dominant Colors")  and st.session_state.output_image:
          get_dominant_color(st.session_state.output_image)

        if st.button("Generate Infographics") and st.session_state.output_image:
          add_text_to_image(st.session_state.output_image, text_title, text_subtitle, text_feature1, text_feature2, text_feature3)
    file.close()

if __name__ == "__main__":
    main()
