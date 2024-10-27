#apitemplate.io
def add_text_to_image(image, original_image, text_title, text_subtitle, text_feature1, text_feature2, text_feature3, background_color=None, text_color=None):
    text_color = text_color
    background_color = background_color
    api_key = os.environ['APITEMPLATE_API_KEY']
    templates = [
        {
            "template_id": os.environ['APITEMPLATE_TEMPLATE4_ID'],
            "use_original_image": True,
            "template_height": 900,
            "template_width": 1200,
            "template_product_image_height": 954,
            "template_product_image_width": 741
        },
        {
            "template_id": os.environ['APITEMPLATE_TEMPLATE5_ID'],
            "use_original_image": True,
            "template_height": 1080,
            "template_width": 1080,
            "template_product_image_height": 880,
            "template_product_image_width": 880
        },
    ]
    data = {
        "overrides": [
            {"name": "text-title", "text": text_title},
            {"name": "text-subtitle", "text": text_subtitle},
            {"name": "text-list-1", "text": text_feature1},
            {"name": "text-list-2", "text": text_feature2},
            {"name": "text-list-3", "text": text_feature3},
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

