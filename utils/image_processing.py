from rembg import remove
from PIL import Image, ImageOps
import io

def remove_background(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_removed_bg = remove(img_bytes)
    img = Image.open(io.BytesIO(img_removed_bg))
    img_cropped = crop_to_object(img)
    return resize_image(img_cropped)

def prepare_image_for_template(image, template_height, template_width, template_product_image_height, template_product_image_width):
    i_width, i_height = image.width, image.height
    scale = template_product_image_width / i_width
    new_height = int(i_height * scale)
    resized_image = image.resize((template_product_image_width, new_height), Image.LANCZOS)
    
    if new_height > template_height - 50:
        scale_height = (template_height - 50) / i_height
        new_width = int(i_width * scale_height)
        resized_image = image.resize((new_width, template_height - 50), Image.LANCZOS)
        
    return resized_image

def crop_to_object(image):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    bbox = image.getbbox()
    cropped_image = image.crop(bbox)
    return resize_image(cropped_image)

def resize_image(image, height=500):
    width = int(image.width * (height / image.height))
    return image.resize((width, height))
