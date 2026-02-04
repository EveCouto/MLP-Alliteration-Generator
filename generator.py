from derpibooru import Search, sort
import argparse
import os
import time
import urllib.request
from PIL import Image


def get_images(tags: list):
    """
    Uses Derpibooru API to get images

    :param character: character used in search
    :type character: str
    """
    images = []
    for image in (Search()
                  # Guarantees the images are from the show
                  .query(*tags)
                  .sort_by(sort.RANDOM)):
        images.append(image.full)
    return images


def dir_path(string: str):
    """
    Checks if string is a dir path

    :param string: string
    :type string: str
    """
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)


def file_path(string: str):
    """
    Checks if string is a file path

    :param string: string
    :type string: str
    """
    if os.path.isfile(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)


class NotADayError(Exception):
    """
    NotADayError
    """


def day(string):
    """
    Checks if string is a day

    :param string: string
    :type string: str
    """
    days = ["monday", "mon", "tuesday", "tue",
            "wednesday", "wed", "thursday", "thu",
            "friday", "fri", "saturday", "sat",
            "sunday", "sun"]
    if string in days:
        return string
    else:
        raise NotADayError(string)


def start_parser():
    """
    Creates a argument processor
    """
    current_time = time.strftime(r"%Y%m%d-%H%M%S", time.localtime())
    parser = argparse.ArgumentParser(description=(
        "Allows for wacky MLP videos to be made"))
    parser.add_argument("-i", "--script",
                        help=".vtt script path",
                        default="./defaults/default-script.txt",
                        type=file_path)
    parser.add_argument("-o", "--output",
                        help="Output folder path",
                        default=".",
                        type=dir_path)
    parser.add_argument("-t", "--title",
                        help="Title of video",
                        default=f"MLP-Alliteration-{current_time}",
                        type=str)
    parser.add_argument("-c", "--char",
                        help="Character",
                        required=True,
                        type=str)
    parser.add_argument("-d", "--day",
                        help="Day of week",
                        required=True,
                        type=str)
    args = parser.parse_args()
    return args


def main():
    day_map = {"monday": 1, "mon": 1, "tuesday": 2, "tue": 2,
               "wednesday": 3, "wed": 3, "thursday": 4, "thu": 4,
               "friday": 5, "fri": 5, "saturday": 6, "sat": 6,
               "sunday": 7, "sun": 7}
    args = start_parser()
    script = args.script
    output = args.output
    title = args.title
    character = args.char
    day = day_map[args.day]

    print(script, output, title, character, day)

    images = get_images([character, "safe", "screencap", "-edit"])
    if len(images) < 30:
        print("Not enough images for this character, exiting")
    for url in images[:5]:
        save_path = os.path.join("./cache/", os.path.basename(url))
        urllib.request.urlretrieve(url, save_path)
        img = Image.open(save_path)
        img.show()
    # print(get_images(character))


if __name__ == "__main__":
    main()
