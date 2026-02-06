from derpibooru import Search, sort
import argparse
import os
import time
import urllib.request
import moviepy as mpy


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
    if os.path.splitext(path)[1] in [".gif", ".webm"]:
        clip = mpy.VideoFileClip(path)
        if clip.duration <= duration:
            clip = mpy.concatenate_videoclips(
                [clip] * int(duration / clip.duration + 2))
    else:
        clip = mpy.ImageClip(path)

    clip = (clip.with_start(start)
            .with_duration(duration)
            .with_position("center")
            .resized(height=720))
    return clip


def paths_to_clip(paths: list[str], starts: list[float],
                  durations: list[float], text: list[str], audio: str):
    clips = []

    for i in range(min(len(starts), len(durations), len(paths))):
        clips.append(image_to_videoclip(paths[i], starts[i], durations[i]))
        clips.append(mpy.TextClip("./defaults/Lexend-Bold.ttf", text[i],
                                  font_size=70, color=(255, 255, 255),
                                  size=(1000, 500), stroke_color=(0, 0, 0),
                                  stroke_width=5).with_start(starts[i])
                     .with_duration(durations[i]).with_position("center"))

    total_length = starts[-1] + durations[-1]
    audio_clip = mpy.AudioFileClip(audio)
    if audio_clip.duration <= total_length:
        audio_clip = mpy.concatenate_audioclips(
            [audio_clip] * int(total_length / audio_clip.duration + 2))

    video = mpy.CompositeVideoClip(clips, bg_color=(0, 0, 0), size=(1280, 720))
    video.audio = audio_clip.with_duration(total_length)
    return video


def time_parser(time_string: str):
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
    lines = script.splitlines()
    all_data = []
    single_data = {}
    for i in range(len(lines)):
        if "-->" in lines[i]:
            single_data.clear()
            frame_time = time_parser(lines[i])
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


def data_to_video(data: list[dict], output, title, audio):
    images = []
    starts = []
    durations = []
    text = []
    all_tags = []

    for frame in data:
        img = get_images(frame["tags"])[0]
        url = img[0]
        all_tags.append(img[1])
        save_path = os.path.join("./cache/", os.path.basename(url))
        urllib.request.urlretrieve(url, save_path)
        images.append(save_path)
        starts.append(frame["time"][0])
        durations.append(frame["time"][1]-frame["time"][0])
        text.append(frame["text"])

    video = paths_to_clip(images, starts, durations, text, audio)
    video.write_videofile(os.path.join(output, title+".mp4"), fps=24)

    return all_tags


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
    parser.add_argument("-a", "--audio",
                        help="Audio for the video",
                        default="./defaults/default-song.mp3",
                        type=str)
    parser.add_argument("-o", "--output",
                        help="Output folder path",
                        default=".",
                        type=dir_path)
    parser.add_argument("-t", "--title",
                        help="Title of video",
                        default=f"MLP-Alliteration-{current_time}",
                        type=str)
    args = parser.parse_args()
    return args


def main():
    args = start_parser()
    script = args.script
    output = args.output
    title = args.title
    audio = args.audio

    with open(script, "r") as file:
        frame_data = script_file_parser(file.read())
        all_tags = data_to_video(frame_data, output, title, audio)

    artists = []
    for tags in all_tags:
        artists.extend(t[7:] for t in tags if t.startswith("artist:"))
    print("Artists included in thie video:\n", "\n".join(artists))


if __name__ == "__main__":
    main()
