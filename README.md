# MLP-Video-Generator

Takes in a script file and will generate a short MLP video based off of it.

The script file is organised similarly to a .vtt file but has additional tag data.

When running the script the only flag needed is -o denoting the output folder.

Run with -h to see all the options.

## Script File

The script file is organised as such:

```text
start time --> ends time
caption text
tags

```

- The start and end times can be in 00:00:00.000 format or 00:00.000 or 00.000 formats.

- Caption text works with basically any text, but some erros with special characters.

- Tags is a list of tags in derpibooru, if there is an invalid it falls back to a default image.

- Ensure there is a newline at the end of every section.

Here is an example of a script file section:

```text
00:00:00.000 --> 5.00
Some sample text!
Flutterhy, Twilight Sparkle, pony, safe

```

There is also a full example in /defaults/default-script.txt showing a full script.

## Installation

There are 3 items needed to run this script:

1. The vid_generator.py python script
2. defaults folder and its contents
3. requirements.txt

Place all 3 items in the same directory, ensure python is installed.

Use `pip install -r requirements.txt` to install the packages needed.

Use `python ./vid_generator.py -h` to run the script.
