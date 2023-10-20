from PIL import Image # Ewww an import

WIDTH = 1280
HEIGHT = 800
BYTES_PER_PIXEL = 4
SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
LOCAL_BUFFER = SYS_VIDEO_BUFFER.read()
LOCAL_QUEUE = {}

def writePixel(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        position = (y * WIDTH + x) * BYTES_PER_PIXEL
        SYS_VIDEO_BUFFER.seek(position)
        SYS_VIDEO_BUFFER.write(Bytes)

def queueLocalChange(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT: # Doesn't write if negative or above screen size
        position = (y * WIDTH + x) * BYTES_PER_PIXEL
        LOCAL_QUEUE[position] = Bytes
        
def updateLocalBuffer() -> None:
    global LOCAL_BUFFER
    buffer_list = bytearray(LOCAL_BUFFER)
    for position in LOCAL_QUEUE:
        buffer_list[position:position+BYTES_PER_PIXEL] = LOCAL_QUEUE[position]
    LOCAL_BUFFER = bytes(buffer_list)

def syncBuffers() -> None:
    SYS_VIDEO_BUFFER.seek(0)
    SYS_VIDEO_BUFFER.write(LOCAL_BUFFER)

def convertRGBtoBGRA(r:int, g:int, b:int) -> bytes:
    r = r << (16)
    g = g << (8)
    return (r + g + b).to_bytes(4,'little')


im = Image.open("image.jpg")

width, height = im.size
px = im.load()
for y in range(height):
    for x in range(width):
        writePixel(x,y,convertRGBtoBGRA(*px[x,y]))
# updateLocalBuffer()
# syncBuffers()