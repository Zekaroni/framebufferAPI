from PIL import Image

def convertRGBtoBGRA(r:int, g:int, b:int) -> bytes:
    r = r << (16)
    g = g << (8)
    return (r + g + b).to_bytes(4,'little')


im = Image.open("image.jpg")

outputFile = open("image.zeke", "wb")

width, height = im.size
b_width = width.to_bytes(2,'little')
b_height = height.to_bytes(2,'little')
outputFile.write(b_width)
outputFile.write(b_height)
px = im.load()
for y in range(height):
    for x in range(width):
        outputFile.write(convertRGBtoBGRA(*px[x,y]))
