import re
import sys
import urllib.request

import config
import main
from PIL import Image


# credit: http://www.techniqal.com/blog/2011/01/18/python-3-file-read-write-with-urllib/
# in - string - direct url of the image to download
# out - Image - image
# downloads the specified image to path
def download_image(url):
    uaurl = urllib.request.Request(url, headers={'User-Agent': 'wallpaper-reddit python script by /u/MarcusTheGreat7'})
    f = urllib.request.urlopen(uaurl)
    print("downloading " + url)
    try:
        img = Image.open(f)
        if config.resize:
            main.log("resizing the downloaded wallpaper")
            img.thumbnail((config.minwidth, config.minheight))
        if config.opsys == "Windows":
            img.save(config.walldir + '\\wallpaper.bmp', "BMP")
        else:
            img.save(config.walldir + '/wallpaper.jpg', "JPEG")
    except IOError:
        print("Error saving image!")
        sys.exit(1)


# in - string, string - path of the image to set title on, title for image
# def set_image_title(path, title):
#     log("setting title")
#     #TODO: Set title with Pillow
#     newtitle = remove_tags(title)
#     if titlefont == "":
#         subprocess.call([spawn.find_executable("convert"), path, "-pointsize", str(titlesize), "-gravity",titlegravity,
#                          "-fill", "# 00000080", "-annotate", "+7+7", newtitle,
#                          "-fill", "white", "-annotate", "+5+5", newtitle, path])
#     else:
#         subprocess.call(
#             [spawn.find_executable("convert"), path, "-pointsize", str(titlesize), "-gravity", titlegravity, "-font",
#              titlefont,
#              "-fill", "# 00000080", "-annotate", "+7+7", newtitle,
#              "-fill", "white", "-annotate", "+5+5", newtitle, path])


# in - string, string, - a url and a title
# saves the url of the image to ~/.wallpaper/url.txt and the title of the image to ~/.wallpaper/title.txt, just
# for reference
def save_info(url, title):
    # Reddit escapes the unicode in json, so when the json is downloaded, the info has to be manually re-encoded
    # and have the unicode characters reprocessed
    title = title.encode('utf-8').decode('unicode-escape')
    with open(config.walldir + '/url.txt', 'w') as urlinfo:
        urlinfo.write(url)
    with open(config.walldir + '/title.txt', 'w') as titleinfo:
        titleinfo.write(re.sub(' +', ' ', re.sub("[\[\(\<].*?[\]\)\>]", "", title)).strip())
