import requests, os, base64, replicate, json
from io import BytesIO
import streamlit as st
import concurrent.futures
from PIL import Image
from loguru import logger
import ast
from utils.image_processing import prepare_image_for_template
from ps.ps import add_text

def generate_prompt(image):
    return replicate.run(
        "salesforce/blip:2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
        input={"task": "image_captioning", "image": image}
    )

def analyze_product_description(description):
    logger.info("analyze_product_description called")
    input = {
        "prompt": description,
        "max_new_tokens": 512,
        "system_prompt": (
            "You are an expert in the Amazon marketplace. "
            "Generate the title, subtitle, and callouts "
            "to use in the images of this product."
            "The output should be a Python dictionary "
            "{'title': 'some text', 'titleSub': 'some text', "
            "'callouts': ['callout1', 'callout2']}. Ignore other "
            "texts before [ and after ]. Each callouts should be "
            "less than 5 words."
        ),
    }
    result = ""
    for event in replicate.stream("meta/meta-llama-3-8b-instruct", input=input):
        result += str(event)
    
    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        dict_str = result[start:end]

        # Convert the string to a Python dictionary
        
        logger.info(dict_str)
        key_value_object = ast.literal_eval(dict_str)
    except json.JSONDecodeError:
        key_value_object = {}
    return key_value_object

def add_text_to_image(text_title, text_subtitle, text_feature1,
     text_feature2, text_feature3, template):
    title = text_title
    subTitle = text_subtitle
    return add_text(template, title, subTitle)

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
