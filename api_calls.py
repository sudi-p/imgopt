import requests
import os
import base64
from io import BytesIO
import streamlit as st
import concurrent.futures

def generate_prompt(image):
    import replicate
    return replicate.run(
        "salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
        input={
            "task": "image_captioning",
            "image": image
        }
    )

def add_text_to_image(image, text_title, text_subtitle, text_feature1, text_feature2, text_feature3):
    api_key = os.environ['APITEMPLATE_API_KEY']
    template1_id = os.environ['APITEMPLATE_TEMPLATE1_ID']
    template2_id = os.environ['APITEMPLATE_TEMPLATE2_ID']
    
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    data = {
        "overrides":[
            {
                "name":"text-title",
                "text":text_title,
            },
            {
                "name":"text-subtitle",
                "text":text_subtitle,
            },
            {
                "name":"text-list-1",
                "text":text_feature1,
            },
            {
                "name":"text-list-2",
                "text":text_feature2,
            },
            {
                "name":"text-list-3",
                "text":text_feature3,
            },
            {
                "name":"product-image",
                "src": f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"
            }
        ]
    }
    def create_image(template_id):
        response = requests.post(
            f"https://rest.apitemplate.io/v2/create-image?template_id={template_id}",
            headers={"X-API-KEY": api_key},
            json=data
        )
        return response
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_template = {
            executor.submit(create_image, template1_id): 'Template 1',
            executor.submit(create_image, template2_id): 'Template 2'
        }
        for future in concurrent.futures.as_completed(future_to_template):
            template_name = future_to_template[future]
            try:
                response = future.result()
                if response.status_code == 200:
                    download_url = response.json().get('download_url')
                    st.image(download_url, width=400)
                else:
                    st.write(f"Error in generating image with {template_name}")
            except Exception as e:
                st.write(f"Exception in processing {template_name}: {e}")

