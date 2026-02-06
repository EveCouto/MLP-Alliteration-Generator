from derpibooru import Search, sort
import argparse
import os
import time
import urllib.request
import moviepy as mpy
import shutil


def get_images(tags: list):
    """
    Uses Derpibooru API to get image data

    :param character: character used in search
    :type character: str
    """
    images = []
    for image in (Search()
                  # Guarantees the images follow tags
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


def image_to_videoclip(path: str, start: float, end: float):
    """
    Takes an image file, start time and duration, makes clip

    :param path: image file path
    :type path: str
    :param start: start time in seconds
    :type start: float
    :param end: end time in seconds
    :type end: float
    """
    # Adds multiple loops for videos/gifs to prevent stopping
    if os.path.splitext(path)[1] in [".gif", ".webm"]:
        clip = mpy.VideoFileClip(path)
        if clip.duration <= end-start:
            clip = mpy.concatenate_videoclips(
                [clip] * int((end-start) / clip.duration + 2))
    else:
        clip = mpy.ImageClip(path)

    # Adds data to clips and returns it
    clip = (clip.with_start(start)
            .with_end(end)
            .with_position("center")
            .resized(height=720))
    return clip


def paths_to_clip(paths: list[str], starts: list[float],
                  ends: list[float], text: list[str], audio: str):
    """
    Takes data and makes a clip

    :param paths: list of img paths
    :type paths: list[str]
    :param starts: list of start times
    :type starts: list[float]
    :param ends: lsit of end times
    :type ends: list[float]
    :param text: display text
    :type text: list[str]
    :param audio: audio path
    :type audio: str
    """
    clips = []
    # Adds text and image to clips with corresponding time data
    for i in range(min(len(starts), len(ends), len(paths))):
        clips.append(image_to_videoclip(paths[i], starts[i], ends[i]))
        clips.append(mpy.TextClip("./defaults/default-font.ttf", text[i],
                                  font_size=70, color=(255, 255, 255),
                                  size=(1000, 500), stroke_color=(0, 0, 0),
                                  stroke_width=5, method="caption",
                                  text_align="center")
                     .with_start(starts[i])
                     .with_end(ends[i]).with_position(("center", "bottom")))

    # Creates audio clip
    total_length = ends[-1]
    audio_clip = mpy.AudioFileClip(audio)
    if audio_clip.duration <= total_length:
        audio_clip = mpy.concatenate_audioclips(
            [audio_clip] * int(total_length / audio_clip.duration + 2))

    # Merges clips and adds audio to video
    video = mpy.CompositeVideoClip(clips, bg_color=(0, 0, 0), size=(1280, 720))
    video.audio = audio_clip.with_duration(total_length)
    return video


def time_parser(time_string: str):
    """
    Takes a 00:00:00.000 time and converts to seconds

    :param time_string: Description
    :type time_string: str
    """
    time_strings = time_string.split("-->")
    time_list = []
    for t in time_strings:
        split_times = t.split(":")
        seconds = 0
        sections = t.count(":")
        for x in range(sections+1):
            seconds += 60**(sections-x) * float(split_times[x].strip())
        time_list.append(seconds)
    return time_list


def script_file_parser(script: str):
    """
    Takes in custom data file and converts to data

    :param script: fancy .txt file
    :type script: str
    """
    lines = script.splitlines()
    all_data = []
    single_data = {}
    for i in range(len(lines)):
        # Each section starts with time data
        if "-->" in lines[i]:
            single_data.clear()
            frame_time = time_parser(lines[i])
            # No way to tell if file ends or no tags
            if i+1 >= len(lines) or lines[i+1] == "":
                text = ""
                tags = []
            elif i+2 >= len(lines) or lines[i+2] == "":
                text = lines[i+1]
                tags = []
            elif i+3 >= len(lines) or lines[i+3] == "":
                text = lines[i+1]
                tags = lines[i+2].split(",")
            else:
                exit
            all_data.append({"time": frame_time, "text": text, "tags": tags})

    return all_data


def data_to_video(data: list[dict], output: str, title: str, audio: str):
    """
    Takes some info and makes a video from it

    :param data: List of dicts with times, tags and text
    :type data: list[dict]
    :param output: output file
    :param title: output title
    :param audio: audio file
    """
    images = []
    starts = []
    ends = []
    text = []
    all_tags = []

    for frame in data:
        # Downloads images
        imgs = get_images(frame["tags"])
        if len(imgs) != 0:
            img = imgs[0]
            url = img[0]
            all_tags.append(img[1])
            save_path = os.path.join("./cache/", os.path.basename(url))
            urllib.request.urlretrieve(url, save_path)
        else:
            save_path = "./defaults/default-image.jpg"

        # Adds data to lists
        images.append(save_path)
        starts.append(frame["time"][0])
        ends.append(frame["time"][1])
        text.append(frame["text"])

    # Creates video and saves it
    video = paths_to_clip(images, starts, ends, text, audio)
    video.write_videofile(os.path.join(output, title+".mp4"), fps=24)

    # Returns all tags for artist recognition
    return all_tags


def start_parser():
    """
    Creates a argument processor
    """
    current_time = time.strftime(r"%Y%m%d-%H%M%S", time.localtime())
    parser = argparse.ArgumentParser(description=(
        "Allows for wacky MLP videos to be made"))
    parser.add_argument("-i", "--script",
                        help="Script path",
                        default="./defaults/default-script.txt",
                        type=file_path)
    parser.add_argument("-a", "--audio",
                        help="Audio path",
                        default="./defaults/default-song.mp3",
                        type=str)
    parser.add_argument("-o", "--output",
                        help="Output folder path",
                        default=".",
                        type=dir_path)
    parser.add_argument("-t", "--title",
                        help="Title of video",
                        default=f"MLP-Video-{current_time}",
                        type=str)
    args = parser.parse_args()
    return args


def empty_folder(path: str):
    """
    Takes a folder path and clears its contents

    :param path: fodler path
    :type path: str
    """
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Failed to delete {item_path}. Reason: {e}")


def main():
    args = start_parser()
    script = args.script
    output = args.output
    title = args.title
    audio = args.audio

    # Creates and empties cache folder
    if not os.path.exists("./cache"):
        os.makedirs("./cache")
    empty_folder("./cache/")

    # Loads script file and creates video from it
    with open(script, "r") as file:
        frame_data = script_file_parser(file.read())
        all_tags = data_to_video(frame_data, output, title, audio)

    # Prints out the artists from the images if listed
    artists = []
    for tags in all_tags:
        artists.extend(t[7:] for t in tags if t.startswith("artist:"))
    print("\nArtists included in thie video:\n" + "\n".join(artists) + "\n")


if __name__ == "__main__":
    main()
