import getpass
from sentinelhub import *
from typing import Any, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from os import getcwd

def plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: Optional[Tuple[float, float]] = None,
    **kwargs: Any
) -> None:
    """Utility function for plotting RGB images."""
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        ax.imshow(np.clip(image * factor, *clip_range), **kwargs)
    else:
        ax.imshow(image * factor, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])

#download template from copernicus
def downloadTemplate(config, time_interval, bbox, size, dir):
    evalscript_true_color = """
        //VERSION=3

        function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"], // Blue, Green, Red bands at 10m resolution
                units: "reflectance"
            }],
            output: {
                bands: 3 // RGB output
            }
        };
    }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """

    request_true_color = SentinelHubRequest(
        evalscript=evalscript_true_color,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C.define_from(
                    "s2l1c", service_url=config.sh_base_url
                ),
                time_interval=time_interval,
                other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=size,
        config=config,
    )

    true_color_imgs = request_true_color.get_data()
    image = true_color_imgs[0]
    imagePNG = Image.fromarray(image)
    imagePNG.save(dir)
    return image

config = SHConfig()
config.sh_client_id = 'sh-e42384a7-795e-40c3-b263-01794c552f24'
config.sh_client_secret = 'JuVSW7csj3yTd3ZyUViWfTJUGMO8X3uh'
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"

coordinates = [4.360113, 51.991117, 4.387193, 52.006785] # EWI centered picture like maps image
#  51.999080, 4.373749
time_interval = ("2022-06-12", "2024-01-01")

resolution = 0.75
bbox = BBox(bbox=coordinates, crs=CRS.WGS84)
size = bbox_to_dimensions(bbox, resolution)

print(size)
dir_root = getcwd()
dir = f"{dir_root}/Appel.PNG"
image = downloadTemplate(config, time_interval, bbox, size, dir)


# #Create template from smaller zoomed images, choose width and height as odd.
# def CreateTemplate(blockHeight, blockWidth, centreLat, centreLon, api_key, zoom):
#     imgTot = Image.new("RGB", (blockWidth*600, blockHeight*600))
#     for i in range(blockWidth):
#         for j in range(blockHeight):
#             print(i*blockHeight+(j+1), "/", blockHeight*blockWidth)
#             coordinate = PxltoCoord(300 + (i-(blockHeight-1)/2)*600, 300 + (j-(blockHeight-1)/2)*600, 600, 600, zoom, centreLat, centreLon)
#             img_dir = download_google_satellite_image(api_key, coordinate[0], coordinate[1], zoom, 640, 640)
#             img = Image.open(img_dir)
#             imgTot.paste(img, (i*600, j*600))
#             os.remove(img_dir)
#     plt.imshow(imgTot)
#     imgTot.save(f"Data\\{blockWidth}x{blockHeight}_{zoom}_Zoom_{centreLat}_{centreLon}.png")

# centreLat = 52.0128569238565
# centreLon = 4.355916744532585
# zoom = 17

# CreateTemplate(7,5,centreLat, centreLon, get_api(), zoom)

# def createTemplate(blockHeight, blockWidth):
#     imgTot = Image.new("RGB", ())
#     return 0