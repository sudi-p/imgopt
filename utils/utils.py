from PIL import Image
from colorthief import ColorThief
import streamlit as st
import io
import colorsys
import replicate
import json

def get_dominant_color(image):
  buffered = io.BytesIO()
  image.save(buffered, format="PNG")
  buffered.seek(0)

  ct = ColorThief(buffered);
  palette = ct.get_palette(color_count=5)

  columns = st.columns(len(palette))
  colors = []
  for idx, color in enumerate(palette):
    hex_color = rgb_to_hex(color)
    colors.append(hex_color)
    with columns[idx]:
      st.markdown(f"<div style='background-color:{hex_color}; width:80px; height:80px;'></div>", unsafe_allow_html=True)
      st.write(hex_color)
  col = get_background_foreground(colors)
  print("Hello",col)
  if ("background_color" in col):
    columns = st.colums(2)
    background_color, text_color = col.background_color, col.text_color
    with columns[1]:
      st.markdown(f"<div style='background-color:{background_color}; width:80px; height:80px;'></div>", unsafe_allow_html=True)
      st.write(background_color)
    with columns[2]:
      st.markdown(f"<div style='background-color:{text_color}; width:80px; height:80px;'></div>", unsafe_allow_html=True)
      st.write(text_color)

# Function to convert RGB to HEX
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_background_foreground(colors):
    colors_str = ", ".join(colors)
    prompt_template = (
        "This is my list of dominant colors of a product image {}. "
        "Generate colors to use in the background and text color based on the dominant colors. "
        "The result must be a Python dictionary with the keys background_color and text_color. "
        "Give me the object only in output. I want to use this object directly in code. Don't give extra text. "
        "The output should start with '{' and end with '}'."
    )
    prompt = prompt_template.format(colors_str)
    input = {
        "prompt": prompt,
        "max_new_tokens": 512,
        "system_prompt": (
          "You are expert on graphic designing"
        ),
    }
    result = ""
    for event in replicate.stream("meta/meta-llama-3-8b-instruct", input=input):
        print(str(event))
        result += str(event)
    print("result of replicate api", result)
    try:
        key_value_object = json.loads(result)
    except json.JSONDecodeError:
        key_value_object = {}
    return key_value_object