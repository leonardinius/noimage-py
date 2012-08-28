# coding=utf-8
'''
Created on Aug 27, 2012

@author: leonids.maslovs
'''

from PIL import Image, ImageDraw, ImageFont
from flask import Flask
import flask
import io
import re

def draw(size, bgcolor=None, txtcolor=None, text=None):
    width, height = size
    
    mask = Image.new('RGB', size, bgcolor)
    draw = ImageDraw.Draw(mask)
    font = ImageFont.truetype("arial.ttf", int(height / 5))
    
    if not text:
        text = "%sx%s" % size
    lines = text.splitlines()
    
    i = 1 if len(lines) == 1 else 0 
    for text_line in lines:
        tw, th = font.getsize(text_line)
        draw.text((width / 2 - tw / 2, height / 2 - i * th / 4), text_line, fill=txtcolor, font=font)
        i += 2
    return mask

app = Flask(__name__)

@app.route("/<path:path>")
def serve_image(path):
    # special pre-defined sizes to use in lieu of number dimensions.  taken from dummyimage.com.
    sizes = {
        # Ad Sizes
        'mediumrectangle':      '300x250',
        'squarepopup':          '250x250',
        'verticalrectangle':    '240x400',
        'largerectangle':       '336x280',
        'rectangle':            '180x150',
        'popunder':             '720x300',
        'fullbanner':           '468x60',
        'halfbanner':           '234x60',
        'microbar':             '88x31',
        'button1':              '120x90',
        'button2':              '120x60',
        'verticalbanner':        '120x240',
        'squarebutton':         '125x125',
        'leaderboard':          '728x90',
        'wideskyscraper':        '60x600',
        'skyscraper':           '120x600',
        'halfpage':             '300x600',
        
        # Screen Resolutions
        'cga':      '320x200',
        'qvga':        '320x240',
        'vga':        '640x480',
        'wvga':        '800x480',
        'svga':        '800x480',
        'wsvga':    '1024x600',
        'xga':       '1024x768',
        'wxga':        '1280x800',
        'wsxga':     '1440x900',
        'wuxga':     '1920x1200',
        'wqxga':    '2560x1600',
        
        # Video Resolutions
        'ntsc':     '720x480',
        'pal':      '768x576',
        'hd720':    '1280x720',
        'hd1080':    '1920x1080',
    }
    
    mimetypes = {
                 'tiff' : 'image/tiff' 
    }
    
    spec = re.match(r"(?P<actual_size>[a-zA-Z0-9x]+)?(/(?P<bgcolor>[a-zA-Z0-9x]+))?(/(?P<txtcolor>[a-zA-Z0-9x]+))?(\.(?P<ext>gif|jpeg|png|bmp))?$", path)
    
    class MyBytesIOHack(io.BytesIO):
        """
        https://bugs.launchpad.net/ubuntu/+source/python-imaging/+bug/718852
        """
        def __init__(self, *args, **kwargs):
            io.BytesIO.__init__(self, *args, **kwargs)
        
        def fileno(self, *args, **kwargs):
            raise AttributeError('fileno')
    
    if spec:
        size_name = spec.group('actual_size')
        actual_size = sizes.get(size_name, size_name)
        image_size = tuple(int(x) for x in actual_size.split('x'))
        ext = spec.group('ext') or 'png'
        img = draw(image_size, 
                   spec.group('bgcolor') or '#AB8CC5', 
                   spec.group('txtcolor') or 'white', 
                   actual_size)
        with MyBytesIOHack() as f:
            img.save(f, ext)
            return flask.Response(f.getvalue(), mimetype=mimetypes.get(ext, 'image/' + ext))

    else:
        return flask.render_template('page404.html'), 404

@app.route("/")
@app.route("/index.html")
def index():
    return flask.render_template("index.html")    

if __name__ == '__main__':
    app.run(debug=True)
