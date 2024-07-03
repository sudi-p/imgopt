from PIL import Image
import pandas as pd
import streamlit as st
from utils.image_processing import resize_image
from utils.api_calls import generate_prompt, add_text_to_image

class FileUpload:
    
    def __init__(self):
        self.fileTypes = ["csv", "png", "jpg"]

    def display_image(self, image, caption):
        st.image(image, caption=caption)

    def load_and_display_file(self, file):
        if file.type == "text/csv":
            data = pd.read_csv(file)
            st.dataframe(data.head(10))
        else:
            image = Image.open(file)
            resized_image = resize_image(image)
            # print(image.size)
            # print(resized_image.size)
            return image, resized_image
        return None, None

    def generate_prompt(self, image):
        return generate_prompt(image)

    def display_side_by_side_images(self, image1, caption1, image2, caption2):
        col1, col2 = st.columns(2)
        with col1:
            print(image1.size)
            self.display_image(image1, caption1)
        with col2:
            print(image2.size)
            self.display_image(image2, caption2)
