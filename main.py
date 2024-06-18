try:
 
    from enum import Enum
    from io import BytesIO, StringIO
    from typing import Union
    import os
    from dotenv import load_dotenv
    load_dotenv()  # loads variables from .env file
    from PIL import Image
    import replicate
    import pandas as pd
    import streamlit as st
    from rembg import remove
except Exception as e:
    print(e)



STYLE = """
<style>
img {
    max-width: 100%;
    width: 300px;
}
</style>
"""

class FileUpload(object):
 
    def __init__(self):
        self.fileTypes = ["csv", "png", "jpg"]
 
    def run(self):
        
        st.write("Image Optimization Tool")
        # REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
        prompt = st.text_input("Enter the prompt")
        st.markdown(STYLE, unsafe_allow_html=True)
        file = st.file_uploader("Upload file", type=self.fileTypes)
        show_file = st.empty()
        if not file:
            show_file.info("Please upload a file of type: " + ", ".join(["csv", "png", "jpg"]))
            return
        if isinstance(file, BytesIO):
          original_image = Image.open(file)
          original_image_resized = original_image.resize((500, int(original_image.height * (500 / original_image.width))))

          output_image = remove(original_image)

          col1, col2 = st.columns(2)
          with col1:
              st.image(original_image_resized, caption="Original Image", use_column_width=True)
          with col2:
              st.image(output_image, caption="Background Removed", use_column_width=True)

            # if st.button("Generate Image"):
            #   try:
            #     input = {
            #       "prompt": prompt,
            #       "image_num": 2,
            #       "image_path": file,
            #       "product_size": "0.5 * width",
            #       "negative_prompt": "(worst quality:2)"
            #     }
            #     output = replicate.run(
            #       "logerzhu/ad-inpaint:b1c17d148455c1fda435ababe9ab1e03bc0d917cc3cf4251916f22c45c83c7df",
            #       input=input
            #     )
            #     if not output:
            #       st.write("Loading...")
            #     else:
            #       for image in output:
            #          st.image(image, width=400)
            #   except Exception as e:
            #     print(e)
            #     if (e.title):
            #       st.write(e.title)
            #     if (e.detail):
            #       st.write(e.detail)
          
        else:
            data = pd.read_csv(file)
            st.dataframe(data.head(10))
        file.close()
 
 
if __name__ ==  "__main__":
    helper = FileUpload()
    helper.run()