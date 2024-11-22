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


# convert pixels to coordinates
def getPointLatLng(x, y):
    parallelMultiplier = math.cos(mid_lat * math.pi / 180)
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = mid_lat - degreesPerPixelY * (y - h / 2)
    pointLng = mid_lon + degreesPerPixelX * (x - w / 2)

    return (pointLat, pointLng)


EARTH_CIR_METERS = 40075016.686  # Circumference of Earth in meters
degrees_per_meter = 360 / EARTH_CIR_METERS  # Degrees per meter


# Convert degrees to radians
def to_radians(degrees):
    return degrees * math.pi / 180


# Function to calculate the bounding box for a given latitude, longitude, zoom, width, and height
def lat_lng_to_bounds(lat, lng, zoom, width, height):
    # Meters per pixel at the given zoom level
    meters_per_pixel_ew = EARTH_CIR_METERS / (2 ** (zoom + 8))
    meters_per_pixel_ns = meters_per_pixel_ew * math.cos(to_radians(lat))

    # Shift in meters (half the width and height of the image)
    shift_meters_ew = width / 2 * meters_per_pixel_ew
    shift_meters_ns = height / 2 * meters_per_pixel_ns

    # Convert meters to degrees
    shift_degrees_ew = shift_meters_ew * degrees_per_meter
    shift_degrees_ns = shift_meters_ns * degrees_per_meter

    # Return the bounding box as [[south, west], [north, east]]
    return [[lat - shift_degrees_ns, lng - shift_degrees_ew], [lat + shift_degrees_ns, lng + shift_degrees_ew]]


w = 620  # pixel width
h = 620  # pixel height
zoom = 15  # test zoom
zoom_template = 18  # template zoom


# Pixel to coordinate,  source: stackoverflow
def PxltoCoord(x, y, zoom, cntr_lat, cntr_lon):
    parallelMultiplier = math.cos(cntr_lat * math.pi / 180)
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier
    pointLat = cntr_lat - degreesPerPixelY * (y - h / 2)
    pointLng = cntr_lon + degreesPerPixelX * (x - w / 2)

    return (pointLat, pointLng)


# Because of non linear transformation (going from pixel to coordinates), function has to be solved for X and Y
def CoordToPixel(pointLat, pointLon, test_lat, test_lon):
    parallelMultiplier = math.cos(test_lat * math.pi / 180)
    degreesPerPixelX = 360 / math.pow(2, zoom + 8)
    degreesPerPixelY = 360 / math.pow(2, zoom + 8) * parallelMultiplier

    Y = (test_lat - pointLat) / degreesPerPixelY + 0.5 * h
    X = (pointLon - test_lon) / degreesPerPixelX + 0.5 * w
    return X, Y


# Generates bounding box by extracting coordinates of the corners from the images and scaling them correctly to the pixels of the test image
def GenBoundingBox(cntr_lat, cntr_lon, test_lat, test_lon):
    # center of test images

    # Coordinates of template corners
    max_lat_temp, max_lon_temp = PxltoCoord(w, 0, zoom_template, cntr_lat, cntr_lon)
    min_lat_temp, min_lon_temp = PxltoCoord(0, h, zoom_template, cntr_lat, cntr_lon)

    # Normalize X Y coordinates
    max_X, max_Y = CoordToPixel(max_lat_temp, max_lon_temp, test_lat, test_lon)
    min_X, min_Y = CoordToPixel(min_lat_temp, min_lon_temp, test_lat, test_lon)

    # Return x and y array in the correct order to generate squares on plot
    return [min_X, min_X, max_X, max_X, min_X], [min_Y, max_Y, max_Y, min_Y, min_Y]


# define coordinate window of template images based on testing image corners
upper_lat, lower_lon = getPointLatLng(0, 0)
lower_lat, upper_lon = getPointLatLng(w, h)

# test_train_dir = ['test_template_matching', 'train_template_matching']
test_train_dir = ['train_template_matching']
data = []

for test_train in test_train_dir:
    try:
        if test_train == 'train_template_matching':
            # This downloads 400 photos of delft area and puts it in images_test
            # for i in np.arange(51.978689, 51.978790, 0.0001):
            #     for j in np.arange(4.306998, 4.307099, 0.0001):
            # lat = np.random.uniform(lower_lat, upper_lat)
            # lon = np.random.uniform(lower_lon, upper_lon)
            pointLat, pointLng = 51.998766, 4.374169
            map_image = download_google_satellite_image(api_key, pointLat, pointLng, test_train, 'map_train', zoom=zoom)
            data = add_search_image(map_image, [pointLat, pointLng], [], data)
            r = lat_lng_to_bounds(pointLat, pointLng, zoom, 640, 640)
            minx, maxx, miny, maxy = r[0][0], r[1][0], r[0][1], r[1][1]

            edge = (maxx - minx) / 16
            edgey = (maxy - miny) / 16

            rangex = np.linspace(minx + edge, maxx - edge, 2 ** (zoom_template - zoom))
            rangey = np.linspace(miny + edgey, maxy - edgey, 2 ** (zoom_template - zoom))

            x_bound = (((maxx - edge) - (minx + edge)) / 2 ** (zoom_template - zoom)) / 2
            y_bound = (((maxy - edgey) - (miny + edgey)) / 2 ** (zoom_template - zoom)) / 2
            print(rangex, rangey, x_bound, y_bound)
            for x in rangex:
                for y in rangey:
                    X, Y = GenBoundingBox(x, y, pointLat, pointLng)
                    # print(X, Y)

                    temp_image = download_google_satellite_image(api_key, x, y, test_train, 'template_train',
                                                                 zoom=zoom_template)
                    data = add_template_to_search_image(map_image, temp_image,
                                                        [[x - x_bound, x + x_bound], [y - y_bound, y + y_bound]],
                                                        [x, y], data)
                    # base_path = os.getcwd()
                    #
                    # main_directory = os.path.dirname(base_path)
                    # img_dir = os.path.join(main_directory, f'Data/test_temp/{round(pointLat,6)}_{round(pointLng, 6)}.png')
                    # plt.figure(figsize=(10, 10))
                    #
                    # plt.subplot(2, 2, 1)
                    # plt.imshow(mpimg.imread(img_dir))
                    # plt.plot(X, Y, color='red')
                    # img_dir = os.path.join(main_directory, f'Data/test_temp/{round(x,6)}_{round(y,6)}.png')
                    # plt.subplot(2, 2, 2)
                    # plt.imshow(mpimg.imread(img_dir))
                    #
                    # plt.show()
                # print('test')
            base_path = os.getcwd()

            main_directory = os.path.dirname(base_path)
            main_directory = base_path

            img_dir = os.path.join(main_directory, f'Data/train_label/train.json')
            with open(img_dir, "w") as json_file:
                json.dump(data, json_file, indent=4)
        else:
            download_google_satellite_image(api_key, mid_lat, mid_lon, test_train, '', zoom=zoom)
            # print('train')
    except Exception as e:
        print(e)

    # extracts labels andset to correct file
    base_path = os.getcwd()

    # img_dir = os.path.join(base_path, f'Data/images_{test_train}')
    # main_directory = os.path.dirname(base_path)

    main_directory = base_path
    img_dir = os.path.join(main_directory, f'Data/map_train')

    files = os.listdir(img_dir)

    # augments data to remove google watermark by cropping the data
    for file in files:
        path = os.path.join(main_directory, f'Data/map_train/{file}')

        img = Image.open(path)
        img_cropped = img.crop((0, 0, 620, 620))

        img_cropped.save(path)

    img_dir = os.path.join(main_directory, f'Data/template_train')
    files = os.listdir(img_dir)

    # augments data to remove google watermark by cropping the data
    for file in files:
        path = os.path.join(main_directory, f'Data/template_train/{file}')
        img = Image.open(path)
        img_cropped = img.crop((0, 0, 620, 620))

        img_cropped.save(path)

print('NE: ', getPointLatLng(w, 0))
print('SW: ', getPointLatLng(0, h))
print('NW: ', getPointLatLng(0, 0))
print('SE: ', getPointLatLng(w, h))