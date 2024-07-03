from rembg import remove
from PIL import Image
import io
from colorthief import ColorThief
import matplotlib.pyplot as plt
import colorsys


def remove_background(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_removed_bg = remove(img_bytes)
    img = Image.open(io.BytesIO(img_removed_bg))
    img_cropped = crop_to_object(img)
    return resize_image(img_cropped)

def crop_to_object(image):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    bbox = image.getbbox()
    cropped_image = image.crop(bbox)
    return resize_image(cropped_image)

def resize_image(image, height=500):
    width = int(image.width * (height / image.height))
    return image.resize((width, height))
