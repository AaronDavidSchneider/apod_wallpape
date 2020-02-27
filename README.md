# APOD Wallpaper on OSX
Fetch current astronomical picture of the day (https://apod.nasa.gov/apod/astropix.html) and set it as wallpaper.

## usage
run the script by calling
```sh
python apod_daily.py [options]
``` 
The script will create a folder called `tmp` inside the directory where the script is saved, download the current astronomical picture of the day into this directory and set it as wallpaper.

The script finishes early if the current apod has already been set as wallpaper.

## options:
- `-d --display`: specify the display from which on you want to set the apod image as wallpaper. Default: second display
- `--no-web`: don't open the webbrowser to show https://apod.nasa.gov/apod/astropix.html

## requirements:
- OSX
- requests

## examples:
add to `~/.bash_profile`:
```sh
python [path to your script]/apod_daily.py [options]
```
Every time you open your terminal the new background picture is set.
