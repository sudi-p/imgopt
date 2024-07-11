from PIL import Image
from colorthief import ColorThief
import streamlit as st
import numpy as np
import io
import ast
import colorsys
import replicate
import json


def calculate_color_coverage(image, palette, tolerance=30):
    image_data = np.array(image)
    # Remove the alpha channel if present
    if image_data.shape[-1] == 4:
        image_data = image_data[:, :, :3]
    total_pixels = image_data.shape[0] * image_data.shape[1]
    color_counts = {rgb_to_hex(color): 0 for color in palette}

    for color in palette:
        # Create a mask to identify pixels matching the color within a tolerance
        mask = np.all(np.abs(image_data - color) <= tolerance, axis=-1)
        color_counts[rgb_to_hex(color)] = np.sum(mask)

    color_coverage = {color: count / total_pixels * 100 for color, count in color_counts.items()}
    return color_coverage

def get_dominant_color(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)

    ct = ColorThief(buffered)
    palette = ct.get_palette(color_count=5)

    colors = [rgb_to_hex(color) for color in palette]
    color_coverage = calculate_color_coverage(image, palette)
    background_foreground = get_background_foreground(color_coverage)
    print(color_coverage)
    return {
        "colors": colors,
        "color_coverage": color_coverage,
        "background_foreground": background_foreground
    }


def display_colors(colors, color_coverage, background_color, text_color):
    columns = st.columns(len(colors))

    for idx, color in enumerate(colors):
        with columns[idx]:
            st.markdown(f"<div style='background-color:{color}; width:40px; height:40px;'></div>",
                        unsafe_allow_html=True)
            st.write(color)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Background Color: {background_color}")
        st.markdown(f"<div style='background-color:{background_color}; width:40px; height:40px;'></div>",
                    unsafe_allow_html=True)
    with col2:
        st.write(f"Text Color: {text_color}")
        st.markdown(f"<div style='background-color:{text_color}; width:40px; height:40px;'></div>",
                    unsafe_allow_html=True)

    for color, coverage in color_coverage.items():
        st.write(f"{color}: {coverage:.2f}% coverage")



# Function to convert RGB to HEX
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def get_background_foreground(color_coverage):
    colors = ""
    for color, coverage in color_coverage.items():
        colors += "{} of {}% coverage".format(color, coverage)
    print(colors)
    colors_str = ", ".join(colors)
    optimal = False;
    while not optimal:
        prompt_template = (
                "This is my list of dominant colors of product images {}"
                "I want to create an image with the product and some background color that enhances the product."
                "Process the colors and give me best color that would be the background and the text color that suits"
                "with the background color generate above. The answer to question 'Is the generated text color an optimal text color for the generated background color' should be a yes."
                "The result must be a Python dictionary with the keys background_color and text_color. Could you give me the object only in output?"
                "I want to use this object directly in the code."
                "Don't give extra text. The output should start with '{{' and end with '}}'."
        )
        prompt = prompt_template.format(colors_str)
        get_colors_input = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "system_prompt": (
              "You are expert on graphic designing"
            ),
        }
        result = ""
        for event in replicate.stream("meta/meta-llama-3-8b-instruct", input=get_colors_input):
            result += str(event)
        result = result.strip()
        result = ast.literal_eval(result)
        text_color = result['text_color']
        background_color = result['background_color']
        optimal_color_prompt = (
            "is {} an optimal text color for the background {}. Just give me a True or False answer."
            "The output should not have any other text."
        ).format(background_color, text_color)
        optimal_input = {
            "prompt": optimal_color_prompt,
            "max_new_tokens": 512,
            "system_prompt": (
                "You are expert on graphic designing"
            ),
        }
        optimal_result = ""
        for event in replicate.stream("meta/meta-llama-3-8b-instruct", input=optimal_input):
            optimal_result += str(event)
        optimal = bool(optimal_result)
        print(optimal)

    return result
