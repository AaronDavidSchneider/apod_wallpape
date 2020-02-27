import argparse
import datetime
import os
import requests
import shutil
from subprocess import Popen, PIPE
import webbrowser


def newest_file_time(path):
    try:
        files = os.listdir(path)
        paths = [os.path.join(path, basename) for basename in files]
        try:
            time = datetime.datetime.fromtimestamp(os.path.getctime(max(paths, key=os.path.getctime)))
        except ValueError:
            time = datetime.datetime.today() - datetime.timedelta(days=2)  # return some old time and update
    except FileNotFoundError:
        time = datetime.datetime.today() - datetime.timedelta(days=2)  # return some old time and update
    return time


def purge(dir):  # only used to clean up old images
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


def main(start_display, web):
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    screen_num, stderr = p.communicate('''tell application "System Events" to return count of desktops''')
    response = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY").json()
    media_type = response["media_type"]
    hdurl = response["hdurl"]
    url = response["url"]
    apod_date = response["date"]
    cwd = os.getcwd()

    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    if web:
        webbrowser.open("https://apod.nasa.gov/apod/astropix.html")
    if media_type == "image":
        purge("{}/tmp/".format(cwd))  # clean up old images
        r = requests.get(hdurl, stream=True)
        if r.status_code == 200:
            with open("tmp/apod_{}.jpg".format(apod_date), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

        for i in range(start_display, int(screen_num) + 1):
            scpt = '''
                tell application "System Events"
                    tell desktop {}
                        set picture rotation to 0
                        set picture to "{}/tmp/apod_{}.jpg"
                    end tell
                end tell
                '''.format(i, cwd, apod_date)

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

    if newest_file_time("/Users/schneider/codes/apod/tmp").date() < datetime.datetime.today().date():
        main(int(args.display), args.web)
