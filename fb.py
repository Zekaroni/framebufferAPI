WIDTH = 1280
HEIGHT = 800
BYTES_PER_PIXEL = 4
SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
LOCAL_BUFFER = SYS_VIDEO_BUFFER.read()
LOCAL_QUEUE = []

def writePixel(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        position = (y * WIDTH + x) * BYTES_PER_PIXEL
        SYS_VIDEO_BUFFER.seek(position)
        SYS_VIDEO_BUFFER.write(Bytes)

def writeBuffer(Bytes: bytes, position: int = 0) -> None:
    SYS_VIDEO_BUFFER.seek(position)
    SYS_VIDEO_BUFFER.write(Bytes)

def queueLocalChange(x: int, y: int, Bytes: bytes):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        position = (y * WIDTH + x) * BYTES_PER_PIXEL
        LOCAL_QUEUE.append([position,Bytes])
        
def updateLocalBuffer() -> None:
    global LOCAL_BUFFER
    buffer_list = bytearray(LOCAL_BUFFER)
    for position, Bytes in LOCAL_QUEUE:
        buffer_list[position:position+BYTES_PER_PIXEL] = Bytes
    LOCAL_BUFFER = bytes(buffer_list)

def syncBuffers() -> None:
    SYS_VIDEO_BUFFER.seek(0)
    SYS_VIDEO_BUFFER.write(LOCAL_BUFFER)

def initTerminal() -> None:
    print("\x1b[2J\x1b[H",end="")
    print("\n"*(HEIGHT//14))

def drawSquare(size: int, start_x: int, start_y: int, Byte: bytes):
    for j in range(start_y, start_y + size):
        for i in range(start_x, start_x + size):
            queueLocalChange(i, j, Byte)


initTerminal()
drawSquare(HEIGHT,0,0,b'\x00\xff\xff\x00')
updateLocalBuffer()
syncBuffers()
