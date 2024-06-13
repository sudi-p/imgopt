try:
 
    from enum import Enum
    from io import BytesIO, StringIO
    from typing import Union
    import os
    from dotenv import load_dotenv
    load_dotenv()  # loads variables from .env file
    import replicate
    import pandas as pd
    import streamlit as st
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
        REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
        prompt = st.text_input("Enter the prompt")
        st.markdown(STYLE, unsafe_allow_html=True)
        file = st.file_uploader("Upload file", type=self.fileTypes)
        show_file = st.empty()
        if not file:
            show_file.info("Please upload a file of type: " + ", ".join(["csv", "png", "jpg"]))
            return
        content = file.getvalue()
        if isinstance(file, BytesIO):
            show_file.image(file)

            if st.button("Generate Image"):
              try:
                input = {
                  "prompt": prompt,
                  "image_num": 2,
                  "image_path": file,
                  "product_size": "0.5 * width",
                  "negative_prompt": "(worst quality:2)"
                }
                output = replicate.run(
                  "logerzhu/ad-inpaint:b1c17d148455c1fda435ababe9ab1e03bc0d917cc3cf4251916f22c45c83c7df",
                  input=input
                )
                if not output:
                  st.write("Loading...")
                else:
                  for image in output:
                    st.image(image, width=400)
              except Exception as e:
                st.write(e.title)
                st.write(e.detail)
        else:
            data = pd.read_csv(file)
            st.dataframe(data.head(10))
        file.close()
 
 
if __name__ ==  "__main__":
    helper = FileUpload()
    helper.run()