# coding=utf-8
'''
Created on Aug 27, 2012

@author: leonids.maslovs
'''

from PIL import Image, ImageDraw, ImageFont
from flask.ext.bootstrap import Bootstrap
from jinja2.exceptions import TemplateNotFound
import flask
import io
import json
import os
import re
import logging 

def loadConfig(path=os.getcwd()):
    file_name = os.path.join(path, '.config.json')
    if not os.path.isfile(file_name):
        return None
    return json.load(open(file_name))


cfg = loadConfig()
app = flask.Flask(__name__)
Bootstrap(app)
app.config['BOOTSTRAP_USE_CDN'] = cfg.get('BOOTSTRAP_USE_CDN', True)
app.config['BOOTSTRAP_USE_MINIFIED'] = cfg.get('BOOTSTRAP_USE_MINIFIED', True)
app.config['BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT'] = cfg.get('BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT', None)

def draw(size, bgcolor=None, txtcolor=None, text=None):
    width, height = size
    
    if not text:
        text = '%sx%s' % size
    lines = text.splitlines()
    
    mask = Image.new('RGB', size, bgcolor)
    draw = ImageDraw.Draw(mask)
    font = ImageFont.truetype(cfg.get('NOIMAGEYET_TTF', 'Arial.ttf'), min(int(height / max(5, len(lines) + 1)), int(1.5 * width / (max(len(l) for l in lines)))))
    
    i = -0.5 if len(lines) == 1 else int(-1 * len(lines) / 2) 
    for text_line in lines:
        tw, th = font.getsize(text_line)
        draw.text((width / 2 - tw / 2, height / 2 + i * th), text_line, fill=txtcolor, font=font)
        i += 1
    return mask


@app.route('/<path:path>')
def serve_image(path):
    # special pre-defined sizes to use in lieu of number dimensions.  taken from dummyimage.com.
    #
    # the sizez table definition itself (code) was copied over from https://github.com/mgrdcm/ipsumimage/ project. 
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
        'verticalbanner':       '120x240',
        'squarebutton':         '125x125',
        'leaderboard':          '728x90',
        'wideskyscraper':       '60x600',
        'skyscraper':           '120x600',
        'halfpage':             '300x600',
        
        # Screen Resolutions
        'cga':      '320x200',
        'qvga':     '320x240',
        'vga':      '640x480',
        'wvga':     '800x480',
        'svga':     '800x480',
        'wsvga':    '1024x600',
        'xga':      '1024x768',
        'wxga':     '1280x800',
        'wsxga':    '1440x900',
        'wuxga':    '1920x1200',
        'wqxga':    '2560x1600',
        
        # Video Resolutions
        'ntsc':     '720x480',
        'pal':      '768x576',
        'hd720':    '1280x720',
        'hd1080':   '1920x1080',
    }
    
    mimetypes = {
                 'tiff' : 'image/tiff' 
    }
    
    spec = re.match(r'(?P<actual_size>[a-zA-Z0-9x]+)?(/(?P<bgcolor>[a-zA-Z0-9\#\,\%\\)\\(]+))?(/(?P<txtcolor>[a-zA-Z0-9\#\,\%\\)\\(]+))?(\.(?P<ext>gif|jpeg|png|bmp))?$', path)
    
    class MyBytesIOHack(io.BytesIO):
        '''
        https://bugs.launchpad.net/ubuntu/+source/python-imaging/+bug/718852
        '''
        def __init__(self, *args, **kwargs):
            io.BytesIO.__init__(self, *args, **kwargs)
        
        def fileno(self, *args, **kwargs):
            raise AttributeError('fileno')
    
    if spec:
        try:
            size_name = spec.group('actual_size')
            actual_size = sizes.get(size_name, size_name)
            text = '%s\n%s' % (size_name, actual_size) if size_name in sizes else actual_size
            text = flask.request.args['t'] if 't' in flask.request.args else text
            text = text.replace('|', '\n')
            image_size = tuple(int(x) for x in actual_size.split('x'))
            ext = spec.group('ext') or 'png'
            img = draw(image_size,
                       spec.group('bgcolor') or '#AB8CC5',
                       spec.group('txtcolor') or 'white',
                       text)
            with MyBytesIOHack() as f:
                img.save(f, ext)
                return flask.Response(f.getvalue(), mimetype=mimetypes.get(ext, 'image/' + ext))
        except BaseException:
            app.logger.exception('Error processing: %s. Request args: %r', path, flask.request.args)
            return flask.render_template('page404.html', page={}), 404
    else:
        return flask.render_template('page404.html', page={}), 404

@app.route('/', defaults={'page': 'index'})
@app.route('/<string:page>.html')
def view(page):
    try:
        return flask.render_template('%s.html' % page, page={'active_page' : page})
    except TemplateNotFound:
        return flask.render_template('page404.html', page={}), 404

if not app.debug:
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(cfg.get('LOG_FILE','~/logs/noimageyet/app.log'))
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
