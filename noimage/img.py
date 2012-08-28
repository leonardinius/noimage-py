'''
Created on Aug 27, 2012

@author: leonids.maslovs
'''

from PIL import Image, ImageDraw, ImageFont

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

if __name__ == '__main__':
    c = 500
    with open('output.png', 'wb') as f:
        draw((c, c), (171, 140, 197), 'white').save(f)
        
    with open('output2.png', 'wb') as f:
        draw((c, c), (171, 140, 197), 'white', 'asas\nrtrt').save(f)
