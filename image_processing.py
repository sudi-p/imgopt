from rembg import remove
from PIL import Image
import io

def remove_background(image):
    # Remove the background
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_removed_bg = remove(img_bytes)
    img = Image.open(io.BytesIO(img_removed_bg))

    # Crop the image to the object
    img_cropped = crop_to_object(img)

    return img_cropped

def crop_to_object(image):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    bbox = image.getbbox()
    cropped_image = image.crop(bbox)
    
    return resize_image(cropped_image)

def resize_image(image):
    new_height = 500
    new_width = int(image.width * (new_height / image.height))
    return image.resize((new_width, new_height))
