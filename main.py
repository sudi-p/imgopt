import streamlit as st
from api_calls import add_text_to_image
from file_upload import FileUpload
from dotenv import load_dotenv
from image_processing import remove_background
import os

load_dotenv()  # loads variables from .env file

STYLE = """
<style>
img {
  max-width: 100%;
  width: 300px;
}
</style>
"""

def main():
    st.markdown("<h1 style='text-align: center; color: grey;'>Image Optimization Tool</h1>", unsafe_allow_html=True)
    
    text_title = st.text_input("Enter the title")
    text_subtitle = st.text_input("Enter the subtitle")
    text_feature1 = st.text_input("Enter feature 1")
    text_feature2 = st.text_input("Enter feature 2")
    text_feature3 = st.text_input("Enter feature 3")
    
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
         
        
        # get_dominant_color(st.session_state.output_image)
        
        # caption = helper.generate_prompt(file)
        # st.write(caption)
        if st.button("Generate Image") and st.session_state.output_image:
            add_text_to_image(st.session_state.output_image, text_title, text_subtitle, text_feature1, text_feature2, text_feature3)
    file.close()

if __name__ == "__main__":
    main()
