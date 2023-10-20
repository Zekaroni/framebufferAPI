# r = 255 # FF
# g = 170 # AA
# b = 51  # 33 # NOTE: If bellow 127, it shows as the ascii char value

def convertRGBtoBGRA(r:int, g:int, b:int) -> bytes:
    r = r << (16)
    g = g << (8)
    return (r + g + b).to_bytes(4,'little')

# print(convertRGBtoBGRA(r,g,b))
from PIL import Image

im = Image.open("image.jpg")
data = bytearray()
width, height = im.size
data.extend(width.to_bytes(2,'little'))
data.extend(height.to_bytes(2,'little'))
px = im.load()
for y in range(height):
    for x in range(width):
        data.extend(convertRGBtoBGRA(*px[x,y]))

width = int.from_bytes(data[0:2], byteorder='little')
height = int.from_bytes(data[2:4], byteorder='little')
cursor = 4
for y in range(height):
    for x in range(width):
        print(data[cursor:cursor+4])
        cursor+=4
# print(data)