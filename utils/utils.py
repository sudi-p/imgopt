from PIL import Image
from colorthief import ColorThief
import streamlit as st
import io
import colorsys

def get_dominant_color(image):
  buffered = io.BytesIO()
  image.save(buffered, format="PNG")
  buffered.seek(0)

  ct = ColorThief(buffered);
  palette = ct.get_palette(color_count=5)

  columns = st.columns(len(palette))
  for idx, color in enumerate(palette):
    hex_color = rgb_to_hex(color)
    print(hex_color)
    with columns[idx]:
      st.markdown(f"<div style='background-color:{hex_color}; width:80px; height:80px;'></div>", unsafe_allow_html=True)
      st.write(hex_color)

# Function to convert RGB to HEX
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])