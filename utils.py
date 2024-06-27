from PIL import Image
import streamlit as st
import io

def get_dominant_color(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)

    image = Image.open(buffered).convert('RGB')
    width, height = image.size
   
    image = image.resize((width // 10, height // 10))

    pixels = image.getcolors(image.size[0] * image.size[1])
    if not pixels:
      st.write("Error: Unable to get colors from image")
      return

    sorted_pixels = sorted(pixels, key=lambda t: t[0], reverse=True)
    
    dominant_colors = [color[1] for color in sorted_pixels[:5]]

    for i, color in enumerate(dominant_colors):
        hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
        st.markdown(f"<div style='background-color:{hex_color}; width:200px; height:100px;'></div>", unsafe_allow_html=True)
        st.write(f"Dominant color {i + 1}: {hex_color}")