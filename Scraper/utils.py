import math


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
