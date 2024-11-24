import json
import os
def add_search_image(search_image_name, search_image_gps, templates, data):
    # Create the new search image entry
    new_entry = {
        "search_image": search_image_name,
        "search_image_gps": search_image_gps,
        "templates": templates
    }

    # Add it to the main data list
    data.append(new_entry)

    # Optionally, save the updated data to a JSON file
    # with open("search_images_with_templates.json", "w") as json_file:
    #     json.dump(data, json_file, indent=4)

    return data


def add_template_to_search_image(search_image_name, template_name, bounding_box, gps_coords, data):
    # Find the search image entry
    for entry in data:
        if entry["search_image"] == search_image_name:
            # Add the new template to the existing entry
            new_template = {
                "template": template_name,
                "bounding_box": bounding_box,
                "gps_coords": gps_coords
            }
            entry["templates"].append(new_template)

            # Optionally, save the updated data to a JSON file
            # with open("search_images_with_templates.json", "w") as json_file:
            #     json.dump(data, json_file, indent=4)
            # return  # Exit the function once the template is added

    # print(f"Search image {search_image_name} not found.")
    return data