import argparse
import datetime
import os
import requests
import shutil
from subprocess import Popen, PIPE
import webbrowser


def current_file():
    tmp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")
    today = datetime.datetime.today()
    current = "apod_{:04d}-{:02d}-{:02d}.jpg".format(today.year, today.month, today.day)
    try:
        if current in os.listdir(tmp_path):
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def purge(dir):  # only used to clean up old images
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


def main(start_display, web):
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    screen_num, stderr = p.communicate('''tell application "System Events" to return count of desktops''')
    if int(screen_num) >= start_display:
        response = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY").json()
        media_type = response["media_type"]
        hdurl = response["hdurl"]
        url = response["url"]
        apod_date = response["date"]
        tmp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp")
        apod_file = os.path.join(tmp_dir, "apod_{}.jpg".format(apod_date))

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        if web:
            webbrowser.open("https://apod.nasa.gov/apod/astropix.html")
        if media_type == "image":
            purge(tmp_dir)  # clean up old images
            r = requests.get(hdurl, stream=True)
            if r.status_code == 200:
                with open(apod_file, "wb") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

            for i in range(start_display, int(screen_num)+1, start_display+1):
                scpt = '''
                    tell application "System Events"
                        tell desktop {}
                            set picture rotation to 0
                            set picture to "{}"
                        end tell
                    end tell
                    '''.format(i, apod_file)

                p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
                stdout, stderr = p.communicate(scpt)

        elif media_type == "video":
            print("Today is a video, please visit https://apod.nasa.gov/apod/astropix.html for more information.")
        else:
            print("Error! Today APOD is something weird.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--display",
        "-d",
        help="specify the display from which on you want to set the apod image as wallpaper. Default: second display",
        default="2",
    )
    parser.add_argument(
        "--no-web",
        "-nw",
        help="don't open the webbrowser to show https://apod.nasa.gov/apod/astropix.html",
        default=True,
        dest='web',
        action='store_false'
    )

    args = parser.parse_args()

    if not current_file():
        main(int(args.display), args.web)
