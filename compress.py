WIDTH = 1280
HEIGHT = 800
BYTES_PER_PIXEL = 4
SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
LOCAL_BUFFER = SYS_VIDEO_BUFFER.read()
LOCAL_QUEUE = {}
COLOURS = {
    "WHITE":  b'\xFF\xFF\xFF\x00',
    "BLACK":  b'\x00\x00\x00\x00',
}

def queueLocalChange(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
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

def initTerminal() -> None:
    print("\x1b[2J\x1b[H",end="")
    print("\n"*(HEIGHT//14))

def drawSquare(size: int, start_x: int, start_y: int, colour: bytes) -> None:
    for j in range(start_y, start_y + size):
        for i in range(start_x, start_x + size):
            queueLocalChange(i, j, colour)

x_value = 0
y_value = 0
shift = 0
tile_size = 50
for row in range(8):
    for column in range(8):
        drawSquare(tile_size,x_value,y_value,COLOURS["WHITE"] if (column+(shift%2))%2==0 else COLOURS["BLACK"])
        x_value += tile_size
    x_value=0
    y_value+=tile_size
    shift+=1
initTerminal()
updateLocalBuffer()
syncBuffers()