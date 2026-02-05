from derpibooru import Search, sort
import argparse
import os
import time
import urllib.request
from PIL import Image
from moviepy import VideoClip, ImageClip, CompositeVideoClip, VideoFileClip


def get_images(tags: list):
    """
    Uses Derpibooru API to get image data

    :param character: character used in search
    :type character: str
    """
    images = []
    for image in (Search()
                  # Guarantees the images are from the show
                  .query(*tags)
                  .sort_by(sort.RANDOM)):
        images.append((image.full, image.tags))
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


def stitch_clips(clips: list[VideoClip]):
    """
    Takes in a list of image clips and stiches them together.
    
    :param clips: A list of image clips being stitched
    :type clips: list[VideoFileClip]
    """
    stitched_video = CompositeVideoClip(clips)
    return stitched_video


def image_to_videoclip(path: str, start: float, duration: float):
    """
    Takes an image file, start time and duration, makes clip
    
    :param path: image file path
    :type path: str
    :param start: start time in seconds
    :type start: float
    :param duration: duration in seconds
    :type duration: float
    """
    if os.path.splitext(path)[1] == ".gif":
        clip = VideoFileClip(path)
    else:
        clip = ImageClip(path)
    clip = clip.with_start(start).with_duration(duration)
    return clip


def paths_to_clip(paths: list[str], starts: list[float], durations: list[float]):
    clips = []
    for i in range(len(paths)):
        clips.append(image_to_videoclip(paths[i], starts[i], durations[i]))
    
    video = CompositeVideoClip(clips, bg_color=(0,0,0), size=(1280,720))
    return video


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

    # images = get_images([character, "safe", "screencap", "-edit"])
    # if len(images) < 30:
    #     print("Not enough images for this character, exiting")
    # for img in images[:5]:
    #     url = img[0]
    #     save_path = os.path.join("./cache/", os.path.basename(url))
    #     urllib.request.urlretrieve(url, save_path)
        # img = Image.open(save_path)
        # img.show()
    # print(get_images(character))
    paths = os.listdir("./cache/")
    paths = ["./cache/" + item for item in paths]
    # print(paths)
    starts = [0,5,10,11,15]
    durations = [5,5,1,4,5]
    video = paths_to_clip(paths, starts, durations)
    video.preview(fps=10)


if __name__ == "__main__":
    main()
