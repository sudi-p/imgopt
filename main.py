import streamlit as st
from utils.api_calls import add_text_to_image, generate_wolverinn_realistic_background, generate_logerzhu_adinpaint_images, analyze_product_description
from utils.file_upload import FileUpload
from dotenv import load_dotenv
from utils.image_processing import remove_background, resize_image
import os
import sentry_sdk
from utils.utils import get_dominant_color

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
        print(resized_bg_removed_image.size)
        st.session_state.output_image = resized_bg_removed_image
        helper.display_side_by_side_images(resized_original_image, "Original Image", resized_bg_removed_image, "Background Removed")

    if 'current' not in st.session_state:
        st.session_state.current = "Background"

    col1, col2, col3 = st.columns(3)
    with col1: 
      if st.button("Background"):
         st.session_state.current = "Background"
    with col2:
      if st.button("Infographics"):
         st.session_state.current = "Infographics"
    with col3:
      if st.button("Dominant Colors"):
         st.session_state.current = "DominantColors"

    if (st.session_state.current == "Background"):
      input_prompt = st.text_input("Enter the prompt")
      if st.button("Generate Background") and st.session_state.output_image:
        # generate_logerzhu_adinpaint_images(input_prompt, file)
        generate_wolverinn_realistic_background(input_prompt, file)
    
    if (st.session_state.current == "Infographics"):
      product_description = st.text_area("Enter the product description")
      if st.button("Analyze product description"):
        description = analyze_product_description(product_description)
        if (description):
          title = description['title']
          subtitle = description['subtitle']
          print(description)
          features = description['features']
          if (len(features)==0):
            st.write("Description is too short to generate text for images infographics")
          st.session_state.title = title
          st.session_state.subtitle = subtitle
          st.session_state.features = features
      if 'title' in st.session_state:
        text_title = st.text_input("Enter the title", value=st.session_state.title)
        text_subtitle = st.text_input("Enter the subtitle", value=st.session_state.subtitle)
        text_feature1 = st.text_input("Enter feature 1", value=st.session_state.features[0] if len(st.session_state.features) > 0 else "")
        text_feature2 = st.text_input("Enter feature 2", value=st.session_state.features[1] if len(st.session_state.features) > 1 else "")
        text_feature3 = st.text_input("Enter feature 3", value=st.session_state.features[2] if len(st.session_state.features) > 2 else "")
        st.markdown(STYLE, unsafe_allow_html=True)
        if st.button("Generate Infographics") and st.session_state.output_image:
          add_text_to_image(st.session_state.output_image, original_image, text_title, text_subtitle, text_feature1, text_feature2, text_feature3)
    
    # caption = helper.generate_prompt(file)
    # st.write(caption)
    
    if (st.session_state.current == "DominantColors"):
      get_dominant_color(st.session_state.output_image)

    file.close()

if __name__ == "__main__":
    main()
