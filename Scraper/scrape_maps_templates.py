import random

import requests
import numpy as np
import pandas as pd
import os
import math
from PIL import Image
from matplotlib import pyplot as plt, image as mpimg
import json
from utils_json import *
from google_utils import *
from utils import *
from api import *

# Function to download satellite image from Google Maps

api_key = get_api()

gen_test_data = 1  # set to zero to generate training data set

# middle coorindates of region delft
mid_lat = 51.998766
mid_lon = 4.374169

# image size in pixels
w = 620
h = 620

# zoom of test image
zoom = 15
zoom_template = 18

# define coordinate window of template images based on testing image corners
# upper_lat, lower_lon = getPointLatLng(0, 0)
# lower_lat, upper_lon = getPointLatLng(w, h)

test_train_dir = ['train_template_matching', 'test_template_matching']
# test_train_dir = ['train_template_matching']
data = []
training_size = 60
test_size = 20
map_image = ''
size = 0
for test_train in test_train_dir:
    data = []

    pointLat, pointLng = 51.999080, 4.373749
    r = lat_lng_to_bounds(pointLat, pointLng, zoom, 640, 640)
    minx, maxx, miny, maxy = r[0][0], r[1][0], r[0][1], r[1][1]

    edge = (maxx - minx) / 16
    edgey = (maxy - miny) / 16

    # Gives the 8 steps for the source image
    minx = minx + edge
    maxx = maxx - edge
    miny = miny + edgey
    maxy = maxy + edgey

    x_bound = (((maxx - edge) - (minx + edge)) / 2 ** (zoom_template - zoom)) / 2
    y_bound = (((maxy - edgey) - (miny + edgey)) / 2 ** (zoom_template - zoom)) / 2

    if test_train == 'train_template_matching':
        map_image = download_google_satellite_image(api_key, pointLat, pointLng, test_train, 'map_train', zoom=zoom)
        data = add_search_image(map_image, [pointLat, pointLng], [], data)
        size = training_size

    if test_train == 'test_template_matching':
        data = add_search_image(map_image, [pointLat, pointLng], [], data)
        size = test_size

    for i in range(size):
        x = round(random.uniform(minx, maxx), 6)
        y = round(random.uniform(miny, maxy), 6)
        X, Y = GenBoundingBox(x, y, pointLat, pointLng)

        temp_image = download_google_satellite_image(api_key, x, y, test_train, test_train,
                                                     zoom=zoom_template)
        data = add_template_to_search_image(map_image, temp_image,
                                            [[x - x_bound, x + x_bound], [y - y_bound, y + y_bound]],
                                            [x, y], data)

    base_path = os.getcwd()

    main_directory = os.path.dirname(base_path)

    img_dir = os.path.join(main_directory, f'Data/labels')
    if not os.path.exists(img_dir):
        # Create the directory
        os.makedirs(img_dir)
    img_dir = os.path.join(main_directory, f'Data/labels/{test_train}.json')
    with open(img_dir, "w") as json_file:
        json.dump(data, json_file, indent=4)

