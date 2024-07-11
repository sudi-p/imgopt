import requests, os, base64, replicate, json
from io import BytesIO
import streamlit as st
import concurrent.futures
from PIL import Image
from utils.image_processing import prepare_image_for_template

def generate_prompt(image):
    return replicate.run(
        "salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
        input={"task": "image_captioning", "image": image}
    )

def analyze_product_description(description):
    input = {
        "prompt": description,
        "max_new_tokens": 512,
        "system_prompt": (
            "Analyze the following paragraph and extract the object of key-value pairs:\\n\\n{paragraph}\\n\\n"
            "with keys title, subtitle, and features with each features less than 20 characters. "
            "I want to use this object directly in code. Don't give extra text. The output should start with \"{\" and end with \"}\"."
        ),
    }
    result = ""
    for event in replicate.stream("meta/meta-llama-3-8b-instruct", input=input):
        result += str(event)
    try:
        key_value_object = json.loads(result)
    except json.JSONDecodeError:
        key_value_object = {}
    return key_value_object

def add_text_to_image(image, original_image, text_title, text_subtitle, text_feature1, text_feature2, text_feature3, background_color, text_color):
    text_color = text_color
    background_color = background_color
    api_key = os.environ['APITEMPLATE_API_KEY']

    templates = [
        {
            "template_id": os.environ['APITEMPLATE_TEMPLATE2_ID'],
            "use_original_image": False,
            "template_height": 1080,
            "template_width": 1080,
            "template_product_image_height": 425,
            "template_product_image_width": 425
        },
    ]
    data = {
        "overrides": [
            {"name": "text-title", "text": text_title, "color": text_color},
            {"name": "text-subtitle", "text": text_subtitle},
            {"name": "text-list-1", "text": text_feature1, "color": text_color, "strokeColor": text_color},
            {"name": "text-list-2", "text": text_feature2, "color": text_color},
            {"name": "text-list-3", "text": text_feature3, "color": text_color},
            {"name": "background", "backgroundColor": background_color},
        ]
    }

    def create_image(template):
        img_to_use = original_image if template["use_original_image"] else image
        prepared_image = prepare_image_for_template(
            img_to_use,
            template["template_height"],
            template["template_width"],
            template["template_product_image_height"],
            template["template_product_image_width"]
        )
        buffered = BytesIO()
        prepared_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        data["overrides"].append({
            "name": "product-image",
            "src": f"data:image/png;base64,{img_base64}",
            "scaleX": 1,
            "scaleY": 1
        })
        response = requests.post(
            f"https://rest.apitemplate.io/v2/create-image?template_id={template['template_id']}",
            headers={"X-API-KEY": api_key},
            json=data
        )
        return response
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_template = {executor.submit(create_image, template): template["template_id"] for template in templates}

        for future in concurrent.futures.as_completed(future_to_template):
            template_name = future_to_template[future]
            try:
                response = future.result()
                if response.status_code == 200:
                    download_url = response.json().get('download_url')
                    st.image(download_url, width=400)
                    with requests.get(download_url, stream=True) as r:
                        r.raise_for_status()
                        img = Image.open(BytesIO(r.content))
                else:
                    st.write(f"Error in generating image with {template_name}")
            except Exception as e:
                st.write(f"Exception in processing {template_name}: {e}")


def generate_logerzhu_adinpaint_images(prompt, file):
    input = {
        "prompt": prompt,
        "image_num": 2,
        "image_path": file,
        "product_size": "0.5 * width",
        "negative_prompt": "frames (worst quality:2)"
    }
    output = replicate.run(
        "logerzhu/ad-inpaint:b1c17d148455c1fda435ababe9ab1e03bc0d917cc3cf4251916f22c45c83c7df",
        input=input
    )
    generated_images = output[1:]
    for image in generated_images:
        st.image(image, width=400)

def generate_wolverinn_realistic_background(prompt, file):
    output = replicate.run(
        "wolverinn/realistic-background:ce02013b285241316db1554f28b583ef5aaaf4ac4f118dc08c460e634b2e3e6b",
        input={
            "seed": -1,
            "image": file,
            "steps": 20,
            "prompt": prompt,
            "cfg_scale": 7,
            "max_width": 1024,
            "max_height": 1024,
            "sampler_name": "DPM++ SDE Karras",
            "negative_prompt": "(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, mutated hands and fingers:1.4), (deformed, distorted, disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, disconnected limbs, mutation, mutated, ugly, disgusting, amputation, mug, cup",
            "denoising_strength": 0.75,
            "only_masked_padding_pixels": 4
        }
    )
    if not output:
        st.write("Loading...")
    else:
        image = output['image']
        st.image(image, width=400)
