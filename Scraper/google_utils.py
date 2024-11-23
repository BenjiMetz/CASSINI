import requests
import os
from PIL import Image

import requests
import os
from PIL import Image
def download_google_satellite_image(api_key, lat, lon, test_train, temp_map, zoom=17, width=256, height=256):
    # Construct the Google Maps Static API URL
    url = f"https://maps.googleapis.com/maps/api/staticmap"

    # Define the query parameters
    params = {
        'center': f"{lat},{lon}",
        'zoom': zoom,
        'size': f"{width}x{height}",
        'maptype': 'satellite',
        'key': api_key
    }

    # Send a GET request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:

        base_path = os.getcwd()

        main_directory = os.path.dirname(base_path)
        # main_directory = base_path
        img_dir = os.path.join(main_directory, f'Data/{temp_map}')

        if not os.path.exists(img_dir):
            # Create the directory
            os.makedirs(img_dir)

        img_dir = os.path.join(main_directory, f'Data/{temp_map}/{round(lat, 6)}_{round(lon, 6)}.png')

        with open(img_dir, 'wb') as file:
            file.write(response.content)

        with Image.open(img_dir) as img:
            cropped_img = img.crop((0, 0, width - 16, height - 16))  # Top-left corner to the desired size
            cropped_img.save(img_dir)

        return f'{round(lat,6)}_{round(lon,6)}.png'
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")