import argparse
import os
import shutil
import math
import time
from PIL import Image


def positive_integer(string: str) -> bool:
    satisfies = int(string) >= 0
    if satisfies:
        return True
    else:
        raise ValueError().add_note("Must be a positive integer.")


# CLI arguments for program configuration
argument_parser = argparse.ArgumentParser(prog="Tyiler")
argument_parser.add_argument(
    "-V",
    "--version",
    action="version",
    dest="version",
    version="%(prog)s 0.0.2",
    help="Displays tool version.",
)
argument_parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    dest="verbose",
    help="Adds more-informative intermediate program outputs.",
)
argument_parser.add_argument(
    "-g",
    "--generate-tiles",
    action="store_true",
    dest="generate_tiles",
    help="Generates tiles of size max_tile_size from the highest resolution image it finds in any child folders.",
)
argument_parser.add_argument(
    "-u",
    "--upload",
    action="store_true",
    dest="upload",
    help="Uploads the generated tiles to ROBLOX using tarmac. Ensure you are running in a BASH terminal and you have a .env file with the ROBLOSECURITY key in it.",
)
argument_parser.add_argument(
    "-t",
    "--max-tile-size",
    action="store",
    dest="max_tile_size",
    default=1024,
    help="Specifies the maximum tile size per tile (default %(default)s).",
    nargs="?",
    type=positive_integer,
)
arguments = argument_parser.parse_args()


# prepares the save folder for tile outputs by clearing any images that exist already, and making the directory
def prepare_save_folder(root_folder_name: str, folder_name: str) -> str:
    folder_path = os.path.join(root_folder_name, folder_name)

    # clearing out any previous files/folders
    if os.path.isdir(folder_path):
        shutil.rmtree(folder_path)

    # creating the new folder
    os.makedirs(folder_path)

    return folder_path


# searches the file at env_file_path to find the desired search_key, and return it.
def parse_env_file(env_file_path: str, search_key: str) -> str:
    if not os.path.isfile(env_file_path):
        return
    env_file = open(env_file_path, "r")
    for line in env_file.readlines():
        # all keys in .env files are separated by a = with no spaces
        line_parts = line.split("=")
        if len(line_parts) == 2 and line_parts[0] == search_key:
            line = line_parts[1]
            line = line[:-2]
            if line.startswith('"'):
                line = line[1:]
            if line.endswith('"'):
                line = line[:-2]
            return line


# returns True when the first image has a higher resolution than the second one
def better_resolution(image1: Image, image2: Image) -> bool:
    if image1 != None and image2 != None:
        return image1.width * image1.height > image2.width * image2.height
    else:
        return True


# splits a given image into tiles based on the arguments.max_tile_size constant, and saves them to save_folder
def split_image_to_tiles(image: Image, save_folder: str, tile_prefix: str) -> int:
    tiles_x = math.ceil(image.width / arguments.max_tile_size)
    tiles_y = math.ceil(image.height / arguments.max_tile_size)
    tiles_generated = tiles_x * tiles_y
    print(
        f"Generating {tiles_generated} ({tiles_x}x{tiles_y}) tile(s) for {image.filename} of size {image.size} in {save_folder}"
    )
    tileIndex = 1
    for y in range(0, tiles_y):
        for x in range(0, tiles_x):
            box = (
                arguments.max_tile_size * x,
                arguments.max_tile_size * y,
                min(arguments.max_tile_size * (x + 1), image.width),
                min(arguments.max_tile_size * (y + 1), image.height),
            )
            image_tile = image.crop(box)

            # edge cases (literally "edge" lol)
            # this ensures every tile is actually the same size as all the others,
            # by pasting the cropped image onto a transparent background image with the regular tile size
            background_tile = Image.new(
                "RGBA",
                (arguments.max_tile_size, arguments.max_tile_size),
                (0, 0, 0, 255),
            )
            if y == tiles_y - 1 or x == tiles_x - 1:
                image_tile = background_tile.paste(image_tile)
                image_tile = background_tile

            image_name = f"{tile_prefix}_tile_{str(tileIndex)}_{str(x)}_{str(y)}.png"  # y and x are swapped because viewing these files in file explorer looks nice
            image_tile.save(os.path.join(save_folder, image_name))

            tileIndex += 1

            if arguments.verbose == True:
                print(
                    f'Created tile "{image_name}" with box-coordinates ({box[0]},{box[1]},{box[2]},{box[3]}) and size {image_tile.width}x{image_tile.height}'
                )
    if arguments.verbose == True:
        print(f"Generated {tiles_generated} tile(s)")
    return tiles_generated


# script execution
if arguments.generate_tiles == True:
    start_time = time.time()

    folder_count = 0
    colour_image_count = 0
    contour_image_count = 0
    tile_count = 0

    for file_name in os.listdir(os.getcwd()):
        if os.path.isdir(file_name):
            folder_count += 1

            # creating save directories and emptying them if they already exist
            target_save_folder_colour = prepare_save_folder(file_name, "colour_tiles")
            target_save_folder_contour = prepare_save_folder(file_name, "contour_tiles")

            # finding the highest resolution colour image and contour image
            existing_images = os.listdir(os.getcwd() + os.path.sep + file_name)
            colour_image: Image = None
            contour_image: Image = None

            for existing_image_name in existing_images:
                existing_image_path = os.path.join(file_name, existing_image_name)
                if (
                    os.path.isfile(existing_image_path) == True
                    and existing_image_name.find(".png") != -1
                ):
                    if existing_image_name.find("contour") == -1:  # not a contour image
                        potentially_better_image: Image = Image.open(
                            existing_image_path
                        )
                        if better_resolution(potentially_better_image, colour_image):
                            if colour_image != None:
                                colour_image.close()
                            colour_image = potentially_better_image
                    elif (
                        existing_image_name.find("contour") != -1
                        and existing_image_name.find("overlay") != -1
                    ):
                        potentially_better_image: Image = Image.open(
                            existing_image_path
                        )
                        if better_resolution(potentially_better_image, contour_image):
                            if contour_image != None:
                                contour_image.close()
                            contour_image = potentially_better_image

            # tiling colour image if it exists
            if colour_image != None:
                colour_image_count += 1

                if arguments.verbose == True:
                    print(
                        f'Found adequate colour image in {file_name}, "{colour_image.filename}" of size {colour_image.width}x{colour_image.height}'
                    )

                tile_count += split_image_to_tiles(
                    colour_image, target_save_folder_colour, f"{file_name}_colour"
                )
            else:
                if arguments.verbose == True:
                    print(f"No adequate colour image found for {file_name}.")

            # tiling contour image if it exists
            if contour_image != None:
                contour_image_count += 1

                if arguments.verbose == True:
                    print(
                        f'Found adequate contour image in {file_name}, "{contour_image.filename}" of size {contour_image.width}x{contour_image.height}'
                    )

                tile_count += split_image_to_tiles(
                    contour_image, target_save_folder_contour, f"{file_name}_contour"
                )
            else:
                if arguments.verbose == True:
                    print(f"No adequate contour image found for {file_name}.")

    # output
    end_time = time.time()
    print(
        f"\nImages tiled: {colour_image_count + contour_image_count} ({colour_image_count} colour, {contour_image_count} contour)",
        f"Tiles generated: {tile_count}",
        f"Folders checked: {folder_count} folders",
        f"Running time: {str(end_time - start_time)}s",
        sep="\n",
        end="\n",
    )

# tarmac syncing
if arguments.upload == True:
    print(f"Syncing tiles to ROBLOX with tarmac.")
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.isfile(env_path):
        auth = parse_env_file(env_path, "ROBLOSECURITY")
        if auth != None:
            os.system(
                f'tarmac sync --target roblox --auth "{auth}" --retry 5 --retry-delay 5'
            )
            os.system("remodel run convert_to_rbxm.lua")
            print(f"All images synced with ROBLOX.")
        else:
            print(
                f"Cannot sync with ROBLOX. ROBLOSECURITY key not present in .env file."
            )
    else:
        print(f"Cannot sync with ROBLOX. No .env with a ROBLOSECURITY key.")
