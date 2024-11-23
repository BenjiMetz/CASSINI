import os
import math
import matplotlib.pyplot as plt
from PIL import Image
import requests
from api import get_api

#Download image from google maps (600x600) with as basis the center of the map
def download_google_satellite_image(api_key, lat, lon, zoom=17, width=640, height=640):

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
        img_dir = os.path.join(base_path, f'Data/{round(lat,6)}_{round(lon,6)}.png')
        res_len = len(response.content)
        
        with open(img_dir, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")
    
    img = Image.open(img_dir)
    img_cropped = img.crop((20, 20, 620, 620))
    img_cropped.save(img_dir)

    return img_dir


#Pixel to coordinate,  source: stackoverflow
def PxltoCoord(x, y, height, width, zoom, cntr_lat, cntr_lon):

    parallelMultiplier = math.cos(cntr_lat * math.pi / 180)
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = cntr_lat - degreesPerPixelY * ( y - height / 2)
    pointLng = cntr_lon + degreesPerPixelX * ( x  - width / 2)

    return (pointLat, pointLng)

#Create template from smaller zoomed images, choose width and height as odd.
def CreateTemplate(blockHeight, blockWidth, centreLat, centreLon, api_key, zoom):
    imgTot = Image.new("RGB", (blockWidth*600, blockHeight*600))
    for i in range(blockWidth):
        for j in range(blockHeight):
            print(i*blockHeight+(j+1), "/", blockHeight*blockWidth)
            coordinate = PxltoCoord(300 + (i-(blockHeight-1)/2)*600, 300 + (j-(blockHeight-1)/2)*600, 600, 600, zoom, centreLat, centreLon)
            img_dir = download_google_satellite_image(api_key, coordinate[0], coordinate[1], zoom, 640, 640)
            img = Image.open(img_dir)
            imgTot.paste(img, (i*600, j*600))
            os.remove(img_dir)
    plt.imshow(imgTot)
    imgTot.save(f"Data\\{blockWidth}x{blockHeight}_{zoom}_Zoom_{centreLat}_{centreLon}.png")

centreLat = 52.0128569238565
centreLon = 4.355916744532585
zoom = 17

CreateTemplate(7,5,centreLat, centreLon, get_api(), zoom)

